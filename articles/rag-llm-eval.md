---
title: "ICCによるRAGチャットボットの自動評価"
emoji: "✨"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["rag", "llm"]
published: true # trueを指定する
published_at: 2025-09-25 19:00 # 未来の日時を指定する
---

RAGの自動評価で代表的なツールとしてRAGASが挙げられます。
RAGASはLLMの自動評価の手法としては有名であり、多くの指標で多角的な評価ができる利点がある一方、準備や実装が重く評価指標も直感的ではないと思っています。

もっとシンプルかつ直感的な評価方法はないかと探したところ、LINEヤフーで紹介されたICCG Frameworkを見つけました。
下記の記事に評価手法について詳細に記載されています。
https://techblog.lycorp.co.jp/ja/20240819a


ICCG Frameworkとは下記の4つの評価項目を指します。

| 評価要素                  | 説明                                                   |
|---------------------------|--------------------------------------------------------|
| 含有性（Inclusion）       | あらかじめ想定されていた回答の内容が含まれているか？   |
| 相反性（Contradiction）   | あらかじめ想定されていた回答と相反する内容があるか？   |
| 一致性（Consistency）     | あらかじめ想定されていた回答と同じトピックについて回答しているか？ |
| 案内性（Guidance）        | 元情報のURLが案内されているか？                         |


これらの4つの評価要素をLLMで自動評価しています。評価指標はBoolean(true/false)での出力としています。
なお、記事には書かれていませんが、LLMで自動評価しているのは、含有性、相反性、一致性の3つと思われます。
※案内性については元情報のURLが案内されるかをルールベースでチェックすればよいだけのはず。

記事には含有性、相反性、一致性の評価の実装例については記載されていなかったため、実装をしてみました。

## 評価方法の実装概要

含有性、相反性、一致性の3つの指標について、LLMを使った自動評価をしてみます。

- 評価用のLLMとして、`Gemini 2.5 Flash`を使用
- 想定回答とLLM回答を比較して、3つの指標でboolean評価を出力するようにプロンプトを設計


## 実装

実際に動くコードは、記事の最後に記載しています。
必要環境と評価用のプロンプトについて簡単にまとめておきます。

### 必要環境

- Python (※python3.13.3で検証)
- ライブラリ：google-generativeai, pandas
- Google API Key（GOOGLE_API_KEY）を環境変数で定義

```
pip install google-generativeai pandas
export GOOGLE_API_KEY=YOUR_KEY
```

### 評価用のプロンプト

ベースのプロンプトは下記です。
```
あなたはRAGシステムの自動評価者（LLM-as-a-Judge）です。以下の定義に従い、**JSONのみ**で厳密に出力してください。

- Inclusion（含有性）: 想定回答（ground_truth）の主要要素を、生成回答（answer）が十分に含むか。
- Contradiction（相反性）: 生成回答に、想定回答と**矛盾する**記述が存在するか。（存在すれば true）
- Consistency（一致性）: 生成回答が、質問と同じトピック・質問意図に沿っているか。

出力スキーマ（厳守）:
{
  "Inclusion": {"verdict": true/false, "explanation": "40~120字の要約理由"},
  "Contradiction": {"verdict": true/false, "explanation": "40~120字の要約理由"},
  "Consistency": {"verdict": true/false, "explanation": "40~120字の要約理由"}
}

[入力データ]
質問: {{question}}
想定回答(ground_truth):
{{ground_truth}}

生成回答(answer):
{{answer}}

**厳密にJSONのみ**を返してください（前置きや説明文、コードフェンスを含めない）。
```

質問、想定回答、生成回答は動的に変わる変数のため都度変更ができるように実装しています。
単にboolean値だけを出力すると、改善方法がイメージできないため、評価理由についても簡潔に出力するようにしています。
また、出力結果は加工がしやすいように、JSONにしました。

**評価例**

下記の入力に対する評価例です。

**入力**
- 質問: RAGとは何の略で、何をする手法ですか？
- 想定回答: RAGはRetrieval-Augmented Generationの略で、検索した知識を用いて生成する手法。
- 生成回答: RAGはRetrieval-Augmented Generationで、検索と生成を組み合わせる技術です。

**評価結果**

```json
{
  "Consistency": {
    "explanation": "生成回答は質問の意図であるRAGの略称と手法の説明に完全に沿っており、トピックの逸脱はない。",
    "verdict": true
  },
  "Contradiction": {
    "explanation": "生成回答は想定回答と矛盾する情報を含んでおらず、両者の内容は完全に一致している。",
    "verdict": false
  },
  "Inclusion": {
    "explanation": "生成回答は、RAGの正式名称と、検索と生成を組み合わせるという主要な概念を適切に含んでいる。",
    "verdict": true
  }
}
```

この例は、3つの指標がすべて期待どおりになっている例です。
Contradictionがfalseになっていますが、**Contradictionは「相反する内容があるか？」が問いのためfalseが正解**です。


## 評価結果のサンプル

評価結果の妥当性を見るため、3つの評価指標が誤っているテストケースをそれぞれ作り評価の挙動を見てみます。

### Inclusion（含有性）が期待通りでないケース

**入力**
- 質問: RAGとは何の略で、何をする手法ですか？
- 想定回答: RAGはRetrieval-Augmented Generationの略で、検索で得た知識を生成に取り込む手法。
- 生成回答: RAGは品質を高めるための生成テクニックです。

**評価出力（例）**
```json
{
  "Consistency": {
    "explanation": "生成回答はRAGについて言及しており、その目的を説明しているため、質問のトピックと意図には沿っています。ただし、回答は不完全です。",
    "verdict": true
  },
  "Contradiction": {
    "explanation": "生成回答はRAGの目的を簡潔に述べているが、想定回答の内容と直接的に矛盾する事実は含まれていません。",
    "verdict": false
  },
  "Inclusion": {
    "explanation": "生成回答はRAGの正式名称を全く含まず、その手法の核心である「検索で得た知識を取り込む」点も欠落しており、主要な事実が不足しています。",
    "verdict": false
  }
}
```

### Contradiction（相反性）が期待どおりでないケース

**入力**
- 質問: RAGとは何の略で、何をする手法ですか？
- 想定回答: RAGはRetrieval-Augmented Generationの略で、検索で得た知識を生成に取り込む手法。
- 生成回答: RAGはRetrieval-Augmented Generationで、検索で得た知識を生成に取り込む手法ですが、検索は実は使わない生成技術です。

**評価出力（例）**
```json
{
  "Consistency": {
    "explanation": "生成回答はRAGの略称と手法について説明しており、質問の意図に沿った内容である。",
    "verdict": true
  },
  "Contradiction": {
    "explanation": "生成回答は「検索で得た知識を生成に取り込む手法」と述べた直後に「検索は実は使わない生成技術」と矛盾する内容を含んでいる。",
    "verdict": true
  },
  "Inclusion": {
    "explanation": "生成回答はRAGの略称と、検索で得た知識を生成に取り込むという主要な説明を含んでいる。",
    "verdict": true
  }
}
```

### Consistency（一致性）が期待どおりでないケース

**入力**
- 質問: RAGとは何の略で、何をする手法ですか？
- 想定回答: RAGはRetrieval-Augmented Generationの略で、検索で得た知識を生成に取り込む手法。
- 生成回答: ドロップアウトはニューラルネットの正則化手法で、学習時にランダムにユニットを無効化します。RAGはRetrieval-Augmented Generationの略で、検索した知識を用いて生成する手法。

**評価出力（例）**
```json
{
  "Consistency": {
    "explanation": "生成回答はRAGに関する質問に対し、無関係なドロップアウトの説明から始まっており、質問意図に完全に沿っているとは言えない。",
    "verdict": false
  },
  "Contradiction": {
    "explanation": "生成回答のRAGに関する記述は、想定回答と矛盾する内容を含んでいない。ドロップアウトに関する記述は無関係だが矛盾ではない。",
    "verdict": false
  },
  "Inclusion": {
    "explanation": "生成回答はRAGの略称と、検索で得た知識を生成に利用する手法であるという主要な事実を十分に含んでいる。",
    "verdict": true
  }
}
```

## まとめ

本記事では、RAGの最終回答品質を**軽量・直感的**に測るICC評価（Inclusion/Contradiction/Consistency）を紹介し、評価用プロンプトの実例とサンプル出力を示しました。  
結論としては、チャットボットの品質を評価する手法としてかなり使えそうだなと思えました。
この3つに加えて、案内性を評価すれば、チャットボットの品質評価の信憑性は基本的に担保されそうです。

懸念として、RAGの検索部分（案内性）はLLMでの評価はできず、適切な検索ができない場合の対処方法のヒントがこれだけでは掴めないというのがあります。
RAGのチャットボットの場合、検索の部分で適切なソースを参照できずに苦労する部分が多いため、ここの改善ヒントがわかるような評価手法も合わせてやれるとベターと思いました。


## 実装した自動評価のコード

```python
import os
import json
import time
from typing import Dict, Any
import pandas as pd
import google.generativeai as genai

# --- 環境変数読み込み ---
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("環境変数 GOOGLE_API_KEY が見つかりません。環境変数を定義してください。")

# --- Gemini 設定 ---
GEMINI_MODEL_NAME = "gemini-2.5-flash"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL_NAME)
GENERATION_CONFIG = {
    "response_mime_type": "application/json",
    "temperature": 0.0,
    "top_p": 0.9,
    "top_k": 32,
    "max_output_tokens": 2048,
}

# --- 評価プロンプト ---
BASE_INSTRUCTIONS = """
あなたはRAGシステムの自動評価者（LLM-as-a-Judge）です。
以下の定義に従い、JSONのみで厳密に出力してください（余計な前置き・後置きは不要）。

- 含有性（Inclusion）: 想定回答（ground_truth）に含まれる主要な事実・要素を、生成回答（answer）が十分に含むか。
- 相反性（Contradiction）: 生成回答が想定回答と矛盾する内容を含むか。
- 一致性（Consistency）: 生成回答が、想定回答と同じトピック・質問意図に沿っているか。

出力スキーマ:
{
  "Inclusion": {"verdict": true/false, "explanation": "<40~120字程度の要約理由>"},
  "Contradiction": {"verdict": true/false, "explanation": "<40~120字程度の要約理由>"},
  "Consistency": {"verdict": true/false, "explanation": "<40~120字程度の要約理由>"}
}
""".strip()

def build_case_block_no_ctx(q: str, gt: str, ans: str) -> str:
    return f"""[入力データ]
質問: {q}

想定回答(ground_truth):
{gt}

生成回答(answer):
{ans}
"""

def build_prompt_all(q: str, gt: str, ans: str) -> str:
    return f"""{BASE_INSTRUCTIONS}

評価対象メトリクス: Inclusion, Contradiction, Consistency（すべて）
判定基準:
- Inclusion: 生成回答が想定回答の主要要素を十分に含むか（十分なら true、欠落が大きければ false）。
- Contradiction: 生成回答が想定回答と矛盾する内容を含むか（矛盾があれば true、なければ false）。
- Consistency: 生成回答が想定回答と同じトピック・質問意図に沿っているか（沿っていれば true、脱線・無関係なら false）。

{build_case_block_no_ctx(q, gt, ans)}
厳密に JSON のみを返してください。
"""

def call_gemini_json(prompt: str, max_retries: int = 3, retry_wait: float = 2.0) -> Dict[str, Any]:
    for attempt in range(max_retries):
        try:
            resp = model.generate_content(prompt, generation_config=GENERATION_CONFIG)
            text = (resp.text or "").strip()
            if not text.startswith("{"):
                l, r = text.find("{"), text.rfind("}")
                if l != -1 and r != -1 and l < r:
                    text = text[l:r+1]
            return json.loads(text)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(retry_wait)

def eval_one_row(row: pd.Series) -> Dict[str, Any]:
    q, gt, ans = row["question"], row["ground_truth"], row["answer"]
    prompt = build_prompt_all(q, gt, ans)
    data = call_gemini_json(prompt)
    return data

#
# --- ダミーデータで動作確認 ---
# 
sample = {
    "question": "RAGとは何の略で、何をする手法ですか？",
    "ground_truth": "RAGはRetrieval-Augmented Generationの略で、検索した知識を用いて生成する手法。",
    "answer": "RAGはRetrieval-Augmented Generationで、検索と生成を組み合わせる技術です。"
}

# 結果取得
result = eval_one_row(pd.Series(sample))


print(f'- 質問: {sample["question"]}')
print(f'- 想定回答: {sample["ground_truth"]}')
print(f'- 生成回答: {sample["answer"]}')

print("\n=== 判定結果 (JSON) ===")
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
```