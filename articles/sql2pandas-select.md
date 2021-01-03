---
title: "sqlからpandasを逆引き(SELECT編)"
emoji: "🐼"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["python", "機械学習"]
published: false
---

こんにちは。ヤギユキ([@yagiyuki06](https://twitter.com/yagiyuki06))です。

SQLのクエリから、Pandas のメソッドを逆引きする情報を作成しました。
SQLは知っているけど、Pandasはあまり知らないエンジニアのための情報です。

今回は、SQLのSELECT文をターゲットとします。

## 列選択

```sql
SELECT COL1, COL2
FROM TABLE;
```

```python
df.loc[:, ["COL1", "COL2"]]
```

## 条件指定(WHERE)

条件指定は、queryメソッドを使います。
https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html

:::message
条件指定は、queryを使わない記法もあります。
好みはありますが、queryメソッドのほうが直感的に書けるという利点があります。

```python
# queryを使う場合
df.query('COL1 == "hoge" and COL2 != "huga"')

# queryを使わない場合
df[(df["COL1"]=="hoge") & (df["COL2"] != "huga")]
```
:::

### 一致

```sql
SELECT *
FROM TABLE
WHERE COL = 'hoge';
```

```python
df.query('COL == "hoge"')
# クオテーションに注意
```

### 不一致

```sql
SELECT *
FROM TABLE
WHERE COL <> 'hoge';
```

```python
df.query('COL != "hoge"')
```

### 大小比較


```sql
SELECT *
FROM TABLE
WHERE COL1 > 1000;
```

```python
df.query('COL1 > 1000')
```

### 複合条件(または)

```sql
SELECT *
FROM TABLE
WHERE COL1 == 'hoge' OR COL2 <> 'huga';
```

```python
df.query('COL1 == "hoge" or COL2 != "huga"')
```

### 複合条件(かつ)

```sql
SELECT *
FROM TABLE
WHERE COL1 == 'hoge' AND COL2 <> 'huga';
```

```python
df.query('COL1 == "hoge" AND COL2 != "huga"')
```

### 含む

```sql
SELECT *
FROM TABLE
WHERE COL IN (1, 2, 3)';
```

```python
df.query('COL in (1, 2, 3)')
```

### 含まれない

```sql
SELECT *
FROM TABLE
WHERE COL NOT IN  (1, 2, 3)';
```

```python
df.query('COL not in (1, 2, 3)')
```

### 範囲

```sql
SELECT *
FROM TABLE
WHERE COL BETWEEN 1000 AND 2000;
```

```python
df.query('COL >= 1000 and date <= 2000')
# pandasのqueryには、betweenという記法はない。
```

### パターンマッチング(前方)

```sql
SELECT *
FROM TABLE
WHERE NAMEL LIKE '中%';
-- 中で始まる名前の行を抽出 例: 中田
```

```python
df.query('item.str.startswith("田")', engine='python')
```

### パターンマッチング(後方)

```sql
SELECT *
FROM TABLE
WHERE NAMEL LIKE '%中';
-- 中で終わる名前の行を抽出 例: 田中
```

```python
df.query('item.str.endswith("田")', engine='python')
```

### パターンマッチング(部分)

```sql
SELECT *
FROM TABLE
WHERE NAMEL LIKE '%中%';
-- 中を含む名前の行を抽出 例: 中田、田中、三田村
```

```python
df.query('item.str.contains("田")', engine='python')
```

## ソート(ORDER BY)

### 昇順

```sql
SELECT *
FROM TABLE
ORDER BY COL ASC;
```

```python
df.sort_values(by=['COL'], ascending=True)
```

### 降順

```sql
SELECT *
FROM TABLE
ORDER BY COL DESC;
```

```python
df.sort_values(by=['COL'], ascending=False)
```

## 重複削除(DISTINCT)

```sql
SELECT DISTINCT COL1, COL2
FROM TABLE
-- COL1の重複を削除して、COL1とCOL2を選択
```

```python
df[~df.duplicated(subset=['COL1'])].loc[:, ["COL1", "COL2"]]
```

## 集合関数(SUM,MAX,MIN,AVG,COUNT)

```sql
SELECT SUM(COL),MAX(COL),MIN(COL),AVG(COL),COUNT(COL)
FROM TABLE
```

```python
df['COL'].sum() # sum by sql
df['COL'].min() # min by sql
df['COL'].max() # max by sql
df['COL'].mean() # avg by sql
len(df) # count by sql
```

## グループ化(GROUP BY)

グループ化は、groupbyメソッドを使います。
https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html


```sql
SELECT COL1, AVG(COL2)
FROM TABLE
GROUP BY COL1;
```

```python
df_mean=df.groupby("COL1").mean()
df_mean.loc[:, ["COL2"]]
```

## グループ化の検索(HAVING)


```sql
SELECT COL1, AVG(COL2)
FROM TABLE
GROUP BY COL1
HAVING AVG(COL2) > 1000
```

```python
df_mean=df.groupby("COL1").mean()
df_mean.query("COL2 > 1000").loc[:, ["COL2"]]
```


