from flask import Flask, render_template, request, redirect, url_for
import chess
from engine import bestmove_for_black, bestmove_for_white

app = Flask(__name__)

board = chess.Board()
game_mode = None
player_color = "white"


@app.route("/", methods=["GET", "POST"])
def index():
    global game_mode, board, player_color

    if request.method == "POST":
        game_mode = request.form.get("mode")
        board = chess.Board()

        if game_mode == "pvb":
            player_color = request.form.get("color") or "white"

        return redirect(url_for("play"))

    return render_template("index.html")


@app.route("/play", methods=["GET", "POST"])
def play():
    global board, game_mode, player_color

    message = ""

    # ======================
    # HANDLE POST REQUESTS
    # ======================
    if request.method == "POST":
        move_input = request.form.get("move")

        # Reset
        if move_input == "reset":
            board = chess.Board()
            return redirect(url_for("play"))

        # BVB - manual next move
        if move_input == "next_ai":
            if game_mode == "bvb" and not board.is_game_over():

                if board.turn == chess.WHITE:
                    ai_move = bestmove_for_white(board)
                else:
                    ai_move = bestmove_for_black(board)

                print("BVB AI move:", ai_move.uci())
                board.push(ai_move)

            return redirect(url_for("play"))

        # PVP and PVB player move
        try:
            move = chess.Move.from_uci(move_input)

            if move in board.legal_moves:
                board.push(move)

                # Player vs Bot response
                if game_mode == "pvb" and not board.is_game_over():
                    if (player_color == "white" and board.turn == chess.BLACK) or \
                       (player_color == "black" and board.turn == chess.WHITE):

                        if board.turn == chess.WHITE:
                            ai_move = bestmove_for_white(board)
                        else:
                            ai_move = bestmove_for_black(board)

                        print("PVB AI move:", ai_move.uci())
                        board.push(ai_move)

            else:
                message = "Illegal move."

        except Exception:
            message = "Invalid move. Use UCI like e2e4."

    # ======================
    # GAME STATUS
    # ======================
    turn = "White" if board.turn == chess.WHITE else "Black"

    if board.is_game_over():
        if board.is_checkmate():
            winner = "White" if board.turn == chess.BLACK else "Black"
            message = f"Checkmate! {winner} wins!"
        elif board.is_stalemate():
            message = "Draw by stalemate!"
        else:
            message = "Game over!"

    game_over = board.is_game_over()

    return render_template(
        "play.html",
        board=str(board),
        turn=turn,
        message=message,
        game_mode=game_mode,
        player_color=player_color,
        game_over=game_over
    )


@app.route("/reset")
def reset():
    global board
    board = chess.Board()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
