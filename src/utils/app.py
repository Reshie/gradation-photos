from PIL import Image
import numpy as np
import statistics
import math
import os
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv
from typing import Tuple, Optional, List, Dict, Any

def get_dominant_color(image_path: str) -> Tuple[Optional[Image.Image], Optional[Tuple[int, int, int]]]:
    """
    画像から最頻色（最頻値）を抽出する（彩度が高い画素に重み付け、グレースケールは除外）
    """
    try:
        # 画像を読み込み
        img = Image.open(image_path)
        
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
        print(f"画像 {image_path} の処理中にエラーが発生しました: {e}")
        return None, None

def sort_images_by_hue(image_folder: str) -> List[Dict[str, Any]]:
    """
    imagesフォルダ内の画像を色相順に並べる
    """
    image_files = []
    
    # imagesフォルダ内の画像ファイルを取得
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            image_path = os.path.join(image_folder, filename)
            image_files.append(image_path)

    print(f"画像の枚数: {len(image_files)}")
    
    # 各画像の最頻色を取得
    image_data = []
    for image_path in image_files:
        img, dominant_color = get_dominant_color(image_path)
        if img is not None and dominant_color is not None:
            # RGBからHSVに変換して色相を取得
            hsv_color = rgb_to_hsv(np.array(dominant_color) / 255.0)
            hue = hsv_color[0]  # 色相（0-1の範囲）
            image_data.append({
                'path': image_path,
                'image': img,
                'dominant_color': dominant_color,
                'hue': hue
            })
    
    # 色相順にソート
    image_data.sort(key=lambda x: x['hue'])
    
    return image_data

def create_combined_image(sorted_images: List[Dict[str, Any]], output_path: str = 'combined_images.jpg') -> Optional[Image.Image]:
    """
    ソートされた画像を横方向につなげて1枚の画像を作成
    """
    if not sorted_images:
        print("画像が見つかりませんでした。")
        return None
    
    # すべての画像を同じ高さにリサイズ
    target_height = 200
    resized_images = []
    
    for img_data in sorted_images:
        img = img_data['image']
        width, height = img.size
        
        # アスペクト比を保ってリサイズ
        aspect_ratio = width / height
        new_width = int(target_height * aspect_ratio)
        resized_img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
        resized_images.append(resized_img)
    
    # 横方向につなげる
    # 結合後の画像の幅を計算
    total_width = sum(img.size[0] for img in resized_images)
    
    # 新しい画像を作成
    combined_image = Image.new('RGB', (total_width, target_height))
    
    # 画像を横方向に配置
    x_offset = 0
    for img in resized_images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.size[0]
    
    # 画像を保存
    combined_image.save(output_path, 'JPEG', quality=95)
    print(f"結合された画像を {output_path} に保存しました。")
    
    return combined_image

def main() -> None:
    """
    メイン処理
    """
    image_folder = 'images'
    
    print("画像を色相順に並べています...")
    print("（彩度が高い画素に重み付け、グレースケールは除外して最頻色を計算）")
    
    # 画像を色相順にソート
    sorted_images = sort_images_by_hue(image_folder)
    
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
    
    # 画像の配置を決定
    num_images = len(sorted_images)
    # num_cols = 10
    # num_rows = (num_images + num_cols - 1) // num_cols  # 必要な行数を計算
    num_cols = 20
    num_rows = 10
    
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
    
    # 画像を配置
    for i, img_data in enumerate(sorted_images):
        if i >= len(positions):
            break
            
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
        col, row = positions[i]
        x = col * target_width
        y = row * target_height
        
        combined_image.paste(resized_img, (x, y))
    
    # 画像を保存
    output_path = 'combined_images.jpg'
    combined_image.save(output_path, 'JPEG', quality=95)
    print(f"結合された画像を {output_path} に保存しました。")
    print(f"グリッドサイズ: {num_cols}列 × {num_rows}行")
    print(f"セルサイズ: {target_width} × {target_height}")
    print(f"元画像の代表的なアスペクト比: {aspect_ratio:.2f}")

    # 各画像の情報を表示
    # print("\n色相順に並べられた画像:")
    # for i, img_data in enumerate(sorted_images):
    #     filename = os.path.basename(img_data['path'])
    #     hue_degrees = img_data['hue'] * 360  # 度に変換
    #     color = img_data['dominant_color']
    #     print(f"{i+1:2d}. {filename} - 色相: {hue_degrees:.1f}° - 最頻色: RGB{color}")

if __name__ == "__main__":
    main()
