---
title: "spaCyで固有表現を抽出する【機械学習の知識0でも理解できます】"
emoji: "🪐"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["機械学習", "深層学習", "ディープラーニング", "Python"]
published: true
---


[spaCy](https://github.com/explosion/spaCy)を使って、文章から固有表現を抽出する方法を書きます。
spaCyは自然言語処理の多くのタスクを統合したライブラリです。
例えば、こんなことができます。

* 固有表現抽出
* 係り受け解析
* 形態素解析

また、CNNで学習したモデルも組み込まれています。お試しで使う分には、学習データを用意する必要もありません。
(もちろん、独自の学習データでモデルをつくることもできます。)

手軽にディープラーニングで自然言語処理をやってみたい方にはとても便利です！

ちなみに、spaCyのv2.2系までは、日本語の学習済みモデルがありませんでした。
よって、日本語の解析をするには、学習データを用意する必要がありました。
(もしくは、[GiNZA](https://github.com/megagonlabs/ginza)というspaCyの派生ライブラリを使う必要があった)
v2.3系から日本語の学習済みモデルが組み込まれたので、spaCy単体で日本語のデータ分析ができるようになりました!
https://spacy.io/usage/v2-3


## 環境構築

検証環境は、[Colaboratory](https://colab.research.google.com/notebooks/welcome.ipynb?hl=ja)を使います。  
Colaboratoryは、googleが提供する無償のpython実行環境です。  
jupyterインタフェースで操作ができて、機械学習ライブラリの検証やデータ分析に、とても便利です。


### spaCyをインストール

Colaboratoryには、デフォルトでspacyが入っていますがバージョンが2.2系(2021/05月時点)です。 
日本語の学習済みモデルを使う場合は、2.3系以上をインストールする必要があります。


```python
# このコマンドで、2.2系が消えて3.0.6が入る
%%bash
pip install spacy==3.0.6
```

### 学習済みモデルをインストール

学習済みモデルには、大中小の3種類あります。
https://spacy.io/models/ja

今回は、`ja_core_news_sm`, `ja_core_news_md`の2つを使います。

```python
%%bash
python -m spacy download ja_core_news_sm
python -m spacy download ja_core_news_md
```


## 固有表現の抽出

本題の固有表現抽出をやっています。  
始める前に、以下でパッケージをリロードしておいてください。

```python
import pkg_resources, imp
imp.reload(pkg_resources)
```

上記の処理をすることで、インストールしたモデルを読み込むことができます。
では、インストールしたモデルで固有表現を抽出してみましょう。

```python
import spacy

# モデルのロード
nlp = spacy.load("ja_core_news_md")
# 解析対象のテキストa
input_text = "2018年の8月に旅行にフランスへ旅行に行った。ルーヴル美術館でモナ・リザの絵を見た。" 
# モデルに解析対象のテキストを渡す
doc = nlp(input_text)
# 固有表現を抽出
for ent in doc.ents: 
    print(ent.text, ent.label_, ent.start_char, ent.end_char)

# out --> 
## 2018年 DATE 0 5
## 8月 DATE 6 8
## フランス GPE 12 16
## ルーヴル美術館 ORG 24 31
```

これだけです。非常に少ないコードで結果を出すことができます。
つぎにモデルを`ja_core_news_md`に変えてみます。 

```python
import spacy

# モデルのロード
nlp = spacy.load("ja_core_news_md")
# 解析対象のテキストa
input_text = "2018年の8月に旅行にフランスへ旅行に行った。ルーヴル美術館でモナ・リザの絵を見た。"
# モデルに解析対象のテキストを渡す
doc = nlp(input_text)
# 固有表現を抽出
for ent in doc.ents:
    print(ent.text, ent.label_, ent.start_char, ent.end_char)

# out --> 
## 2018年 DATE 0 5
## 8月 DATE 6 8
## フランス GPE 12 16
## ルーヴル美術館 ORG 24 31
## モナ・リザ PERSON 32 37
```

新たに、「モナ・リザ」が人名として抽出できることがわかります。
モデルサイズに比例して、固有表現のバリエーションが増えるのだと思います。
より多くのバリエーションのデータを取りたいときは、`ja_core_news_lg`を使えばよさそうですね。

また、抽出結果を可視化することもできます。
```python
from spacy import displacy
displacy.render(doc, style="ent", jupyter=True)
```

![](https://storage.googleapis.com/zenn-user-upload/hnsu0oourw83buh13fp2kp74ygo2)
ブログやプレゼンなどの説明に便利そうですね。

## 文脈によって抽出結果は変わるか? 

結論からいうと、抽出結果は文脈にも多少依存があるようです。

```python
import spacy 
nlp = spacy.load("ja_core_news_sm")
input_text = "川崎へ行く"

#
# 「川崎」がGPE(地名)として抽出される
#
doc = nlp(input_text)
for ent in doc.ents:
    print(ent.text, ent.label_, ent.start_char, ent.end_char)
# out -> 川崎 GPE 0 2
```

```python
import spacy 
nlp = spacy.load("ja_core_news_sm") 
input_text = "川崎さんの家"

#
# 「川崎」がPERSON(人物)として抽出される
#
doc = nlp(input_text)
for ent in doc.ents:
    print(ent.text, ent.label_, ent.start_char, ent.end_char)
# out -> 川崎 PERSON 0 2
```

抽出できた固有表現は同一ですが、ラベルが異なることがわかります。
冒頭で説明した通り、spaCyの学習済みモデルは、CNNベースのモデルです。  
CNNベースのモデルは、連続性を考慮した学習に適していないので、文脈と抽出結果の依存は低い認識だったのでちょっと意外でした。

ちなみに、連続した情報の解釈に有効な手段としては、RNNが有名です。  
CNNとRNNの違いは、こちらが参考になるので興味がある方は見てください。

https://lionbridge.ai/ja/articles/neural-network-cnn-rnn/

## まとめ

spaCyを使えばお手軽に固有表現抽出のタスクを実施する方法を書きました。
spaCyは、固有抽出表現以外にも多くの自然言語処理タスクを手軽に試すことができます。
興味のある方はぜひ参考にしてください！
