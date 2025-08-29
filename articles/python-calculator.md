---
title: "Pythonで数値を3桁カンマ区切り表示する方法【対話モードで自動反映】"
emoji: "🔢"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["python", "tips"]
published: true
---

突然ですが、Pythonの対話モードを電卓代わりに使っていますか？
Pythonの対話モードでの計算は非常に直感的であり、ちょっと複雑な計算をするときに便利です。

```python
$ python
Python 3.10.0 (default, Apr 14 2024, 11:30:24) [Clang 12.0.0 (clang-1200.0.32.29)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> 3+3*2
9
```

しかし難点もあり桁数の大きな数字を扱うとき、コンマ区切りで表示されないため視認性が悪いという点です。

```python
>>> 1234567890 * 9876
12193263111240  # どこで区切る？一瞬で理解しづらい
```

理想的には3桁区切りで表示したいと思い方法を調べてみました。
調べたところ、Pythonの対話モード起動時に決まった処理を実行する仕組み（PYTHONSTARTUP）を利用すれば解決できそうでした。

この記事のまとめでも触れますが、この機能を使えば、日常のPythonの動作確認をもっと便利にできそうだなと思いました。ぜひ参考にしてみてください。

## 結論の前に:よくある解決方法

検索してみると、たいていはPythonのフォーマット機能を使った手法がよく出てきます。

```python
>>> n = 1234567890 * 9876
>>> f"{n:,}"
'12,193,263,111,240'
>>> f"{n:_}"
'12_193_263_111_240'
```

しかしライトに電卓として利用したい場合、「毎回 f文字列でラップするのは面倒」 です。

## PYTHONSTARTUPを利用した方法

Pythonは対話モードは起動時に [PYTHONSTARTUP](https://docs.python.org/ja/3.10/using/cmdline.html#envvar-PYTHONSTARTUP) で指定したスクリプトを読み込むことができます。

下記のステップを踏むことで、3桁区切りで計算結果を表示することが可能です。

1.	~/.pystartup.py に3桁区切りで表示するための処理を実装
2.	python対話モード起動時に ~/.pystartup.py をロード


### 1.	~/.pystartup.py に3桁区切りで表示するための処理を実装

```python
# ~/.pystartup.py
# 目的:
# - Pythonの対話モードで、評価結果の表示だけを自動で「区切り入り」にする
# - 値そのものは変えず、演算にも影響しない

import sys, builtins  # sys: displayhook設定 / builtins: 直前結果(_)の維持に使用

# 区切り文字を選択（'_' or ',' or ' '）
_SEP = '_'

def _pretty_display(v):
    """
    Python対話モードの表示フック(displayhook)として呼ばれる関数。
    v: 評価された直後のオブジェクト(式の結果)
    """
    if v is None:
        # 代入文など結果が None の時は何も表示しない（通常の挙動に合わせる）
        return

    # 直前の結果を builtins._ に保存する（通常のREPLの便利機能を壊さない）
    builtins._ = v

    # 整数は3桁区切り化 → 任意の区切り文字に置換
    if isinstance(v, int):
        print(format(v, ",").replace(",", _SEP))
        return

    # 浮動小数は有効桁数12桁 + 3桁区切り
    if isinstance(v, float):
        s = f"{v:,.12g}".replace(",", _SEP)
        print(s)
        return

    # それ以外（リストや辞書など）は通常表示
    print(repr(v))

# 対話モードの出力フェーズを差し替え
sys.displayhook = _pretty_display
```

### 2.	python対話モード起動時に ~/.pystartup.py をロード

起動時に `~/.pystartup.py` を読み込ませるために、シェルの設定ファイルに環境変数を追記します。

```bash
echo 'export PYTHONSTARTUP="$HOME/.pystartup.py"' >> ~/.zshrc
source ~/.zshrc
```

## 動作の確認

設定を反映すると、計算結果が次のように区切り付きで表示されます。

```python
Python 3.10.0 (default, Apr 14 2024, 11:30:24) [Clang 12.0.0 (clang-1200.0.32.29)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> 1234567890 * 9876
12,192,592,481,640
>>> 1234567.89 * 98765.4321
121,932,631,113
>>> _
121,932,631,113
```

対話モード以外では、PYTHONSTARTUPでの実装内容が反映されないため、3桁区切りにはなりません！

```bash
$ python -c "print(1234567890 * 9876)"
12192592481640
```

## まとめ

今回は、PYTHONSTARTUPを使ってPythonでの計算結果を見やすくする方法を紹介しました。
PYTHONSTARTUPは起動時に処理を実行できるので、工夫次第で対話モードをさらに便利にできます。

例えば、よく使うimportはあらかじめ実装しておくなどすると少しだけ生産性が上がりそうです。

```python
# 例えばこんな感じで普段よく使うライブラリを仕込んでおくことができます
import math
import datetime
```

便利だなと思った方はぜひ参考にしてみてください。
