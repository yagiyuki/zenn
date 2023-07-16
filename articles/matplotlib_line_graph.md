---
title: "Matplotlibで折れ線グラフを描く：チートシート"
emoji: "📈"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["python", "matplotlib", "可視化"]
published: true
---

Pythonのデータ視覚化ライブラリであるMatplotlibは、データ分析者や研究者に広く利用されています。その主要な理由として、高度にカスタマイズ可能なプロットを容易に作成できる点が挙げられます。この記事では、PythonとMatplotlibを使用して基本的な折れ線グラフを作成する方法を解説します。

この記事で解説しているコードは、[plt_line_graph.ipynb](https://github.com/yagiyuki/zenn/blob/main/python/plt_line_graph.ipynb)から参照できます。
以下の環境で動作確認済みです。
```
Python 3.8.16
matplotlib==3.7.2
```

## 環境設定

Matplotlibは、以下のコマンドでインストールできます。

```bash
pip install matplotlib
```

## 基本のキ

基本的な折れ線グラフを描くために、最初に必要なのはデータです。
Pythonのリストを使用して簡単なデータセットを作成しましょう。

```python
data = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
```

このデータセットを使用して、Matplotlibで最初の折れ線グラフを作成しましょう。

```python
import matplotlib.pyplot as plt

plt.plot(data)
plt.show()
```

![](https://storage.googleapis.com/zenn-user-upload/302fafbb5173-20230716.png)

`plt.plot()`関数は折れ線グラフを描画し、`plt.show()`関数は描画したグラフを表示します。

## タイトルとラベルの設定

Matplotlibの強力な機能のひとつは、グラフのカスタマイズです。
例えば、グラフにタイトルを追加したり、x軸とy軸にラベルを設定したりできます。

```python
plt.plot(data)
plt.title('My First Graph')
plt.xlabel('X-Axis')
plt.ylabel('Y-Axis')
plt.show()
```

![](https://storage.googleapis.com/zenn-user-upload/4659a7f03b8e-20230716.png)

## マーカーの使用

データポイントを強調するためにマーカーを使用できます。
マーカーの形状や色など、さまざまなスタイルをカスタマイズすることが可能です。

```python
plt.plot(data, marker='o', color='red')
plt.title('My First Graph')
plt.xlabel('X-Axis')
plt.ylabel('Y-Axis')
plt.show()
```

![](https://storage.googleapis.com/zenn-user-upload/a7acc7a5019f-20230716.png)

## 複数のグラフの作成

複数のグラフを同時に表示するには、`subplots()`関数を使用します。
例えば、2x2のレイアウトで4つの折れ線グラフを作成するには以下のようにします。

```python
data1 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
data2 = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
data3 = [0.3, 0.5, 0.1, 0.9, 0.7, 0.4, 0.6, 0.2, 0.8, 1.0]
data4 = [0.5, 0.6, 0.8, 0.4, 0.2, 0.9, 0.1, 0.7, 0.3, 1.0]

fig, axs = plt.subplots(2, 2, figsize=(10, 10))

data_sets = [data1, data2, data3, data4]
for i, ax in enumerate(axs.flat):
    ax.plot(data_sets[i], marker='o')
    ax.set_title(f'Graph {i+1}')

plt.tight_layout()
plt.show()
```
![](https://storage.googleapis.com/zenn-user-upload/7641211d1d69-20230716.png)

## データポイントにテキストを追加

折れ線グラフのデータポイントにテキストを追加することも可能です。
この機能を使用すれば、データポイントに注釈を付けたり、データの詳細を表示できます。

```python
fig, axs = plt.subplots(2, 2, figsize=(10, 10))

data_sets = [data1, data2, data3, data4]
for i, ax in enumerate(axs.flat):
    ax.plot(data_sets[i], marker='o')
    ax.set_title(f'Graph {i+1}')
    
    for j, y in enumerate(data_sets[i]):
        ax.text(j, y+0.05, f'P{j+1}', color='red', fontsize=12, ha='center', va='bottom')

plt.tight_layout()
plt.show()
```

![](https://storage.googleapis.com/zenn-user-upload/d0a3c6f9651d-20230716.png)

## 複数のデータセットの描画

さらに進んで、複数のデータセットを同じグラフに描画することも可能です。
この場合、異なるデータセットを区別するために、それぞれのプロットにラベルを付け、凡例を表示します。

```python
data1 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
data2 = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]

plt.plot(data1, marker='o', color='red', label='Data1')
plt.plot(data2, marker='o', color='blue', label='Data2')

plt.title('My Second Graph')
plt.xlabel('X-Axis')
plt.ylabel('Y-Axis')
plt.legend(loc='upper right')

plt.show()
```

ここでは`label`パラメータを使用して各プロットにラベルを付け、`plt.legend()`関数を使用して凡例を表示しています。`loc`パラメータで凡例の位置を設定することができます。

![](https://storage.googleapis.com/zenn-user-upload/5c240025667d-20230716.png)

## グラフのスタイル

Matplotlibでは、グラフのスタイルを全体的に変更することもできます。これは`style`モジュールを使用して行います。例えば、以下のコードでは`ggplot`スタイルを適用しています。

```python
plt.style.use('ggplot')

plt.plot(data1, marker='o', color='blue', label='Data1')
plt.plot(data2, marker='o', color='green', label='Data2')

plt.title('My Third Graph')
plt.xlabel('X-Axis')
plt.ylabel('Y-Axis')
plt.legend(loc='upper right')

plt.show()
```

![](https://storage.googleapis.com/zenn-user-upload/997181f3dafe-20230716.png)

## まとめ

この記事では、PythonのMatplotlibライブラリを使用して基本的な折れ線グラフを作成する方法を解説しました。
このあたりの知識があれば、折れ線グラフを使った可視化スキルとしては、最低限のものが身についた状態になっていると思います。
お役に立てれば幸いです。



