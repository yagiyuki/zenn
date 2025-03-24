---
title: "PythonでQPS上限を指定して画像をダウンロードする"
emoji: "🔖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Python"]
published: false
---

Pythonで指定QPS範囲で画像をダウンロードするプログラムを書きました。
QPSはQueries Per Secondのことです。
今回の場合、1秒間にダウンロードする画像件数のことを指します。
たとえば、10QPSならば1秒間に10枚の画像をダウンロードするという意味になります。

クロール先のサイトの負荷を軽減するためにQPS上限を指定することは重要です。
以下がコード例となります。

```python
import os
import time
import requests

def download_image(url, save_path):
    try:
        response = requests.get(url)
    except:
        print(f'err request url = {url}')
        return

    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
    else:
        print(f'status code not 200 url = {url}, status_code = {response.status_code}')

def download_images_with_qps(image_urls, qps, download_folder):
    os.makedirs(download_folder, exist_ok=True)
    
    interval = 1 / qps
    last_download_time = time.time()
    
    for index, url in enumerate(image_urls):
        elapsed_time = time.time() - last_download_time
        if elapsed_time < interval:
            time.sleep(interval - elapsed_time)
        
        save_path = os.path.join(download_folder, f'image_{index}.jpg')
        download_image(url, save_path)
        last_download_time = time.time()

# 以下のリストにダウンロードしたい画像のURLを追加
image_urls = [
    "https://1.bp.blogspot.com/-_JwCwOPPE1s/X9GYHH3CirI/AAAAAAABctM/RpxqJYP7syENbaaWyNIfhi2SsLGeNaEQgCNcBGAsYHQ/s400/food_sushi_kobore_ikura_don.png",
    "https://1.bp.blogspot.com/Err.png", # リクエストのステータスが200以外
    "https://not url text", # リクエスト不可
    "https://1.bp.blogspot.com/-w7IdkWA1IeM/X9lJUbYQrqI/AAAAAAABc3k/Tyl_KW-RUqsvzkMold-bwKMb83-pI1VsACNcBGAsYHQ/s501/food_pizza_cut_cheese.png",
]

qps = 10  # クエリあたりのリクエスト数を指定
download_folder = "downloaded_images"  # 画像を保存するフォルダ名を指定

download_images_with_qps(image_urls, qps, download_folder)
```

画像は、[いらすとや](https://www.irasutoya.com/) のものを使わせてもらいました。

今回は、QPSは10としています。
QPSを変更したい場合は、`qps = 10`の値を適宜調整してください。

以上です。外部サイトから画像ダウンロードをする処理を実装するさいに参考にいただければと思います。
