---
title: "sqlからpandasを逆引き(select編)"
emoji: "🐼"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["python", "機械学習"]
published: false
---

こんにちは。ヤギユキ([@yagiyuki06](https://twitter.com/yagiyuki06))です。

SQL のクエリから、Pandas のメソッドを逆引きする情報を作成しました。
SQLは知っているけど、Pandasはあまり知らないエンジニアのための情報です。

今回は、SQLのselect文をターゲットとします。

## 列選択

```sql
SELECT COL1, COL2
FROM TABLE;
```

```python
df.loc[:, ["COL1", "COL2"]]
```


## 条件指定

条件指定は、query
TODO: コラム queryを使わない方法

### 一致

```sql
SELECT *
from TABLE
where COL1 = 'hoge';
```

```python
df.query('COL1 == "hoge"')
```

Pandasは、クオテーションに注意

### 不一致

```sql
SELECT *
from TABLE
where COL1 <> 'hoge';
```

```python
df.query('COL1 != "hoge"')
```

### 大小比較

1000より大きい
```sql
SELECT *
FROM TABLE
WHERE COL1 > 1000;
```

```python
df.query('COL1 > 1000')
```

1000以下
```sql
SELECT *
FROM TABLE
WHERE COL1 <= 1000;
```

```python
df.query('COL1 <= 1000')
```

### 複合条件(or)

```sql
SELECT *
FROM TABLE
WHERE COL1 == 'hoge' OR COL2 <> 'huga';
```

```python
df.query('COL1 == "hoge" or COL2 != "huga"')
```

### 複合条件 (and)

```sql
SELECT *
FROM TABLE
WHERE COL1 == 'hoge' AND COL2 <> 'huga';
```

```python
df.query('COL1 == "hoge" AND COL2 != "huga"')
```

### 含む

SELECT *
FROM TABLE
WHERE COL in (1, 2, 3)';
```

```python
df.query('COL in (1, 2, 3)')
```

### 含まれない

```sql
SELECT *
FROM TABLE
WHERE COL not in (1, 2, 3)';
```

```python
df.query('COL not in (1, 2, 3)')
```

### 範囲

```sql
select *
from TABLE
where COL between 1000 and 2000;
```

```python
df.query('COL >= 1000 and date <= 2000')
# pandasのqueryには、betweenという記法はない。
```

### パターンマッチング(前方)

```sql
select *
from TABLE
where NAMEL like '中%';
-- 中で始まる名前の行を抽出 例: 中田
```

```python
df.query('item.str.startswith("田")', engine='python')
```

### パターンマッチング(後方)

```sql
select *
from TABLE
where NAMEL like '%中';
-- 中で終わる名前の行を抽出 例: 田中
```

```python
df.query('item.str.endswith("田")', engine='python')
```

### パターンマッチング(部分)

```sql
select *
from TABLE
where NAMEL like '%中%';
-- 中を含む名前の行を抽出 例: 中田、田中、三田村
```

```python
df.query('item.str.contains("田")', engine='python')
```

## ソート

### 昇順

```sql
select *
from TABLE
order by COL asc;
```

```oython
df.sort_values(by=['COL'], ascending=True)
```

### 降順

```sql
select *
from TABLE
order by COL desc;
```

```oython
df.sort_values(by=['COL'], ascending=False)
```

## 重複削除

```sql
SELECT DISTINCT COL1, COL2
FROM TABLE
-- COL1の重複を削除して、COL1とCOL2を選択
```

```python
df[~df.duplicated(subset=['COL1'])].loc[:, ["COL1", "COL2"]]
```

