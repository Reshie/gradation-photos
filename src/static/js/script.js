// script.js (ドラッグ＆ドロップ機能を追加)

// --- HTML要素の取得 ---
const imageInput = document.getElementById('imageInput');
const uploadButton = document.getElementById('uploadButton');
const gallery = document.getElementById('gallery');
const fileNameSpan = document.getElementById('fileName');
const galleryPlaceholder = document.getElementById('gallery-placeholder');
const toast = document.getElementById('toast');
const loader = document.getElementById('loader');
// ★★★ ドラッグ＆ドロップの対象となるエリア（<label>要素）を取得 ★★★
const uploadArea = document.querySelector('label[for="imageInput"]');


// --- 初期設定 ---
uploadButton.disabled = true;


// --- イベントリスナーの設定 ---

// [イベント1] ファイルインプットの中身が変わったとき（クリック選択またはドロップ後）
imageInput.addEventListener('change', () => {
    const numFiles = imageInput.files.length;
    if (numFiles > 0) {
        fileNameSpan.textContent = `${numFiles} 個のファイルが選択されました`;
    } else {
        fileNameSpan.textContent = '複数枚の画像を選択';
    }
    if (numFiles < 2) {
        uploadButton.disabled = true;
    } else {
        uploadButton.disabled = false;
    }
});

// [イベント2] 「グラデーションに並べる」ボタンがクリックされたとき
uploadButton.addEventListener('click', async () => {
    // (この関数の中身は変更ありません)
    const files = imageInput.files;
    if (files.length < 2) {
        showToast('画像を結合するには2つ以上のファイルを選択してください。');
        return;
    }
    const formData = new FormData();
    for (const file of files) {
        formData.append("files", file);
    }
    loader.style.display = 'block';
    try {
        const response = await fetch('/process-images/', { method: 'POST', body: formData });
        if (!response.ok) { throw new Error(`サーバーエラー: ${response.status}`); }
        const result = await response.json();
        if (result.status === "success") {
            addProcessedImageToGallery(result.image_data);
            if (galleryPlaceholder) { galleryPlaceholder.style.display = 'none'; }
            imageInput.value = '';
            fileNameSpan.textContent = '複数枚の画像を選択';
            uploadButton.disabled = true;
            showToast('画像の結合に成功しました！');
        } else {
            throw new Error(result.detail || '画像の処理に失敗しました。');
        }
    } catch (error) {
        console.error("Error:", error);
        showToast(`エラーが発生しました: ${error.message}`);
    } finally {
        loader.style.display = 'none';
    }
});

// ★★★ ここからドラッグ＆ドロップ用のイベントリスナーを追加 ★★★

// デフォルトの動作を無効化するための共通処理
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
    }, false);
});

// ファイルがエリア上に来たときの処理
uploadArea.addEventListener('dragenter', (e) => {
    uploadArea.classList.add('dragging'); // 見た目を変えるためのクラスを追加
});
uploadArea.addEventListener('dragover', (e) => {
    uploadArea.classList.add('dragging'); // ドラッグ中もクラスを維持
});

// ファイルがエリアから離れたときの処理
uploadArea.addEventListener('dragleave', (e) => {
    uploadArea.classList.remove('dragging'); // 見た目を元に戻す
});

// ファイルがドロップされたときの処理
uploadArea.addEventListener('drop', (e) => {
    uploadArea.classList.remove('dragging'); // 見た目を元に戻す

    // ドロップされたファイルを取得
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
        // 取得したファイルを<input>要素に設定
        imageInput.files = files;
        // changeイベントを手動で発火させ、既存の処理を呼び出す
        const changeEvent = new Event('change', { bubbles: true });
        imageInput.dispatchEvent(changeEvent);
    }
});
// ★★★ ドラッグ＆ドロップ処理ここまで ★★★


// --- UIを操作するヘルパー関数 ---
// (ここから下の関数は変更ありません)
function addProcessedImageToGallery(imageDataUrl) {
    const imageContainer = document.createElement('div');
    imageContainer.className = 'gallery-item';
    const img = document.createElement('img');
    img.src = imageDataUrl;
    img.alt = '結合された画像';
    imageContainer.appendChild(img);
    gallery.prepend(imageContainer);
}

function showToast(message) {
    toast.textContent = message;
    toast.className = "toast show";
    setTimeout(() => {
        toast.className = toast.className.replace("show", "");
    }, 3000);
}