---
title: "Transformersの'from_pretrained'の使い方とリスクを考察"
emoji: "⚡"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Python", "機械学習", "transformer"]
published: true
---

Transformersの事前学習済みのモデルのロード処理で、こんなコードをよく見かけませんか?

```python
from transformers import HogeModel
hoge_model = HogeModel.from_pretrained('hoge_model_name')
```

[Hugging Face](https://huggingface.co/)上のモデルロードのサンプルは、だいたい上のような実装になっています。
これまでなんとなく使っていましたが、少し詳しく挙動を知りたいと思い調査したので、まとめておきます。
また、上記のコードをそのまま実運用システムへ組み込むのにもリスクを感じたので、そのあたりも書いておきます。

## 'from_pretrained'の動作概要

`from_pretrained`は、パラメーターで指定した文字列に一致する事前学習済みのモデルを取得しています。
取得先はHugging Face上のレポジトリとなります。
また、初回ロード時にローカルディレクトリにモデルを保存しており、2回目以降はローカルディレクトリからモデルを取得します。
保存先のディレクトリは、`~/.cache/huggingface/hub/` となります。
保存先を変更したい場合は、`cache_dir`パラメーターに任意のパスを指定すればよいです。


## リスク

ライブラリを試しに使ってみるということであれば、上記の実装方法で問題はないと思います。
しかし、実運用システムへの組み込みを考えると気にしなければならないリスクがあると考えます。

[cl-tohoku/bert-base-japanese-whole-word-masking](https://huggingface.co/cl-tohoku/bert-base-japanese-whole-word-masking)のロードを例にリスクと対策をまとめます。

```python
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("cl-tohoku/bert-base-japanese-whole-word-masking")
```

なお、上記のコードを動かすには以下の2つのライブラリのインストールが必要です。

```bash
!pip install fugashi
!pip install ipadic
```

### リスク1: versionが未指定

冒頭の実装の場合、versionが未指定です。
versionが未指定の場合は最新のversionがインストールされることになります。
Hugging Face上のライブラリは、更新されることがあるため期待したバージョンがインストールされないリスクがあります。
対策としては、from_pretrainedのrevisionパラメーターにバージョンを指定する方法があります。

```python
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("cl-tohoku/bert-base-japanese-whole-word-masking", revision='84425dd597b97e439b193648ea6602682db46e99')
```

revisionはブランチ名、タグ名、コミットIDのいずれかを指定します。
https://huggingface.co/cl-tohoku/bert-base-japanese-whole-word-masking/tree/main

### リスク2: 外部環境との通信制限

システムによっては外部環境との通信が制限されていることもあると思います。
よって、Hugging Faceとの通信ができずモデルがロードできないリスクがあります。

対策としては、外部との通信ができる環境でモデルをダウンロードしておく方法が考えられます。

1. 外部からモデルをダウンロード
2. ダウンロードしたモデルを運用サーバへ転送
3. 転送先のパスを指定してモデルをロード

1のモデルのダウンロードは、`save_pretrained`を使うのがよいです。

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking', revision='84425dd597b97e439b193648ea6602682db46e99')
tokenizer.save_pretrained('model')
```

3のモデルロードは、下記のようにできます。(ローカルのパスを指定すればよいだけ。)

```python
tokenizer = AutoTokenizer.from_pretrained('model')
```

## 参考

### 'from_pretrained'の主要パラメーター

1. pretrained_model_name_or_path (str): 事前学習済みモデルまたはトークナイザーの名前、またはローカルディレクトリへのパス。Hugging Faceのモデルハブに公開されている事前学習済みモデルをロードする場合は、この引数にモデル名を指定します。
2. cache_dir (str, optional): キャッシュディレクトリへのパス。指定された場合、ダウンロードされたモデルやトークナイザーはこのディレクトリに保存されます。指定されない場合、デフォルトのキャッシュディレクトリ（~/.cache/huggingface/transformers/）が使用されます。
3. force_download (bool, optional): モデルまたはトークナイザーを再ダウンロードするかどうかを指定します。デフォルトはFalseで、キャッシュ済みのモデルがある場合はそれを使用します。Trueに設定すると、キャッシュを無視してモデルを再ダウンロードします。
4. resume_download (bool, optional): ダウンロードが中断された場合に、中断された箇所からダウンロードを再開するかどうかを指定します。デフォルトはFalseです。
5. local_files_only (bool, optional): ローカルファイルのみを使用してモデルをロードするかどうかを指定します。デフォルトはFalseで、必要であればモデルをダウンロードします。Trueに設定すると、モデルがローカルに存在しない場合はエラーが発生します。
6. use_auth_token (str or bool, optional): Hugging Faceモデルハブの認証トークン。デフォルトはNoneで、認証なしでモデルをダウンロードします。プライベートなモデルにアクセスする場合には、この引数に認証トークンを指定する必要があります。
7. revision (str, optional): モデルの特定のリビジョンをロードするために使用します。デフォルトはNoneで最新リビジョンをダウンロードします。特定のリビジョンをダウンロードする場合、この引数にリビジョン文字列（コミットハッシュ）を指定します。

より詳細は[公式ドキュメント](https://huggingface.co/docs/transformers/main_classes/model#transformers.PreTrainedModel.from_pretrained)参照

### 参考にした記事

https://hironsan.hatenablog.com/entry/how-to-download-transformers-pretrained-models
