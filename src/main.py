import os
from typing import List

import uvicorn
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from utils.process import calc_grid_size, combine_images

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
async def process_images(files: List[UploadFile] = File(...), num_cols: int = 0, num_rows: int = 10):
    """
    複数の画像ファイルを受け取り、それらを水平に結合して
    単一の画像として返すAPIエンドポイント。
    """
    if len(files) < 2:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "最低2つの画像をアップロードしてください。"}
        )

    # グリッドサイズを一応計算
    if num_cols == 0 and num_rows == 0:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "サイズを指定してください。"}
        )
    if num_cols == 0:
        num_cols = calc_grid_size(len(files), num_rows=num_rows)[0]
    if num_rows == 0:
        num_rows = calc_grid_size(len(files), num_cols=num_cols)[1]

    data_url = await combine_images(files, num_cols, num_rows)

    return {"status": "success", "image_data": data_url}

@app.post("/get-rows/")
async def get_rows(num_images:int, num_cols: int = 1):
    try:
        num_rows = calc_grid_size(num_images=num_images,num_cols=num_cols)[1]
    except Exception as e:
        print(e)

    return num_rows

@app.post("/get-cols/")
async def get_cols(num_images:int, num_rows: int = 1):

    num_cols = calc_grid_size(num_images=num_images,num_rows=num_rows)[0]

    return num_cols

# このスクリプトが直接実行された場合にUvicornサーバーを起動
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)