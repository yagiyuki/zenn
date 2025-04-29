---
title: "うっかり GitHub に公開しない！5分でできる生成AI APIキー管理するTips紹介"
emoji: "🗝️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["generativeai", "python", "github", "セキュリティ対策", "gemini"]
published: true
---


## はじめに

OpenAI、Gemini、Claude など、生成AI の API を手軽に試せる時代になりました。
ちょっと使うだけであれば、数行で動作するため、非エンジニアでも扱えるレベル感になっていると思います。
検証用スクリプトを GitHub に置くケースも多いと思いますが、例えば、こんなサンプルコードを見かけることはありませんか？

```python
import google.generativeai as genai

# APIキーを設定
API_KEY = "xxx"

# Gemini APIの設定
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

user_input = input("質問: ")
response = model.generate_content(user_input)  # AIの応答を取得
if hasattr(response, "text"):  # 応答がある場合のみ表示
    print("Gemini:", response.text)
else:
    print("Gemini: 応答が取得できませんでした。")
```

インターネットに公開されている実装例は、分かりやすさを重視するチュートリアルを目的に書かれたものが中心です。
しかし、実際の開発でこのまま GitHub にコミットしたら……。もしリポジトリが公開状態であれば、キーを悪用され高額請求が発生する可能性があります。
（仮にprivateであってもセキュリティ上はあまりよろしくないのではと思います。）

そこで本記事では、生成AIのAPIを検証する人向けに、APIキーをうっかり GitHub へ公開しないための Tips を 紹介します。
非エンジニアにとってもわかりやすい内容になっていると思います。

## OS 環境変数に API キーを保存する

## 手法概要

OS 環境変数（Environment Variable） とは、OS やシェルがプロセスに渡す “設定用の値” です。
キーと値のペアで保持され、アプリは os.environ["GEMINI_API_KEY"] のように参照できます。
ソースファイルに直接APIキーの値を書く必要がない（ソースコードに混ざらない）ため、うっかり GitHub にコミットしてしまう事故を避けられます。

:::message
ポイント
* キーは OS が管理してくれる。Pythonから使う際は、OSで管理される生成AIのキーの設定値を参照するだけ。
* キーをシェルの設定ファイル（例: .zshrc）に書き込む運用を想定しているため、“完全ファイルレス” ではない
* それでも コードベースにハードコーディング するよりは安全性は高い。（GitHubにAPIキーをうっかりコミットすることはまずない。）
:::

### 設定手順（Mac）

私がMacユーザーのためMacでの実施手順を書きます。ただし、Windowsでも流れは一緒と思います。
:::message
重要なポイントとして、1〜4の手順は一回設定すればよいということです。(PC買い替えやAPIキーの変更の場合は別です。)
:::

1.	ターミナルを開く: Spotlight で「Terminal」を検索
2. 自分のログインシェルを確認

```bash
echo $SHELL
# 例: /bin/zsh なら zsh、/bin/bash なら bash
```

3. 設定ファイルを特定

|シェル|代表的な設定ファイル|補足|
|:----|:----|:----|
|zsh|~/.zshrc|macOS Catalina 以降のデフォルト|
|bash|~/.bash_profile|bash_profile がなければ .bashrc を参照することも|

4. API キーを追記
例として環境変数名を GEMINI_API_KEY とします。
```bash
# zsh の場合
echo 'export GEMINI_API_KEY="ここにあなたのキー"' >> ~/.zshrc
source ~/.zshrc  # 追記を即時反映
```
5. Python から使う

```python
import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

user_input = input("質問: ")
response = model.generate_content(user_input)  # AIの応答を取得
if hasattr(response, "text"):  # 応答がある場合のみ表示
    print("Gemini:", response.text)
else:
    print("Gemini: 応答が取得できませんでした。")
```

## まとめ

- **ハードコーディングは厳禁**  
  API キーをソースに直接書くと Git 履歴に残り、漏えいリスクが跳ね上がります。

- **最初の一歩は OS 環境変数**  
  `.zshrc` や `.bash_profile` に `export GEMINI_API_KEY="..."` を追記するだけで、安全性と可搬性が大きく向上します。

- **設定は 5 分で完了**  
  `echo $SHELL` でシェルを確認 → 設定ファイルを選ぶ → `export` を追記 → `source` で適用、の 4 ステップだけ。


## FYI

個人の検証用途で生成AIのAPIを使う場合、無料枠があるGeminiが最強だと思いました。
https://shift-ai.co.jp/blog/20257/