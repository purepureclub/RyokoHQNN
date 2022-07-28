from celery.result import AsyncResult
from fastapi import Body, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from worker import create_task

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home(request: Request):
    return JSONResponse({"status": "ok"})

@app.post("/tasks", status_code=201)
def run_task(request = Body(...)):
    task = create_task.delay(request)
    return JSONResponse({"task_id": task.id})

@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return JSONResponse(result)
