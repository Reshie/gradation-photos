// script.js

// --- HTML要素の取得 ---
// これから操作するHTML要素を、IDを元に見つけて変数に格納しておく
const imageInput = document.getElementById('imageInput');
const uploadButton = document.getElementById('uploadButton');
const gallery = document.getElementById('gallery');
const fileNameSpan = document.getElementById('fileName');
const galleryPlaceholder = document.getElementById('gallery-placeholder');
const toast = document.getElementById('toast');
const loader = document.getElementById('loader');


// --- イベントリスナーの設定 ---
// ユーザーの操作（イベント）をきっかけに処理を開始するための設定

// [イベント1] ファイルインプットの中身が変わったとき（ファイルが選択されたとき）
imageInput.addEventListener('change', () => {
    const numFiles = imageInput.files.length;
    if (numFiles > 0) {
        // 1つ以上のファイルが選択されたら、ファイル数を表示
        fileNameSpan.textContent = `${numFiles} 個のファイルが選択されました`;
    } else {
        // ファイルが選択されていない状態に戻ったら、元のテキストを表示
        fileNameSpan.textContent = 'クリックしてファイルを選択 (複数可)';
    }
});

// [イベント2] 「結合して生成」ボタンがクリックされたとき
uploadButton.addEventListener('click', async () => {
    const files = imageInput.files;

    // ファイルが2つ未満の場合は処理を中断し、ユーザーに通知
    if (files.length < 2) {
        showToast('画像を結合するには2つ以上のファイルを選択してください。');
        return; // ここで処理を終了
    }

    // サーバーに送るためのデータ形式（FormData）を作成
    const formData = new FormData();
    // 選択されたファイルを一つずつFormDataに追加
    for (const file of files) {
        formData.append("files", file); // "files"というキーでファイルを追加
    }

    loader.style.display = 'block'; // ローディングアニメーションを表示

    try {
        // Fetch APIを使って、サーバーの '/process-images/' へデータを送信
        const response = await fetch('/process-images/', {
            method: 'POST', // POSTメソッドで送信
            body: formData, // 送信するデータ本体
        });

        // サーバーからの応答が失敗だった場合、エラーを発生させる
        if (!response.ok) {
            throw new Error(`サーバーエラー: ${response.status}`);
        }

        // サーバーからの応答(JSON形式)をJavaScriptオブジェクトに変換
        const result = await response.json();
        
        // サーバーからの処理結果に応じて表示を分岐
        if (result.status === "success") {
            // 成功した場合
            addProcessedImageToGallery(result.image_data); // ギャラリーに画像を追加
            if (galleryPlaceholder) {
                galleryPlaceholder.style.display = 'none'; // 「まだ画像がありません」の表示を消す
            }
            imageInput.value = ''; // ファイル選択をリセット
            fileNameSpan.textContent = 'クリックしてファイルを選択 (複数可)'; // テキストを元に戻す
            showToast('画像の結合に成功しました！'); // 成功メッセージを表示
        } else {
            // 失敗した場合 (サーバーがエラーを返した場合)
            throw new Error(result.detail || '画像の処理に失敗しました。');
        }

    } catch (error) {
        // 通信エラーや処理中のエラーが発生した場合
        console.error("Error:", error);
        showToast(`エラーが発生しました: ${error.message}`); // エラーメッセージを表示
    } finally {
        // 成功・失敗にかかわらず、最後に必ず実行される
        loader.style.display = 'none'; // ローディングアニメーションを非表示
    }
});


// --- UIを操作するヘルパー関数 ---
// 特定のUI操作をまとめた小さな関数群

/**
 * 生成された画像をギャラリーに追加する関数
 * @param {string} imageDataUrl - 表示する画像のデータURL
 */
function addProcessedImageToGallery(imageDataUrl) {
    // 画像を囲むためのdiv要素を作成
    const imageContainer = document.createElement('div');
    // ★修正点: 新しく定義したCSSクラスを指定する
    imageContainer.className = 'gallery-item';
    
    // img要素を作成
    const img = document.createElement('img');
    img.src = imageDataUrl; // サーバーから受け取った画像データを設定
    img.alt = '結合された画像';
    // ★修正点: img要素のクラス指定は不要（親の.gallery-item imgでスタイルが適用されるため）
    // img.className = 'w-full h-auto object-contain'; // ← この行を削除またはコメントアウト

    // divの中にimgを入れて、それをギャラリーの先頭に追加
    imageContainer.appendChild(img);
    gallery.prepend(imageContainer);
}

/**
 * 通知トーストを表示する関数
 * @param {string} message - 表示したいメッセージ
 */
function showToast(message) {
    toast.textContent = message;
    toast.className = "toast show"; // 'show'クラスを追加して表示
    // 3秒後に'show'クラスを削除して非表示に戻す
    setTimeout(() => {
        toast.className = toast.className.replace("show", "");
    }, 3000);
}