# 量子コンピューターで画像を識別してみよう - サンプルアプリ

## ローカルでの実行方法

### 前提

- [Docker Desktop](https://docs.docker.com/desktop/) または [Rancher Desktop](https://docs.rancherdesktop.io/getting-started/installation) (moby)
- Node.js 16 または 18


### バックエンドの準備（初回のみ）

[IBM Quantum](https://quantum-computing.ibm.com/) のダッシュボードで API token を取得し、`server/worker.py` 26行目に記入します。

### フロントエンドの準備（初回のみ）

以下のコマンドを実行します。

```sh
cd ./client
npm install
cp .env.example .env
cd ..
```

### バックエンドの起動

以下のコマンドを実行します。

```sh
cd ./server
docker-compose up -d --build
cd ..
```

### フロントエンドの起動

以下のコマンドを実行します。

```sh
cd ./client
npm run start
```

http://localhost:3000 へアクセスします。


*Enjoy!*