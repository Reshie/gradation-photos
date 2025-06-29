import os
from typing import List

import uvicorn
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from utils.process import combine_images

# FastAPIアプリケーションの初期化
app = FastAPI()

# このスクリプトがあるディレクトリを基準に、HTMLファイルのパスを決定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE_PATH = os.path.join(BASE_DIR, "templates/index.html")

# 静的ファイルの設定
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    """
    ルートURLにアクセスがあった場合に、index.htmlを返します。
    これにより、ユーザーはWebページを閲覧できます。
    """
    if os.path.exists(HTML_FILE_PATH):
        templates = Jinja2Templates(directory="./templates")
        return templates.TemplateResponse("index.html", {"request": request})
    return JSONResponse(status_code=404, content={"error": "index.html not found"})

@app.post("/process-images/")
async def process_images(files: List[UploadFile] = File(...)):
    """
    複数の画像ファイルを受け取り、それらを水平に結合して
    単一の画像として返すAPIエンドポイント。
    """
    if len(files) < 2:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "最低2つの画像をアップロードしてください。"}
        )

    data_url = await combine_images(files)

    return {"status": "success", "image_data": data_url}

# このスクリプトが直接実行された場合にUvicornサーバーを起動
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)