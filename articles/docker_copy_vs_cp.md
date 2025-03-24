---
title: "dockerfileのCOPYでゴミファイルが入るのを防ぐ"
emoji: "🕌"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Docker", "Linux"]
published: false
---

Dockefileの`COPY`命令を使う際にゴミデータを一緒にコピーしてしまうという問題の回避策をまとめます。

## DockerfileのCOPYの簡単な説明

COPYはホスト環境のデータをdockerイメージにコピーする記法です。

```dockerfile
FROM python:alpine3.18

# ホスト環境file.pyをdockerイメージにコピー
COPY file.py /home/

WORKDIR /home
```

ファイルでなくディレクトリをコピーすることもできます。

```dockerfile
FROM python:alpine3.18

# ホスト環境のscriptsディレクトリをdockerイメージの/home/scriptsへコピー
COPY scripts /home/scripts/

WORKDIR /home
```

## ゴミデータが交じるケース

ディレクトリをコピーするときにディレクトリの中にうっかりゴミが混じっている場合、イメージの中にもゴミが入ってしまいます。
例として、scriptsの中にpythonが入っている場合だと(`__pycache__`)[https://peps.python.org/pep-3147/#proposal]が入ってしまうことがあります。
また、Macで開発している人は[`.DS_Store`](https://en.wikipedia.org/wiki/.DS_Store)が入ることもあるでしょう。

ゴミデータを入れないようにする方法を2つ書きます。

## 方法1: Dockerfileにコピー対象ファイルを明確に書く

ディレクトリをコピーするのでなく、コピー対象のファイルを明確に書くという方法があります。

```dockerfile
FROM python:alpine3.18

# ホスト環境のscriptsにあるpyファイルをdockerイメージの/home/scripts/へコピー
COPY scripts/*py /home/scripts/

WORKDIR /home
```

:::message alert

COPY命令を以下のように書いてしまうと正常に動作しません。

```dockerfile
# !! /home/scripts/ でなく /home/scripts にすると scriptsがファイル扱いされる
COPY scripts/*py /home/scripts
```

上記のように書いてしまうと、`scripts/*py`に該当するファイルのうち名前順が後ろのファイルが、`scripts`という名前のファイルにコピーされてしまいます。

以下の例だとfile2.pyがscriptsという名前のファイルにコピーされます。
```
scripts/
├── file.py
└── file2.py
```

:::

## 方法2: .dockerignoreを使う

Dockerfileを下記のように記載したうえで、`.dockerignore`というファイルを作ることで、ゴミデータをコピー対象から外すことができます。

* Dcokefile
```dockerfile
FROM python:alpine3.18

# ホスト環境のscriptsディレクトリをdockerイメージの/home/scriptsへコピー
COPY scripts /home/scripts/

WORKDIR /home
```

* .dockerignore 
```
scripts/__pycache__
scripts/.DS_Store
```

このように書けば、scriptsの中の`__pycache__`と`.DS_Store`を外すことができます。
`.dockerignore`というファイルは、Dockerfileと同じ階層に作ります。

また以下のように`.dockerignore`を書けばより汎用的に対処できます。

```
# binディレクトリのコピー対象をpyファイル限定にする
scripts
!scripts/*py
```

このようにすれば、`__pycache__`と`.DS_Store`以外のゴミデータが`scripts`の中に混じっていてもコピー対象から外すことができます。


## まとめ

Dockefileの命令に`COPY`命令時にゴミデータをいれないよにする方法をまとめました。
方法1と方法2のどちらがよいかはケースにもよると思います。






