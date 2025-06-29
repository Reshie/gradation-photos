// --- HTML要素の取得 ---
const imageInput = document.getElementById('imageInput');
const uploadButton = document.getElementById('uploadButton');
const gallery = document.getElementById('gallery');
const fileNameSpan = document.getElementById('fileName');
const galleryPlaceholder = document.getElementById('gallery-placeholder');
const toast = document.getElementById('toast');
const loader = document.getElementById('loader');

// ★★★ 機能1: ページ読み込み時にボタンを「無効」状態にする ★★★
uploadButton.disabled = true;

// --- イベントリスナーの設定 ---

// ★★★ 機能2: ファイルが選択されたら、枚数をチェックしてボタンの状態を切り替える ★★★
imageInput.addEventListener('change', () => {
    const numFiles = imageInput.files.length;

    // ファイル数のテキスト表示を更新
    if (numFiles > 0) {
        fileNameSpan.textContent = `${numFiles} 個のファイルが選択されました`;
    } else {
        fileNameSpan.textContent = '複数枚の画像を選択';
    }

    // ファイルが2枚未満ならボタンを無効化、2枚以上なら有効化する
    if (numFiles < 2) {
        uploadButton.disabled = true;
    } else {
        uploadButton.disabled = false;
    }
});

// [イベント2] 「グラデーションに並べる」ボタンがクリックされたとき
uploadButton.addEventListener('click', async () => {
    const files = imageInput.files;

    // このチェックは念のため残しますが、ボタンが無効化されているので通常は実行されません
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
        const response = await fetch('/process-images/', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`サーバーエラー: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.status === "success") {
            addProcessedImageToGallery(result.image_data);
            if (galleryPlaceholder) {
                galleryPlaceholder.style.display = 'none';
            }
            imageInput.value = '';
            fileNameSpan.textContent = '複数枚の画像を選択';
            
            // ★★★ 機能3: 処理完了後、再度ボタンを「無効」状態に戻す ★★★
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