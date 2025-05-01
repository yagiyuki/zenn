---
title: "うっかり GitHub に公開しない！5分でできる生成AI APIキー管理するTips紹介"
emoji: "🗝️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["generativeai", "python", "github", "セキュリティ対策", "gemini"]
published: true
---


## はじめに

OpenAI、Gemini、Claude など、生成AI の API を手軽に試せる時代になりました。
まともに検証コードを書くとしたら、下記のようなコードになります。

```python
import google.generativeai as genai

# APIキーを設定
API_KEY = "xxx"

# Gemini APIの設定
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

user_input = input("質問: ")
response = model.generate_content(user_input)  # AIの応答を取得
print("Gemini:", response.text) # 応答結果の表示
```

APIキーをハードコードしたまま GitHub に上げるのは危険です。この記事では、安全に API キーを管理するための簡単な Tips を2つ紹介します。

## TIPS1: OS 環境変数に API キーを保存する

OS 環境変数（Environment Variable） に書いておく方法です。おそらくこれが一番手軽です。
キーと値のペアで保持され、アプリは os.environ["GEMINI_API_KEY"] のように参照できます。
ソースファイルに直接APIキーの値を書く必要がない（ソースコードに混ざらない）ため、うっかり GitHub にコミットしてしまう事故を避けられます。

Macユーザーであれば、`~/.zshrc`に一行書いておくだけです。（bashを使っている場合は、`~/.bash_profile`に書く。）

```bash
echo $SHELL
# 例: /bin/zsh なら zsh、/bin/bash なら bash
```
pythonからは下記のように参照します。
```python
import os
import google.generativeai as genai

# APIキーを参照
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

user_input = input("質問: ")
response = model.generate_content(user_input)  # AIの応答を取得
print("Gemini:", response.text) # 応答結果の表示
```

## TIPS2: Secret.yamlを定義する

設定ファイル（例: `secret.yaml`）に API キーを記述し、それをプログラムから読み込む方法です。この設定ファイル自体を `.gitignore` に追加しておくことで、GitHub に誤ってコミットしてしまうのを防ぎます。
レポジトリごとにAPI キーを管理したいときに便利です。

まず、レポジトリに `secret.yaml` というファイルを作成し、以下のように記述します。

```YML
GEMINI_API_KEY: "ここにあなたのAPIキーを貼り付けます"
# 他のキーや設定も必要に応じて追加できます
# OPENAI_API_KEY: "xxx"
```

次に、この `secret.yaml` を Git の管理対象から除外するために、`.gitignore` ファイルに以下のように追記します。

```
secret.yaml
```

最後に、Python コードから `secret.yaml` ファイルを読み込んで API キーを取得します。


```python
import os
import yaml  # PyYAMLライブラリをインポート
import google.generativeai as genai

# secret.yaml から API キーを読み込む
try:
    with open("secret.yaml", "r") as f:
        secrets = yaml.safe_load(f)
    api_key = secrets["GEMINI_API_KEY"]
except FileNotFoundError:
    print("エラー: secret.yaml が見つかりません。")
    exit()
except KeyError:
    print("エラー: secret.yaml に GEMINI_API_KEY が定義されていません。")
    exit()

# APIキーを設定
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

user_input = input("質問: ")
response = model.generate_content(user_input)  # AIの応答を取得
print("Gemini:", response.text) # 応答結果の表示
```

## コメント募集

Tipsを2つ紹介しましたが、他にも様々な方法があると思います。
皆さんが実践している便利な方法やおすすめのツールがあれば、ぜひコメントで共有してください！

## FYI

個人の検証用途で生成AIのAPIを使う場合、無料枠があるGeminiが最強だと思いました。
https://shift-ai.co.jp/blog/20257/