from tkinter import *

root = Tk()
root.title("Tic Tac Toe")

player = 1
game_over = False

def initialize_button():
    return [['', '', ''],
            ['', '', ''],
            ['', '', '']]

button = initialize_button()

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

def update_board():
    for row in range(3):
        for column in range(3):
            b = Button(root, text=button[row][column], font=('Arial', 60), width=3, height=1,
                       command=lambda row=row, column=column: click(row, column))
            b.grid(row=row, column=column)

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

def display_winner(winner):
    label = Label(root, text=f"Winner: {winner}", font=('Arial', 20))
    label.grid(row=3, column=0, columnspan=3)

def display_draw():
    label = Label(root, text="Draw", font=('Arial', 20))
    label.grid(row=3, column=0, columnspan=3)

def display_reset_button():
    reset_button = Button(root, text="Reset", font=('Arial', 20), command=reset_game)
    reset_button.grid(row=4, column=0, columnspan=3)

def reset_game():
    global player, game_over, button
    player = 1
    game_over = False
    button = initialize_button()
    for widget in root.grid_slaves():
        if int(widget.grid_info()["row"]) > 2:
            widget.destroy()
    update_board()

update_board()

root.mainloop()

