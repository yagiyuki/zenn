---
title: "機械学習の高速化テクニック3選"
emoji: "💨"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["機械学習", "Python"]
published: true
---

機械学習の高速化テクニックを3つまとめました。 
手を動かしながら、3つのテクニックを検証する流れになっています。  

今回あげたテクニックは、ツールや環境に依存しないものです。  
例えば、以下のようなものは載せていません。  

* マシンスペックをあげる
* プロセッサをかえる (CPUではなくGCPを使うなど)
* 高速に動作するツールを使う(XGBoostからLightGBMにかえる) 

汎用的なテクニックをまとめたので、どんなタスクにも応用できるはずです。　　
ぜひ参考にしてみてください。  


## データセットの準備

今回は、文章分類タスクに取り組みながら、高速化テクニックを実践します。    
そのためのデータセットとして、livedoor ニュースコーパスを使います。    
https://www.rondhuit.com/download.html#ldcc


### データセットのダウンロード

まずは、データセットをダウンロード&&展開します。  

```
wget https://www.rondhuit.com/download/ldcc-20140209.tar.gz
tar xzf ldcc-20140209.tar.gz
```

展開すると直下にディレクトリ`text`というディレクトリがあり、その下に9つのディレクトリがあります。

```
topic-news
sports-watch
kaden-channel
smax
livedoor-homme
it-life-hack
dokujo-tsushin
peachy
movie-enter
```

個々のディレクトリにはニュース記事が入っています。

```
# 独女通信の例
./text/
├── CHANGES.txt
├── dokujo-tsushin
│   ├── dokujo-tsushin-4778030.txt
│   ├── dokujo-tsushin-4778031.txt
│   ├── dokujo-tsushin-4782522.txt
│   ├── dokujo-tsushin-4788357.txt
│   ├── dokujo-tsushin-4788362.txt
```

### 必要カラムの抜き出し

以下の情報を抜き出します。  
* ファイル名
* カテゴリラベル
* カテゴリ名
* ニュース記事のタイトル(学習対象)

```python
import os

#
# テキスト直下のディレクトリ一覧を取得(これがカテゴリになる。)
#
dirlist = os.listdir('text')
category_list = {}
i=0
for dirname in dirlist:
    if dirname[-3:] != 'txt':
        category_list[str(i)] = dirname
        i+=1

#
# データセットを作成して、ファイルに出力する。
#　　ファイルはtsv形式で、ファイル名、ラベルid、カテゴリ名、テキストを出力する。
#
with open('dataset.tsv', 'w') as f_out:
    for label, category in category_list.items():
        path = './text/{}/'.format(category)
        filelist = os.listdir(path)
        filelist.remove('LICENSE.txt')
        for filename in filelist:
            with open(path + filename, 'r') as f_in:
                # テキストはタイトルのみ取得　(本文は学習対象にしない)
                text = f_in.readlines()[2]
                # カラム生成
                out_row = [filename, label, category, text]
                f_out.write("\t".join(out_row))
```

`dataset.tsv` というファイルが生成されて、以下のようなデータがあれば、成功です。

```
topic-news-6612237.txt	0	topic-news	神戸「サンテレビ」、プロ野球中継で放送事故
topic-news-6298663.txt	0	topic-news	フジで午後のワイドショーが復活、韓流推し反対デモの影響は「関係ない」に物議
topic-news-6625187.txt	0	topic-news	「全てのトイレを和式に」 野村ホールディングス株主の珍提案が海外で話題に
topic-news-6118456.txt	0	topic-news	女性教授が男子生徒に「なめるな」「テクニシャン」などと発言し提訴される
topic-news-6657046.txt	0	topic-news	「週刊文春」でAKB指原交際報道、衝撃内容にファン「絶対許さない」
```

### 学習とテストデータに分離

データをpandasでロードしたうえで、学習データとテストデータを分離します。  
ロード時は必ずランダムサンプリングを実施してください。   
実施しない場合は、データに偏りが出て、正確な検証ができなくなります。

```python
import pandas as pd
df = pd.read_table(
    'dataset.tsv',
    names=['filename', 'label', 'category', 'text']
    ).sample(frac=1, random_state=0).reset_index(drop=True)
```



```python
#
# データを学習:テスト用=8:2に分割
#
N = len(df)
train_df = df[:int(N * 0.8)] # 学習
test_df = df[int(N * 0.8):] # テスト
```

## ベースライン

### 設定
ベースラインに対して、高速化テクニックを加えることで、効果を見ていきます。  
ベースラインとして設定が必要なのは、「前処理」と「文章分類ツール」です。

今回は、以下の条件をベースラインとします。

```
# 前処理
テキストの加工処理は、sudachiによるトークン化のみとする。　
正規化やストップワード除去などは、実施しない。
文章ベクトルは、Bag-of-Word形式とする。 
```

```
# 文章分類ツール
sklearnのロジスティック回帰をツールとして使う。
ハイパーパラメータは、デフォルトの状態とする。　
```

ベースラインの前処理コードは、以下を使います。

```python
from unicodedata import normalize
from sudachipy import tokenizer
from sudachipy import dictionary
import string

from sklearn.feature_extraction.text import CountVectorizer

#
# 前処理
#
class TextPreprocessing(object):
    def __init__(self):
        self.tokenizer_obj = dictionary.Dictionary().create()
        self.mode = tokenizer.Tokenizer.SplitMode.A
        self.vectorizer = CountVectorizer()

    #
    # テキストに対して前処理を実施
    #
    def _preprocess(self, text):
        # トークン化
        morphs = []
        for m in self.tokenizer_obj.tokenize(text, self.mode):
            morphs.append(m.surface())

        return " ".join(morphs)

    #
    # 文章データの行列を生成(各文章に対するベクトル一覧)
    #
    def get_matrix(self, text_series, mode='train'):
        text_series = text_series.map(self._preprocess)

        if mode == 'train':
            # 辞書作成と文章データの行列を作成
            bag = self.vectorizer.fit_transform(text_series)
        else:
            # 文章データの行列を作成 ※ 辞書はtrainでつくったものを使用
            bag = self.vectorizer.transform(text_series)

        return bag
```

### 評価

ベースラインに対して、処理速度とモデル性能を評価します。  
性能は、テストデータに対する正解率(accuracy)評価します。

性能を評価する理由は、改善により**性能が極端に劣化していない**ことをみるためです。 
処理の高速化をしたことで、モデル性能が下がったら元も子もないので^^;

処理速度は、以下の時間を評価対象します。

* 学習データに対する前処理の時間
* 学習時間

:::message
検証環境はGoogle Colaboratoryを使っており、処理時間は`%%time`で計測したuserの時刻としています。　
![](https://storage.googleapis.com/zenn-user-upload/b3slshixi4zihx62gf2tuejnx9lj)
:::

評価に使ったコードは、それぞれ以下の通りです。　

```python
%%time
# 学習データに対する前処理
tp = TextPreprocessing()
bag = tp.get_matrix(train_df.text)
train_X = bag.toarray()
train_y = pd.Series(train_df.label)
```

```python
%%time
# 学習
from sklearn.linear_model import LogisticRegression

clf = LogisticRegression()
clf.fit(train_X, train_y)
```

```python
# 正解率
bag_test = tp.get_matrix(test_df.text, mode='test')
test_X = bag_test.toarray()
test_y = pd.Series(test_df.label)
score = clf.score(test_X, test_y)
print(score)
```

評価した結果以下のとおりとなりました。

* 学習データに対する前処理の時間: 14.2s
* 学習時間: 82s
* 正解率: 0.8005427408412483


## 高速化テクニック1: スパース行列の利用

文章行列である`train_X`をスパース行列型に変更します。

今回はBag-of-Word形式で文章ベクトルを生成しています。
Bag-of-Wordで作った文章行列は性質上0を大量に含んだ行列なります。

```python
print(train_X)
# -> out
#[[0 0 0 ... 0 0 0]
# [0 0 0 ... 0 0 0]
# [0 0 0 ... 0 0 0]
# ...
# [1 0 0 ... 0 0 0]
# [0 0 0 ... 0 0 0]
# [0 0 0 ... 0 0 0]]
```

この特徴を持つ行列は、scipyのスパース行列に変換すると、メモリ削減・処理速度向上の効果があります。

```python
%%time
from scipy.sparse import lil_matrix
from sklearn.linear_model import LogisticRegression

train_X = lil_matrix(train_X) # スパース行列に変換

clf = LogisticRegression()
clf.fit(train_X, train_y)
```

学習時間が82s -> 3.6s に大幅に縮まりました。
行列の型を変更するだけでモデル性能に影響を与えることはありません。     
やらない理由が無いですね！


## 高速化テクニック2: 特徴量を減らす

特徴量を減らすのも有効なテクニックです。   
今回のタスクの場合、特徴量=語彙になります。   
改善のポイントは、**性能に極力影響を及ばさない範囲で語彙数**を削減することです。

まずは、以下の改善を実施していきます。

* ユニコード正規化
* 記号などのノイズ除去
* アルファベットは小文字に統一
* 品詞選択(名詞のみを使用)
* 数値除去

```python
from unicodedata import normalize
import string
from sudachipy import tokenizer
from sudachipy import dictionary

from sklearn.feature_extraction.text import CountVectorizer

#
# 前処理
#
class TextPreprocessing(object):
    def __init__(self):
        self.tokenizer_obj = dictionary.Dictionary().create()
        self.mode = tokenizer.Tokenizer.SplitMode.A
        punctuation = string.punctuation + '。、×÷ 【】『』 「」”“'
        self.noises = str.maketrans(
            {k: ' ' for k in normalize('NFKC', punctuation)})
        self.vectorizer = CountVectorizer()


    #
    # ユニコード正規化を実施したうえで、トークン化を実施
    #
    def _preprocess(self, text):
        # unicode正規化と記号除去
        text = normalize('NFKC', text).lower()
        text = text.translate(self.noises).strip()

        # トークン化
        morphs = []
        for m in self.tokenizer_obj.tokenize(text, self.mode):
            if m.part_of_speech()[0] == '名詞' and m.part_of_speech()[1] != '数詞':
                morphs.append(m.surface())
        return " ".join(morphs)


    #
    # 文章データの行列を生成(各文章に対するベクトル一覧)
    #
    def get_matrix(self, text_series, mode='train'):
        text_series = text_series.map(self._preprocess)
        if mode == 'train':
            # 辞書作成と文章データの行列を作成
            bag = self.vectorizer.fit_transform(text_series)
        else:
            # 文章データの行列を作成 ※ 辞書はtrainでつくったものを使用
            bag = self.vectorizer.transform(text_series)

        return bag
```

この改善を実施した結果の評価は以下の通りとなっています。

```python
%%time
# 学習データに対する前処理
tp = TextPreprocessing()
bag = tp.get_matrix(train_df.text)
train_X = bag.toarray()
train_y = pd.Series(train_df.label)
```

```python
%%time
# 学習時間
from scipy.sparse import lil_matrix
from sklearn.linear_model import LogisticRegression

clf = LogisticRegression()
clf.fit(lil_matrix(train_X), train_y)
```

```python
# 正解率
bag_test = tp.get_matrix(test_df.text, mode='test')
test_X = bag_test.toarray()
test_y = pd.Series(test_df.label)
score = clf.score(lil_matrix(test_X), test_y)
print(score)
```

* 学習データに対する前処理の時間: 14.2s -> 13.3s
* 学習時間: 3.6s -> 2.93s
* 正解率: 0.8005427408412483 -> 0.7930800542740841

わずかですが、前処理や学習時間の短縮に成功しました。   
性能もやや劣化していますが、1%以内なので許容範囲とします。  


さらにストイックに語彙を減らしたい場合は、`CountVectorizer`の`max_features`を調整する手もあります。   
ちなみに、現状は、`max_features`はNoneであるため、学習データの中のすべての語彙が使用されている状態です。

語彙数は、`CountVectorizer`の`vocabulary_`をみればわかります。

```python
d = tp.vectorizer.vocabulary_
print(len(d)) # out -> 9463
```
語彙数は9463あることがわかりました。 (※ 実行環境により語彙数が異なる可能性があります。)
語彙数を減らせば学習時間を減らすことが期待できますが、正解率が低下するリスクがあります。
そこで、1000〜最大(9463)の範囲で正解率がどのくらい変化していくかみていきましょう。

まずは、前処理のクラスに`max_features`を指定できるように変更をいれます。

```python
from unicodedata import normalize
import string
from sudachipy import tokenizer
from sudachipy import dictionary

from sklearn.feature_extraction.text import CountVectorizer

#
# 前処理
#
class TextPreprocessing(object):
    def __init__(self, max_features=None):
        self.tokenizer_obj = dictionary.Dictionary().create()
        self.mode = tokenizer.Tokenizer.SplitMode.A
        punctuation = string.punctuation + '。、×÷ 【】『』 「」”“'
        self.noises = str.maketrans(
            {k: ' ' for k in normalize('NFKC', punctuation)})
        # max_featuresを追加
        self.vectorizer = CountVectorizer(max_features = max_features)


    #
    # ユニコード正規化を実施したうえで、トークン化を実施
    #
    def _preprocess(self, text):
        # unicode正規化とノイズ除去
        text = normalize('NFKC', text).lower()
        text = text.translate(self.noises).strip()

        # トークン化
        morphs = []
        for m in self.tokenizer_obj.tokenize(text, self.mode):
            if m.part_of_speech()[0] == '名詞' and m.part_of_speech()[1] != '数詞':
                morphs.append(m.surface())
        return " ".join(morphs)


    #
    # 文章データの行列を生成(各文章に対するベクトル一覧)
    #
    def get_matrix(self, text_series, mode='train'):
        text_series = text_series.map(self._preprocess)
        if mode == 'train':
            # 辞書作成と文章データの行列を作成
            bag = self.vectorizer.fit_transform(text_series)
        else:
            # 文章データの行列を作成 ※ 辞書はtrainでつくったものを使用
            bag = self.vectorizer.transform(text_series)

        return bag
```

語彙数をいくつにするか決定するために、1000きざみで正解率の変化をみていきます。

```python
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt

candidate = list(range(1000, 11000, 1000))
clf = LogisticRegression()
scores = []
for max_features in candidate:
    tp = TextPreprocessing(max_features=max_features)
    bag = tp.get_matrix(train_df.text)
    train_X = bag.toarray()
    train_y = pd.Series(train_df.label)
    clf.fit(lil_matrix(train_X), train_y)

    bag_test = tp.get_matrix(test_df.text, mode='test')
    test_X = bag_test.toarray()
    test_y = pd.Series(test_df.label)
    scores.append(clf.score(lil_matrix(test_X), test_y))

plt.plot(candidate, scores, label='socre')
plt.legend()
```

グラフを見ると語彙数が4000件で頭打ちになっていることがわかります。

![](https://storage.googleapis.com/zenn-user-upload/4a6y6bbplo94uw4p9sblbqamo2f3)

よって、`max_features`は4000件として、再評価します。  

```python
%%time
# 学習データに対する前処理
tp = TextPreprocessing(max_features=4000)
bag = tp.get_matrix(train_df.text)
train_X = bag.toarray()
train_y = pd.Series(train_df.label)
```

```python
%%time
# 学習時間
from scipy.sparse import lil_matrix
from sklearn.linear_model import LogisticRegression

clf = LogisticRegression()
clf.fit(lil_matrix(train_X), train_y)
```

```python
# 正解率
bag_test = tp.get_matrix(test_df.text, mode='test')
test_X = bag_test.toarray()
test_y = pd.Series(test_df.label)
score = clf.score(lil_matrix(test_X), test_y)
print(score)
```

* 学習データに対する前処理の時間: 13.3s -> 13.8s
* 学習時間: 2.93s -> 1.7s
* 正解率: 0.7930800542740841 -> 0.7991858887381276

前処理の処理時間が若干上昇しましたが、学習時間は削減できており、   
トータルでみると処理時間が短縮できていることがわかります。   
前処理の処理時間が増えた理由は、`CountVectorizer`に`max_features`を指定したことで、   
語彙の選定コストが増えたためと思われます。  

## 高速化テクニック3: 学習回数を減らす

最後に、ハイパーパラメータで学習回数を減らします。 
ここでも、**性能に極力影響を及ばさない**程度に調整することが重要です。  

ロジスティック回帰の場合、max_iterが学習回数を制御するパラメーターになります。   
max_iterの値(デフォルト100)を小さくすれば、高速化できる可能性があります。 

max_iterの値を10きざみで変化をみていきます。  


```python
import matplotlib.pyplot as plt

iter_candidate = [30, 40, 50, 60, 70, 80]
scores = []
train_X=lil_matrix(train_X)
test_X=lil_matrix(test_X)

for iter in iter_candidate:
    clf = LogisticRegression(max_iter=iter)
    clf.fit(train_X, train_y)
    scores.append(clf.score(test_X, test_y))

plt.plot(iter_candidate, scores, label='score')
plt.legend()
```

![](https://storage.googleapis.com/zenn-user-upload/p03ck40mijw9lg9jl2cojnnd7xtp)

グラフを見る限り、50付近で頭打ちしそうです。  
よって、max_iter=50とします。   

評価をまとめると、以下のとおりです。

```python
%%time
# 学習時間
from scipy.sparse import lil_matrix
from sklearn.linear_model import LogisticRegression

clf = LogisticRegression(max_iter=50) # max_iterを100->50に変更
clf.fit(lil_matrix(train_X), train_y)
```

```python
# 正解率
bag_test = tp.get_matrix(test_df.text, mode='test')
test_X = bag_test.toarray()
test_y = pd.Series(test_df.label)
score = clf.score(lil_matrix(test_X), test_y)
print(score)
```

* 学習データに対する前処理の時間(処理内容に変更なし): 13.8s -> 13.8s
* 学習時間: 1.7s -> 1.15s
* 正解率: 0.7991858887381276 -> 0.7998643147896879

## まとめ

機械学習モデルの処理改善として、3つのテクニックを紹介しました。 
最終評価として、ベースラインに対して以下の成果を得ることができました。　

* 学習データに対する前処理の時間(処理内容に変更なし): 14.2s -> 13.8s
* 学習時間: 82s -> 1.15s
* 正解率: 0.8005427408412483-> 0.7998643147896879

処理の高速化のみを評価していますが、スパース行列の利用や前処理の改善は、メモリ使用量の改善にもつながっています。    

機械学習というとモデル性能の改善がとにかく大事とおもわれがちです。  
しかし、開発においては、処理の高速化やリソース削減が課題になることもしばしばです。    

高速化やリソース削減のヒントになれば、幸いです。 

おわりです。 
