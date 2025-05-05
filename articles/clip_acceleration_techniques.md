---
title: "PyTorchでCLIP推論を高速化する ── バッチ処理の実践と効果検証"
emoji: "⚡"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["pytorch", "clip", "マルチモーダルai", "速度改善"]
published: true
---

画像分類モデルCLIPを大量の画像に対して効率的にバッチ推論する実装方法のまとめです。
CLIPのモデルは、LINEヤフーの[clip-japanese-base](https://huggingface.co/line-corporation/clip-japanese-base)を使っています。

CLIPに限らずですが大量の画像を一括処理する場合、処理を1枚ずつ行っていると非常に時間がかかります。
そこで有効なのが「バッチ処理」です。バッチ処理でどこまで高速化できるのかをシンプルに検証しました。

検証コードは[こちら](https://github.com/yagiyuki/clip-study-playground/blob/52ecd1c/CLIP_acceleration_batch.ipynb)は公開しています。

## 実装1: 手動スライス

### 概要

* for 文とインデックススライスで画像リストを自分で分割してバッチ処理。
* 実装の自由度が高く、デバッグもしやすいが、やや冗長になる。実装ミスが起きやすいかも。

### サンプルコード

```python
# モデルのロード処理等は省略

batch_size = 50

with torch.no_grad():
    text = tokenizer(["ベンチプレス", "スクワット", "デッドリフト"]).to(device)
    text_feats = model.get_text_features(**text)

    image_paths = glob.glob('data/*')
    for i in range(0, len(image_paths), batch_size):
        # ここだけが追加：複数画像を一度に処理
        batch = image_paths[i:i+batch_size]
        imgs = [Image.open(p).convert("RGB") for p in batch]
        inputs = processor(images=imgs, return_tensors="pt").to(device)

        img_feats = model.get_image_features(inputs.pixel_values)

        probs = (img_feats @ text_feats.T).softmax(dim=-1)
        # …結果処理…
        #for path, p in zip(batch, probs):
        #    print(path, p)
```


## 実装2: DataLoader を使用

###  概要

* 画像のファイルパス一覧を DataLoader に渡し、自動的にバッチ化
* バッチ単位でファイルパスが渡ってくるので、毎回それらを読み込み・前処理する
* バッチ化する部分を自動でやってくれるため実装1よりコードが簡潔になる
    * ただし、合わせて前処理を並列化する場合は、別途 Dataset クラスなどの工夫が必要で実装が複雑化する（詳細は割愛）

### サンプルコード

```python
# モデルのロード処理等は省略
# 画像パス一覧
image_paths = glob.glob('data/*')

# DataLoader で自動的に path のリストをバッチ化
dataloader = DataLoader(
    image_paths,
    batch_size=50,
    shuffle=False
)

with torch.no_grad():
    for batch_paths in dataloader:
        # batch_paths は文字列のリスト
        imgs = [Image.open(p).convert("RGB") for p in batch_paths]
        inputs = processor(images=imgs, return_tensors="pt").to(device)
        img_feats = model.get_image_features(inputs.pixel_values)
        probs = (img_feats @ text_feats.T).softmax(dim=-1)
        # …結果処理…
        #for path, p in zip(batch_paths, probs):
        #    print(path, p)

```

## 簡易的な検証結果 (CLIP @ Google Colab + T4 GPU)

参考として、CLIPモデルを題材にGoogle Colab (T4 GPU)でこれらのテクニックを試してみました（1000枚の同一画像、固定テキストラベルを使用）。ベースラインと比較したざっくりとした結果はこんな感じです。

* ベースライン(1枚ずつ処理): 30.5 s
* 実装1（バッチサイズ50）: 17.2 s
* 実装2（バッチサイズ50）: 17.6 s

実装2は実装1よりわずかに遅くなりましたが、誤差の範囲内です。速度差は小さく、どちらの方法でも高速化の効果が得られます。
実装2のほうがコードが簡潔になるため、保守性や見通しの良さを重視する場合にはこちらを選ぶのが適しています。

## まとめ

簡易的な検証であるものの、大量の画像をまとめて処理する場面では、バッチ処理が推論速度の向上に大きく貢献するといえそうでした。
なお、環境やモデルによって結果は異なる可能性があるため、ご自身の用途に応じて検証することをおすすめします。