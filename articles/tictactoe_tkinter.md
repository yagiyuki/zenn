---
title: "Python初心者必見！Tkinterを使って簡単に○✗ゲームを作成しよう！"
emoji: "🎮"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Python", "tkinter", "Game", "gui"]
published: true
---

## はじめに

PythonとGUIライブラリであるTkinterを使って、簡単な○✗ゲームを作成するための記事を書きました。
Pythonを勉強してみたいけど、何からやればいい変わらないという方は、ぜひこの記事の手順に沿ってゲームを作成してみてください。
楽しくPythonが勉強できると思います。
また、最後に本記事の理解度を確認するための問題も用意したので、ぜひチャレンジしてみてください。

## 実装手順

下記に○✗ゲーム実装の手順を書きます。  
まずは、完成したコードを実際に動かしてから読みたいという人は、「実装結果」を参照してください。  

### 1. Tkinterのインポート

まずは、Tkinterをインポートしましょう。

```python
from tkinter import *
```

### 2. ウィンドウの作成

Tkinterのウィンドウを作成し、ウィンドウのタイトルを設定します。

```python
root = Tk()
root.title("Tic Tac Toe")
```

### 3. ゲームの初期設定

プレイヤーとゲーム終了フラグを設定し、ボタンの状態を初期化する関数を定義します。

```python
player = 1
game_over = False

def initialize_button():
    return [['', '', ''],
            ['', '', ''],
            ['', '', '']]

button = initialize_button()
```

### 4. クリックイベント

ボタンがクリックされたときの処理を実装します。
実装内容は、以下です。

* プレイヤー交代
* ボタンの状態が更新 (`update_board()`の呼び出し)
* 勝者が決まったかどうかの確認 (`check_winner()`の呼び出し)

```python
def click(row, column):
    global player, game_over
    if not game_over and button[row][column] == '':
        if player == 1:
            button[row][column] = "○"
            player = 2
        elif player == 2:
            button[row][column] = "✗"
            player = 1
        update_board()
        check_winner()
```

### 5. ボタンの作成と更新

クリックイベントが発生したときにボタンの状態を更新する関数です。

```python
def update_board():
    for row in range(3):
        for column in range(3):
            b = Button(root, text=button[row][column], font=('Arial', 60), width=3, height=1,
                       command=lambda row=row, column=column: click(row, column))
            b.grid(row=row, column=column)
```

### 6. 勝者のチェック

勝者をチェックし、ゲーム終了フラグを更新する関数を定義します。
この関数は、3つの同じ記号が横、縦、または斜めに並んでいるかどうかを確認し、その結果に基づいて勝者を決定する処理を実装します。
また、ゲームが引き分けになった場合も確認します。

```python
def check_winner():
    global game_over
    for i in range(3):
        if button[i][0] == button[i][1] == button[i][2] != '':
            display_winner(button[i][0])
            game_over = True
        if button[0][i] == button[1][i] == button[2][i] != '':
            display_winner(button[0][i])
            game_over = True
    if button[0][0] == button[1][1] == button[2][2] != '':
        display_winner(button[0][0])
        game_over = True
    if button[0][2] == button[1][1] == button[2][0] != '':
        display_winner(button[0][2])
        game_over = True

    if not any('' in row for row in button) and not game_over:
        display_draw()
        game_over = True
    elif game_over:
        display_reset_button()
```

### 7. 勝者、引き分け、リセットボタンの表示

勝者の結果の表示、引き分けの結果を表示、リセットボタンを表示をする関数です。

```python
def display_winner(winner):
    label = Label(root, text=f"Winner: {winner}", font=('Arial', 20))
    label.grid(row=3, column=0, columnspan=3)

def display_draw():
    label = Label(root, text="Draw", font=('Arial', 20))
    label.grid(row=3, column=0, columnspan=3)

def display_reset_button():
    reset_button = Button(root, text="Reset", font=('Arial', 20), command=reset_game)
    reset_button.grid(row=4, column=0, columnspan=3)
```

### 8. ゲームのリセット

ゲームをリセットし、ボタンの状態とゲーム終了フラグを初期化する関数です。

```python
def reset_game():
    global player, game_over, button
    player = 1
    game_over = False
    button = initialize_button()
    for widget in root.grid_slaves():
        if int(widget.grid_info()["row"]) > 2:
            widget.destroy()
    update_board()
```

### 9. メインループの開始

ボタンの状態を初期化し、メインループを開始します。

```python
update_board()

root.mainloop()
```

## 実装結果

上記のコードを実装したコードは、[こちら](https://github.com/yagiyuki/zenn/blob/e812f12/python/tkinter_tictactoe.py)から取得できます。
`python tkinter_tictactoe.py` で○✗ゲームが開始しますので、遊んでみてください。

![](/images/tkinter_tictactoe.png)

## 理解度の確認

本記事の理解度を確認するための問題を1つ用意しました。
ぜひ、チャレンジしてください。

:::message 

**== 問題 ==**

○✗ゲームで勝者が決まった場合は、ゲームを再スタートできるように `Reset` ボタンを用意しています。
しかし、引き分けの場合は、`Reset`ができません。
引き分けの場合でも、ゲームを再スタートできるように `Reset` ボタンを用意してください。
:::
