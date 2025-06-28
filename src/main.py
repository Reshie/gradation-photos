import io
import base64
import os
from typing import List

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from PIL import Image

# FastAPIアプリケーションの初期化
app = FastAPI()

# このスクリプトがあるディレクトリを基準に、HTMLファイルのパスを決定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE_PATH = os.path.join(BASE_DIR, "index.html")

@app.get("/")
async def get_root():
    """
    ルートURLにアクセスがあった場合に、index.htmlを返します。
    これにより、ユーザーはWebページを閲覧できます。
    """
    if os.path.exists(HTML_FILE_PATH):
        return FileResponse(HTML_FILE_PATH)
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

    images = []
    try:
        for file in files:
            # アップロードされたファイルをメモリ上で読み込む
            contents = await file.read()
            # Pillowを使って画像を開く
            image = Image.open(io.BytesIO(contents))

            # PNGなどの透過画像(RGBA)をRGBに変換して、結合エラーを防ぐ
            if image.mode == 'RGBA':
                image = image.convert('RGB')
                
            images.append(image)
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": f"無効な画像ファイルが含まれています: {e}"}
        )

    # --- 画像を水平に結合する処理 ---
    # 各画像のサイズを取得
    widths, heights = zip(*(i.size for i in images))

    # 結合後の画像の全体の幅と最大の高さを計算
    total_width = sum(widths)
    max_height = max(heights)

    # 結合後の新しい画像を生成 (背景は白)
    combined_image = Image.new('RGB', (total_width, max_height), (255, 255, 255))

    # 順番に画像を貼り付け
    x_offset = 0
    for img in images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.width
    # --- ここまでが結合処理 ---

    # 結合した画像をメモリ上のバッファにPNG形式で保存
    buffered = io.BytesIO()
    combined_image.save(buffered, format="PNG")
    
    # Base64エンコードして、HTMLで表示できるデータURL形式に変換
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    data_url = f"data:image/png;base64,{img_str}"

    return {"status": "success", "image_data": data_url}

# このスクリプトが直接実行された場合にUvicornサーバーを起動
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)