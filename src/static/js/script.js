const imageInput = document.getElementById('imageInput');
const uploadButton = document.getElementById('uploadButton');
const gallery = document.getElementById('gallery');
const fileNameSpan = document.getElementById('fileName');
const galleryPlaceholder = document.getElementById('gallery-placeholder');
const toast = document.getElementById('toast');
const loader = document.getElementById('loader');
const uploadArea = document.querySelector('label[for="imageInput"]');

// アプリケーションが処理中かどうかを管理するフラグ
let isLoading = false;



// --- 初期設定 ---
uploadButton.disabled = true;


// --- イベントリスナーの設定 ---

// [イベント1] ファイルインプットの中身が変わったとき
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
    if (isLoading) return;
    const files = imageInput.files;
    if (files.length < 2) {
        showToast('画像を結合するには2つ以上のファイルを選択してください。');
        return;
    }

    isLoading = true;
    uploadButton.disabled = true;
    // ★★★ 1. ファイル選択自体を無効化 ★★★
    imageInput.disabled = true; 
    loader.style.display = 'flex'; 

    const formData = new FormData();
    for (const file of files) { formData.append("files", file); }
    
    try {
        const response = await fetch('/process-images/', { method: 'POST', body: formData });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'サーバーから不明なエラーが返されました。' }));
            throw new Error(errorData.detail || `サーバーエラー: ${response.status}`);
        }
        const result = await response.json();
        if (result.status === "success") {
            addProcessedImageToGallery(result.image_data);
            if (galleryPlaceholder) { galleryPlaceholder.style.display = 'none'; }
            imageInput.value = '';
            fileNameSpan.textContent = '複数枚の画像を選択';
            
            // ★★★ 2. ファイルクリア後、changeイベントを発火させてボタンの状態を正しく更新 ★★★
            imageInput.dispatchEvent(new Event('change'));
            
            showToast('画像の生成に成功しました！');
        } else {
            throw new Error(result.detail || '画像の処理に失敗しました。');
        }
    } catch (error) {
        console.error("Error:", error);
        showToast(`エラーが発生しました: ${error.message}`);
        // エラー後、ファイルは選択されたままなので、ボタンを再度有効化する
        if (imageInput.files.length >= 2) {
            uploadButton.disabled = false;
        }
    } finally {
        isLoading = false;
        // ★★★ 3. 処理完了後、ファイル選択を再度有効化 ★★★
        imageInput.disabled = false;
        loader.style.display = 'none';
    }
});

// --- ドラッグ＆ドロップ用のイベントリスナー (変更なし) ---
uploadArea.addEventListener('dragenter', (e) => {
    e.preventDefault(); e.stopPropagation();
    if (isLoading) { uploadArea.classList.add('busy'); } 
    else { uploadArea.classList.add('dragging'); }
});
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault(); e.stopPropagation();
    if (isLoading) { uploadArea.classList.add('busy'); }
    else { uploadArea.classList.add('dragging'); }
});
uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault(); e.stopPropagation();
    uploadArea.classList.remove('dragging');
    uploadArea.classList.remove('busy');
});
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault(); e.stopPropagation();
    uploadArea.classList.remove('dragging');
    uploadArea.classList.remove('busy');
    if (isLoading) return; 
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
        imageInput.files = files;
        const changeEvent = new Event('change', { bubbles: true });
        imageInput.dispatchEvent(changeEvent);
    }
});


// --- UIを操作するヘルパー関数 ---
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