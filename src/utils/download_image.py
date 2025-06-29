import requests

url = "https://code4fukui.github.io/find47/find47images_c.json"
response = requests.get(url)
data = response.json()

COUNT = 100

for d in data[101:201]:
    img = requests.get(f"https://find47.jp/ja/i/{d['code']}/image_file?type=thumb")
    with open(f"images/{d['id']}.jpg", "wb") as f:
        f.write(img.content)