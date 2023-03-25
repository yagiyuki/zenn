---
title: "画像分類の革命児、CLIPによる画像分類サンプル解説"
emoji: "📎"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["機械学習", "Python"]
published: true
---

2022年/5月にrinna社により、日本語特化した事前学習済みの言語画像モデルCLIPが公開されました。

https://prtimes.jp/main/html/rd/p/000000031.000070041.html

CLIPについては、以下の記事を参照ください。
https://qiita.com/sonoisa/items/00e8e2861147842f0237

以下、上記記事からCLIPの特徴を抜粋した情報です。

```
1. 従来のモデルに比べて、非常に広いクラスのオブジェクトを認識できる。
2. 画像とテキストの両方の埋め込みができる。画像から類似画像を探したり、テキストから類義テキストを探したりできるだけでなく、テキストから類義画像を探したり、その逆もできる。
3. ゼロショット（個別タスク用にファインチューニングしない）でも精度が高いケースがある。ファインチューニング用のデータセット構築が大変になるタスクの場合はとても嬉しい。
```

個人的には、2が革命的だと思います。
これまでの機械学習は、画像だったら画像のみ、テキストだったらテキストのみというように、画像とテキストを1つのモデルで扱うことができませんでした。
CLIPの登場で画像とテキストを1つのモデルで扱えるようになったので、AIがより人間に近づいているように思います。

使い方は簡単で、以下の`How to use the model`に従えば、簡単に試すことができます。
https://huggingface.co/rinna/japanese-cloob-vit-b-16

この記事では、`2. Run`のコードの動きについて深堀りしてみます。
また、現状のCLIPの精度が体感できるように、入力値などを変更して、動きを確認していきます。

## CLIPの利用方法

公式の`How to use the model` に記載されている通りの手順で動かすことができます。
https://huggingface.co/rinna/japanese-cloob-vit-b-16

とりあえず動かしたいという人は、GoogleのColaboratoryで上の手順を試してみましょう。
https://colab.research.google.com/?hl=ja


## サンプルコード解説

サンプルコードは、`["犬", "猫", "象"]`の3つのテキストと画像を比較して、画像を表すテキストとしてふさわしい情報を判定します。
出力値は確率値です。(例: 犬:70%、猫:20%、象:10% のように。)
サンプルコードの場合、`"犬"`の確率値が最も高く`1`(ほぼ100%)になっています。

なお、画像はこちらです。ゴールデンレトリバーなので、犬が正しいといます。
https://images.pexels.com/photos/2253275/pexels-photo-2253275.jpeg

以下、サンプルコードの各ステップにコメントを追加したコードです。
動きは、`How to use the model`の2と全く同じです。

```python
#
# 必要モジュールのimport
#
import io
import requests
from PIL import Image
import torch
import japanese_clip as ja_clip

# 利用環境(GPU or CPU)を指定する。
# GPUが利用可能であれば、GPUを優先する。
device = "cuda" if torch.cuda.is_available() else "cpu"

# 2つのモデルをロードをする
# model -> 画像および言語情報の特徴量を抽出するためのモデル
# preprocess -> 画像前処理用のモデル
model, preprocess = ja_clip.load("rinna/japanese-cloob-vit-b-16", device=device)
# テキストに指定するトークナイザー
tokenizer = ja_clip.load_tokenizer()

# MEMO1: 画像情報を取得
img = Image.open(io.BytesIO(requests.get('https://images.pexels.com/photos/2253275/pexels-photo-2253275.jpeg?auto=compress&cs=tinysrgb&dpr=3&h=750&w=1260').content))
# 画像に対して前処理(画像をエンコードする)
image = preprocess(img).unsqueeze(0).to(device)

# 
# "犬", "猫", "象"のテキストをエンコードする
# 
encodings = ja_clip.tokenize(
    texts=["犬", "猫", "象"],
    max_seq_len=77,
    device=device,
    tokenizer=tokenizer, # this is optional. if you don't pass, load tokenizer each time
)

with torch.no_grad():
    # 画像の特徴量を取得する
    image_features = model.get_image_features(image)
    # テキストの特徴量を取得する
    text_features = model.get_text_features(**encodings)
    
    # 
    # MEMO2: 画像に対するテキストの確率値を得る。(類似度が高いテキストほど確率が高い)
    # 
    text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)

print("Label Probs:", text_probs)  # prints: [[1.0, 0.0, 0.0]]
```

### MEMO1 

画像はクラウド上のデータから取得しています。
自身のパソコンの中にある画像データを推論に使いたい場合は、以下のようにコードを書き換えてみてください。


```python
img = Image.open('/content/image/path/hoge.jpeg')
# before
# img = Image.open(io.BytesIO(requests.get('https://images.pexels.com/photos/2253275/pexels-photo-2253275.jpeg?auto=compress&cs=tinysrgb&dpr=3&h=750&w=1260').content))
```

### MEMO2

類似度のとり方は、以下の手順となっています。

1. 画像と各テキストの内積を取る
2. 各内積の値に対して、100をかける
3. 「2」の値をsoftmax値(0〜1)に変換することで確率値を得る

以下、動作イメージです。

```python
import torch
image_features = torch.tensor([1., 2.])
text_features = torch.tensor([[0.001, 0.002], [0.002, 0.003], [0.003, 0.004]])

# 1. 画像と各テキストの内積を取る
res1 = image_features @ text_features.T
print(res1) # out -> tensor([[0.0050, 0.0080, 0.0110]])

# 2. 各内積の値に対して、100をかける
res2 = (100.0 * res1)
print(res2) # out -> tensor([[0.5000, 0.8000, 1.1000]])

# 3. 「2」の値をsoftmax値(0〜1)に変換することで確率値を得る
res3 = res2.softmax(dim=-1)
print(res3) # out -> tensor([[0.2397, 0.3236, 0.4368]])
```

「2」で100をかけているのは、「3」の結果の確率値の開きを大きくするためと思われます。
→ 最小と最大の確率値の幅を大きくするため。

サンプルコードのように100倍すると、確率値の結果が0or1になりがちです。
→1つのテキストに対する結果が1になる。
タスクによって大きさを調整してあげるのがよさそうです。
例えば、最小と最大の確率値の幅を小さくしたい場合は、0〜1の範囲の値をかけるとよさそうです。

CLIPの役割は画像やテキストの特徴量(ベクトル情報)を取るところまでです。
ベクトルを使った後の処理は、利用者側で自由にできます。

テキスト間のベクトル情報も取れるので、個人的には、word2vecとの出力の違いなども気になりました。

## 理解を深めるために

理解を深めるためサンプルコードの入力値を変えて動きを確認してみます。

### 文章を理解することはできるか

サンプルコードは、犬, 猫, 象というように、単語の推定になっていました。
これが文章だった場合は、推論できるのでしょうか?

試しに、以下のテキストでの推論を試みたころ、"犬が座っている"が1と判定されました。

```python
texts=["犬", "猫", "象", "犬が座っている", "猫が座っている", "象が座っている"]
```

内積の値(※MEMO2に記載した「1」)は、以下の通りでした。

```
367.9807, -24.3343,  38.1820, 449.3326,  31.2535, 105.9059
```
「犬が座っている」、「犬」が2トップでした。
また、「犬が座っている」>「犬」となっているので、状態を正確に捉えていることができていそうです。

### 犬種を予測することはできるか

犬と犬以外の動物ではなく、犬種の予測ができるかをみてみます。

以下のデータを予測させてみました。
```python
texts=["犬", " チワワ", "ブルドッグ", "ゴールデンレトリバー", "ごーるでんれとりばー", "ゴールデンレトリィバァ"]
```

結果は、ゴールデンレトリバーが1で、内積の値は以下のとおりでした。

```
367.9807,  80.2566,  52.4977, 699.2475,  41.1649,  15.9513
```

実際に犬の画像を見ると、ゴールデンレトリバーが正解なのでCLIPの判定は正しいといえそうです。
ただ、`ごーるでんれとりばー`, `ゴールデンレトリィバァ` という表記の内積の値は低い結果となりました。
スタンダードでない表記を判定することは難しそうです。
(※人間であれば、`ごーるでんれとりばー`, `ゴールデンレトリィバァ`も正と考えるはず。)
珍しい犬種の場合などもデータセットが不足している可能性があるので、判定が難しかもしれません。

## まとめ

所感として、学習なし(ゼロショット)でこれだけのことができるのは、すごいと感じました。
今後は、産業利用の視点で機械学習利用を考える場合、ゼロショットで扱えるモデルを探すというのが普通になりそうだなと思いました。

使い方など工夫の余地がありそうなので、引続き調査していこうと思います。

