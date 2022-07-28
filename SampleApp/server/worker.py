import os
from io import BytesIO
import base64
from PIL import Image, ImageOps
import torch
from torch import cat, no_grad
from torchvision import transforms
from torch.nn import (
    Module,
    Conv2d,
    Linear,
    Dropout2d,
)
import torch.nn.functional as F
from qiskit import IBMQ
from qiskit.utils import QuantumInstance
from qiskit.circuit.library import RealAmplitudes, ZZFeatureMap
from qiskit_machine_learning.neural_networks import TwoLayerQNN
from qiskit_machine_learning.connectors import TorchConnector
from qiskit.providers.ibmq import least_busy
from celery import Celery

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
ibmq_apikey = os.environ.get("IBMQ_APIKEY", "PASTE_YOUR_APIKEY_HERE")
used_backend = ""
img_path = "/tmp/"

@celery.task(bind=True, name="create_task")
def create_task(self, request) -> int:
    id = self.request.id
    backend = request['backend'] # "real" or "simulator"

    # 手書き文字の画像を取得して一時保存
    starter = request['img'].find(',')
    image_data = request['img'][starter+1:]
    image_data = bytes(image_data, encoding='ascii')
    image_data = Image.open(BytesIO(base64.b64decode(image_data))).convert('RGB')
    image_data.save(img_path + id + '.png')
    
    # 識別処理
    qnn = create_qnn(backend)
    model = Net(qnn)
    model.load_state_dict(torch.load("model.pt"))
    model.eval()
    with no_grad():
        image = Image.open(img_path + id + '.png')
        image_resized = ImageOps.invert(image.convert('L')).resize((28,28))
        # Normalization https://discuss.pytorch.org/t/normalization-in-the-mnist-example/457
        transform=transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
        image_unsqueezed = transform(image_resized).unsqueeze(0)
        output = model(image_unsqueezed)
        if len(output.shape) == 1:
            output = output.reshape(1, *output.shape)
        pred = output.argmax(dim=1, keepdim=True)
        os.remove(img_path + id + ".png")
        return {"result": pred.item(), "backend": used_backend}

def create_qnn(backend):
    IBMQ.save_account(ibmq_apikey)
    provider = IBMQ.load_account()
    global used_backend
    qi = QuantumInstance(provider.get_backend('simulator_statevector'))
    used_backend = 'simulator_statevector'
    if backend == "real":
        # 5qubit以上の実機の中で最も空いているものを選択
        backend_lb = backend_lb = least_busy(provider.backends(simulator=False, operational=True, filters=lambda q: q.configuration().n_qubits >= 5))
        used_backend = str(backend_lb)
        qi = QuantumInstance(provider.get_backend(str(backend_lb)))
    feature_map = ZZFeatureMap(2)
    ansatz = RealAmplitudes(2, reps=1)
    # REMEMBER TO SET input_gradients=True FOR ENABLING HYBRID GRADIENT BACKPROP
    qnn = TwoLayerQNN(
        2,
        feature_map,
        ansatz,
        input_gradients=True,
        quantum_instance=qi,
    )
    return qnn

class Net(Module):
    def __init__(self, qnn):
        super().__init__()
        self.conv1 = Conv2d(1, 2, kernel_size=5)
        self.conv2 = Conv2d(2, 16, kernel_size=5)
        self.dropout = Dropout2d()
        self.fc1 = Linear(256, 64)
        self.fc2 = Linear(64, 2)  # 2-dimensional input to QNN
        self.qnn = TorchConnector(qnn)  # Apply torch connector, weights chosen
        # uniformly at random from interval [-1,1].
        self.fc3 = Linear(1, 1)  # 1-dimensional output from QNN

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        x = self.dropout(x)
        x = x.view(x.shape[0], -1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        x = self.qnn(x)  # apply QNN
        x = self.fc3(x)
        return cat((x, 1 - x), -1)
