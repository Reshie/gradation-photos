# Photo Gradation

## プロジェクト構成

- **フロントエンド**: React + Vite (Node.js 20.x, ポート5173)
- **バックエンド**: Python 3.12 + FastAPI + uv (ポート8000)
- **開発環境**: DevContainer (Docker)

## 開発環境のセットアップ

### 前提条件

- Docker Desktop
- Visual Studio Code
- Dev Containers 拡張機能

### 使用方法

1. VSCodeでプロジェクトルートディレクトリを開く
2. コマンドパレット(F1)を開く
3. 「Dev Containers: Reopen in Container」を選択

### アクセス方法

- **フロントエンド**: http://localhost:5173
- **バックエンド**: http://localhost:8000
- **FastAPI Docs**: http://localhost:8000/docs

### 必要なファイル

#### フロントエンド

- `package.json` - npm依存関係
- `vite.config.js` - Vite設定

#### バックエンド

- `pyproject.toml` - Python依存関係
- `uv.lock` - 依存関係ロックファイル
- `main.py` - FastAPIアプリケーション
