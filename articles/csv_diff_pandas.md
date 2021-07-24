---
title: "Pandasでcsvファイルの差分比較"
emoji: "🐼"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Python", "pandas", "csv", "DataFrame", "データ分析"]
published: true
---

こんにちは。ヤギユキ([@yagiyuki06](https://twitter.com/yagiyuki06))です。
今回は、pandasを使った2つのcsvファイルの比較方法をまとめました。

pandasを使ったファイル比較は、pythonの標準関数を使うよりかなりコードを省略できます。
ぜひ、参考にしてみてください。

## 基本

おおまかな比較の流れは以下のとおりです。

* 比較する2つのcsvをDataFrameへロード
* 2つのDataFrameを比較

`key,val`をヘッダーに持つ、以下2つのcsvを例にして比較してみます。

```bash
cat <<EOF > test1.csv
key,val
string1,1
string2,2
string3,3
string4,4
string5,5
EOF
```

```bash
cat <<EOF > test2.csv
key,val
string1,1
string2,2
string3,3
string4,-1
string5,5
EOF
```

差分があるのは、4行目ののvalのみです。
2つのcsvをpandasのDataFrameへロードします。

```python
df_1 = pd.read_csv('test1.csv')
df_2 = pd.read_csv('test2.csv')

print(df_1)
print(df_2)
```

```
       key  val
0  string1    1
1  string2    2
2  string3    3
3  string4    4
4  string5    5
       key  val
0  string1    1
1  string2    2
2  string3    3
3  string4   -1
4  string5    5
```

2つのDataFrameを比較します。

### 方法1: 全レコードを比較結果を出力

```python
print(df_1 == df_2)
```

```
  key    val
0  True   True
1  True   True
2  True   True
3  True  False
4  True   True
```

### 方法2: 差分があったレコードのみを出力

```python
print(df_1[(df_1 == df_2).all(axis=1) == False])
```

差分があったdf_1のレコードを出力しています。
```
       key  val
3  string4    4
```

### 方法3: 差分があったフィールドのみを出力

```python
print(df_1.compare(df_2))
```

```
   val      
  self other
3  4.0  -1.0
```

`self`がdf_1のval、`other`がdf_2のvalになります。

## sortしてから比較

データによっては順不同であることもあるでしょう。
そういった順不同なデータについては、事前にsortしてから比較するのが有効です。

```
%%bash

cat <<EOF > test1.csv
key,val
string2,2
string3,3
string4,4
string5,5
string1,1
EOF

cat <<EOF > test2.csv
key,val
string1,1
string2,2
string4,-1
string5,5
string3,3
EOF
```

先程同様、差分があるのは、`key=string4`のデータのみです。
しかし、順番が異なるため、以下の通り差分レコードが検出されます。
```
df_1 = pd.read_csv('test1.csv')
df_2 = pd.read_csv('test2.csv')

print(df_1[(df_1 == df_2).all(axis=1) == False])
```
```
       key  val
0  string2    2
1  string3    3
2  string4    4
4  string1    1
```

こういったデータは、事前にsortするとよいです。

```python
# keyカラムでソート
df_1 = pd.read_csv('test1.csv').sort_values('key')
df_2 = pd.read_csv('test2.csv').sort_values('key')

# indexを再設定しないとエラーになる
df_1.reset_index(drop=True, inplace=True)
df_2.reset_index(drop=True, inplace=True)

print(df_1[(df_1 == df_2).all(axis=1) == False])
```

```
       key  val
3  string4    4
```

## 共通部分だけ比較

```
%%bash

cat <<EOF > test1.csv
key,val
string2,2
string3,3
string4,4
string5,5
string1,1
EOF


cat <<EOF > test2.csv
key,val
string1,1
string2,2
string4,-1
string5,5
string3,3
string6,6
EOF
```

前の`test2.csv`に対して、`string6`を追加しました。
この状態で比較すると、2つのcsvのレコード数が異なるため、エラーになります。

```python
print(df_1[(df_1 == df_2).all(axis=1) == False])
```

```
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
<ipython-input-51-3e12f0372c88> in <module>()
----> 1 print(df_1[(df_1 == df_2).all(axis=1) == False])

1 frames
/usr/local/lib/python3.7/dist-packages/pandas/core/ops/__init__.py in _align_method_FRAME(left, right, axis, flex, level)
    509             else:
    510                 raise ValueError(
--> 511                     "Can only compare identically-labeled DataFrame objects"
    512                 )
    513     elif isinstance(right, ABCSeries):

ValueError: Can only compare identically-labeled DataFrame objects
```

こういったcsvにおいて、keyが共通部分だけ比較する方法をかきます。

```python
# test1.csv, test2.csvの2つのkeyを一覧を取得する
l1 = list(df_1.key.values)
l2 = list(df_2.key.values)

# 2つのkeyの共通を取得する
l1_l2_and = sorted(list(set(l1) & set(l2)))
print(l1_l2_and)　# out -> ['string1', 'string2', 'string3', 'string4', 'string5']

# 共通するキーのレコードを取得
df_1 = df_1.query('key in {}'.format(l1_l2_and))
df_2 = df_2.query('key in {}'.format(l1_l2_and))

# indexを再設定
df_1.reset_index(inplace=True, drop=True)
df_2.reset_index(inplace=True, drop=True)

# 比較
print(df_1[(df_1 == df_2).all(axis=1) == False])
```

```
       key  val
3  string4    4
```

以上です。




