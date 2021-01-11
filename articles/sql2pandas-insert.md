---
title: "sqlからpandasを逆引き(INSERT編)"
emoji: "🐼"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["python", "機械学習", "SQL"]
published: true
---

こんにちは。ヤギユキ([@yagiyuki06](https://twitter.com/yagiyuki06))です。

SQLのクエリから、Pandas のメソッドを逆引きする情報を作成しました。
SQLは知っているけど、Pandasはあまり知らないエンジニアのための情報です。

今回は、SQLのINSERT文をターゲットとします。

前回は、SELECT編の記事を書いたので、よろしければこちらもどうぞ。  
https://zenn.dev/yagiyuki/articles/sql2pandas-select

## 単一レコード追加

レコード追加は、appendメソッドを使います。
https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.append.html

単一のレコードを追加する例です。 

> SQL
```SQL
-- カラムCOL1にA1、COL2にB1を追加
INSERT into tbl (COL1, COL2) values ('A1', 'B1');
```
 
> python
```python
s = pd.Series(['A1', 'B2'], index=['COL1', 'COL2']) # 複数レコードと同様にDataFrameでも可
df.append(s, ignore_index=True)
```

## 複数レコード追加

複数レコードを追加する例です。 

> SQL

```SQL
-- カラムCOL1,COL2に3つのレコード ('A1', 'B1'), ('A2', 'B2'), ('A3', 'B3') を追加
INSERT into tbl (COL1, COL2) values ('A1', 'B1'), ('A2', 'B2'), ('A3', 'B3');
```

> python
```python
df2 = pd.DataFrame([['A1', 'B1'], ['A2', 'B2'], ['A3', 'B3']], 
                   columns=['COL1', 'COL2'])
df.append(df2, ignore_index=True)
```

:::message
**ignore_indexって何?**

pandasのdataframeには列を追加した順にindexが振られています。
ignore_indexをTrueにすることで、既存のindexを無視して、振り直す処理が走ります。 

```python
import pandas as pd

df = pd.DataFrame([['A0', 'B0']],
                    columns=['COL1', 'COL2'])

df2 = pd.DataFrame([['A1', 'B1'], ['A2', 'B2'], ['A3', 'B3']],
                    columns=['COL1', 'COL2'])
print(df)
# COL1 COL2
# 0   A0   B0
print(df2)
# COL1 COL2
#0   A1   B1
#1   A2   B2
#2   A3   B3

# df, df2の既存のindexがそのまま振られ、index0が重複する
print(df.append(df2)) 
# COL1 COL2
#0   A0   B0
#0   A1   B1
#1   A2   B2
#2   A3   B3

# df, df2の既存のindexのが無視され、新しいindexが振り直される
print(df.append(df2, ignore_index=True))
#  COL1 COL2
#0   A0   B0
#1   A1   B1
#2   A2   B2
#3   A3   B3

```
:::


## SELECT結果をINSERT

別テーブルから選択したレコードを、追加する例です。

> SQL
```SQL
-- tbl2でA1にマッチするレコードをtblに追加する
INSERT INTO tbl SELECT * FROM tbl2 WHERE COL1 = 'A1'
```

> python
```python
df.append(df2.query('COL1=="A1"'), ignore_index=True)
```

