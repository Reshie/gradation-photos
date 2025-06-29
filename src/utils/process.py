import base64
import io
import os
import math
import statistics
from collections import Counter
from typing import Tuple, Optional, List, Dict, Any
import numpy as np
from matplotlib.colors import rgb_to_hsv
from fastapi import File, HTTPException, UploadFile
from PIL import Image

def get_dominant_color(image: Image.Image) -> Tuple[Optional[Image.Image], Optional[Tuple[int, int, int]]]:
    """
    画像から最頻色（最頻値）を抽出する（彩度が高い画素に重み付け、グレースケールは除外）
    """
    try:
        # 画像を読み込み
        img = image
        
        # 画像をリサイズして処理を高速化
        if img.size[0] > 100 or img.size[1] > 100:
            scale = min(100/img.size[0], 100/img.size[1])
            new_width = int(img.size[0] * scale)
            new_height = int(img.size[1] * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 画像をRGBに変換
        if img.mode != 'RGB':
            img = img.convert('RGB')
        # ピクセルデータを取得
        pixels = np.array(img.getdata())
        
        # 各ピクセルの彩度を計算して重み付け
        pixel_weights = {}  # ピクセルごとの重みを保存する辞書
        for pixel in map(tuple, pixels):
            # RGBを0-1の範囲に正規化
            rgb_normalized = np.array(pixel) / 255.0
            
            # RGBからHSVに変換
            hsv = rgb_to_hsv(rgb_normalized)
            saturation = hsv[1]  # 彩度（0-1の範囲）
            value = hsv[2]  # 明度（0-1の範囲）
            
            # 彩度が0（グレースケール）の場合はスキップ
            if saturation < 0.2 or value < 0.2:
                continue
            
            # 彩度に基づいて重みを計算（彩度が高いほど重みが大きい）
            # 彩度0.1以下は重み0.1、彩度1.0は重み1.0
            weight = max(0.1, saturation * value)
            
            # ピクセルの重みを累積
            if pixel in pixel_weights:
                pixel_weights[pixel] += weight
            else:
                pixel_weights[pixel] = weight
        
        # 最頻色を取得
        if pixel_weights:
            dominant_color = max(pixel_weights.items(), key=lambda x: x[1])[0]
        else:
            # すべての色がグレースケールの場合は、元の方法で最頻色を取得
            original_counts = Counter(pixels)
            dominant_color = max(original_counts.items(), key=lambda x: x[1])[0]
        
        return img, dominant_color
        
    except Exception as e:
        return None, None

def sort_images_by_hue(images: List[Image.Image]) -> List[Dict[str, Any]]:
    """
    imagesフォルダ内の画像を色相順に並べる
    """
    
    # 各画像の最頻色を取得
    image_data = []
    for image in images:
        img, dominant_color = get_dominant_color(image)
        if img is not None and dominant_color is not None:
            # RGBからHSVに変換して色相を取得
            hsv_color = rgb_to_hsv(np.array(dominant_color) / 255.0)
            hue = hsv_color[0]  # 色相（0-1の範囲）
            image_data.append({
                'path': image,
                'image': img,
                'dominant_color': dominant_color,
                'hue': hue
            })
    
    # 色相順にソート
    image_data.sort(key=lambda x: x['hue'])
    
    return image_data

def calc_grid_size(num_images: int, num_cols: int = 0, num_rows: int = 0) -> Tuple[int, int]:
    """
    画像の枚数を計算
    """
    if num_cols == 0 and num_rows == 0:
        return 0, 0
    
    if num_cols == 0:
        num_cols = (num_images + num_rows - 1) // num_rows
    if num_rows == 0:
        num_rows = (num_images + num_cols - 1) // num_cols
    
    return num_cols, num_rows

async def combine_images(files: List[UploadFile] = File(...), num_cols: int = 0, num_rows: int = 0):
    """
    メイン処理
    """
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
        raise HTTPException(status_code=400, detail=f"無効な画像ファイルが含まれています: {e}")

    # 画像を色相順にソート
    sorted_images = sort_images_by_hue(images)
    
    if not sorted_images:
        print("処理可能な画像が見つかりませんでした。")
        return
    
    print(f"{len(sorted_images)}枚の画像を処理しました。")
    
    # 元画像のサイズを分析してグリッドサイズを決定
    all_widths = []
    all_heights = []
    for img_data in sorted_images:
        width, height = img_data['image'].size
        all_widths.append(width)
        all_heights.append(height)
    
    # 中央値を使用して代表的なサイズを決定
    median_width = statistics.median(all_widths)
    median_height = statistics.median(all_heights)
    
    # アスペクト比を考慮してグリッドサイズを設定
    aspect_ratio = median_width / median_height
    
    if aspect_ratio > 1.5:  # 横長の画像が多い場合
        target_width = 300
        target_height = 200
    elif aspect_ratio < 0.7:  # 縦長の画像が多い場合
        target_width = 200
        target_height = 300
    else:  # 正方形に近い場合
        target_width = 250
        target_height = 250
    
    
    # 新しい画像を作成
    combined_image = Image.new('RGB', (target_width * num_cols, target_height * num_rows))
    
    # 対角線状のグラデーション配置順序を生成
    positions = []
    for s in range(num_cols + num_rows + 1):
        points = []
        for x in range(s + 1):
            y = s - x
            if 0 <= x < num_cols and 0 <= y < num_rows:
                points.append((x, y))
        if s % 2 == 0:
            points.reverse()
        positions.extend(points)
    
    # positionsの各位置に対して画像を配置
    for pos_idx, pos in enumerate(positions):
        # 画像インデックスを計算（循環させる）
        img_idx = pos_idx % len(sorted_images)
        img_data = sorted_images[img_idx]
        
        img = img_data['image']
        
        # アスペクト比を保ってリサイズ（隙間をなくすため、セルサイズに合わせる）
        width, height = img.size
        aspect_ratio = width / height
        
        # セルサイズに合わせてリサイズ（隙間をなくす）
        if aspect_ratio > 1:
            # 横長の画像
            new_width = target_width
            new_height = target_height
        else:
            # 縦長または正方形の画像
            new_width = target_width
            new_height = target_height
            
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 画像の配置位置を計算（隙間をなくす）
        col, row = pos
        x = col * target_width
        y = row * target_height
        
        combined_image.paste(resized_img, (x, y))
    
    # グリッドサイズ、セルサイズ、アスペクト比を表示
    print(f"グリッドサイズ: {num_cols}列 × {num_rows}行")
    print(f"セルサイズ: {target_width} × {target_height}")
    print(f"元画像の代表的なアスペクト比: {aspect_ratio:.2f}")

    # 画像を出力
    buffered = io.BytesIO()
    combined_image.save(buffered, format="JPEG", quality=95)

    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{img_str}"
    
    return data_url