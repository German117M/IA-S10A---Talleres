WIN_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def winner(board):

    for a, b, c in WIN_LINES:

        if (
            board[a]
            == board[b]
            == board[c]
            and board[a] != " "
        ):
            return board[a]

    return None


def minimax(board, maximizing):

    w = winner(board)

    if w == "X":
        return 1

    if w == "O":
        return -1

    if " " not in board:
        return 0

    scores = []

    mark = (
        "X"
        if maximizing
        else "O"
    )

    for i, cell in enumerate(board):

        if cell == " ":

            nxt = board.copy()
            nxt[i] = mark

            scores.append(
                minimax(
                    nxt,
                    not maximizing
                )
            )

    if maximizing:
        return max(scores)

    return min(scores)


def best_move(board):

    choices = []

    for i, cell in enumerate(board):

        if cell == " ":

            nxt = board.copy()
            nxt[i] = "X"

            choices.append(
                (
                    minimax(
                        nxt,
                        False
                    ),
                    i
                )
            )

    return max(choices)[1]


board = [
    "X", "O", "X",
    "O", "X", " ",
    " ", " ", "O"
]

print(
    "Tablero:",
    board
)

print(
    "Mejor posición para X:",
    best_move(board)
)