---
title: "pythonでcsv処理の速度比較"
emoji: "🔖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Python", "pandas", "numpy"]
published: true
---

こんにちは。ヤギユキ([@yagiyuki06](https://twitter.com/yagiyuki06))です。
今回は、pythonのcsvファイルの読み込み・書き込み速度を比較しました。

比較手法は以下の3つです。

* 標準関数のみ
* csvモジュール
* pandas

実行環境は、[Google Colaboratory](https://colab.research.google.com/?hl=ja)でGPUは使わずに検証してます。 
結果は最後のまとめに書いてあります。

## 下準備

まず検証用のcsvファイルを作成します。

```python
# csvの行数　100万件
N=1000000
# N×5のcsvファイルを作成
with open('input.csv', 'w') as f:
    for i in range(N):
        l = []
        for j in range(5):
            s = '{}_{}'.format(i, j)
            l.append(s)
        f.write(",".join(l) + '\n')
```

## 標準関数のみ

### 読み込み

```python
%%time

out_l = []

with open('input.csv') as in_f:
    for s in in_f:
        row = s.strip().split(',')
        out_l.append(row)
```
```
CPU times: user 1.79 s, sys: 275 ms, total: 2.06 s
Wall time: 1.99 s
```


### 書き込み

```python
%%time

with open('output.csv', 'w') as out_f:
    for row in out_l:
        out_f.write(",".join(row) + '\n')
```
```
CPU times: user 452 ms, sys: 60.1 ms, total: 512 ms
Wall time: 516 ms
```

## csvモジュール

### 読み込み

```python
%%time

with open('input.csv') as csvfile:
    reader = csv.reader(csvfile)
    out_l = [row for row in reader]
```
```
CPU times: user 1.76 s, sys: 256 ms, total: 2.01 s
Wall time: 1.97 s
```

### 書き込み

```python
%%time

with open('output.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in out_l:
        writer.writerow(row)
```
```
CPU times: user 1.31 s, sys: 66.8 ms, total: 1.37 s
Wall time: 1.38 s
```

## pandas

### 読み込み

```python
%%time

df = pd.read_csv('input.csv', delimiter=',', names=[str(i) for i in range(5)])
```
```
CPU times: user 2.33 s, sys: 192 ms, total: 2.52 s
Wall time: 2.51 s
```

### 書き込み

```python
%%time

df.to_csv('output.csv', index=False, header=False)
```
```
CPU times: user 2.2 s, sys: 81.8 ms, total: 2.28 s
Wall time: 2.29 s
```

## まとめ

結果をまとめると以下のようになりました。

|             | 標準関数のみ | csvモジュール | pandas | 
| ----------- | ------------------- | ------------------- | ------------------- | 
| 読み込み    | 1.99 s               | 1.97 s              | 2.51s                 | 
| 書き込み    | 516 ms               | 1.38 s              | 2.29s                 | 

処理速度を優先するなら標準関数を使うのが良さそうです。

読み込み・書き込みともにpandasが一番遅いという結果になりました。
高機能であるがゆえに処理速度はどうしても落ちるようです。
高い処理速度が求められるシステムであれば、使わないほうがよいかもしれないですね。

以上です。
