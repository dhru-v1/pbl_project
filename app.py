from flask import Flask, render_template, request, redirect, url_for, jsonify
import chess
from engine import bestmove_for_black, bestmove_for_white

app = Flask(__name__, static_folder="images", static_url_path="/images")

board = chess.Board()
game_mode = "pvp"
player_color = "white"

def get_board_state():
    game_over = board.is_game_over()
    message = ""
    if game_over:
        if board.is_checkmate():
            winner = "White" if board.turn == chess.BLACK else "Black"
            message = f"Checkmate! {winner} wins!"
        elif board.is_stalemate():
            message = "Draw by stalemate!"
        else:
            message = "Game over!"
            
    # Check if last move was a capture to trigger capture sound
    last_move_capture = False
    if len(board.move_stack) > 0:
        last_move = board.move_stack[-1]
        # Pop the move to check the board state before it
        board.pop()
        last_move_capture = board.is_capture(last_move)
        board.push(last_move)
        
    return {
        "fen": board.fen(),
        "turn": "white" if board.turn == chess.WHITE else "black",
        "game_over": game_over,
        "message": message,
        "in_check": board.is_check(),
        "legal_moves": [move.uci() for move in board.legal_moves],
        "game_mode": game_mode,
        "player_color": player_color,
        "last_move": board.move_stack[-1].uci() if len(board.move_stack) > 0 else None,
        "last_move_capture": last_move_capture
    }

@app.route("/", methods=["GET", "POST"])
def index():
    global game_mode, board, player_color
    if request.method == "POST":
        game_mode = request.form.get("mode", "pvp")
        board = chess.Board()
        if game_mode == "pvb":
            player_color = request.form.get("color", "white")
        return redirect(url_for("play"))
    return render_template("index.html")

@app.route("/play")
def play():
    return render_template("play.html", game_mode=game_mode, player_color=player_color)

@app.route("/api/state")
def api_state():
    return jsonify(get_board_state())

@app.route("/api/move", methods=["POST"])
def api_move():
    global board
    data = request.json
    move_uci = data.get("move")
    if not move_uci:
        return jsonify({"success": False, "error": "No move provided"})
    
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
            return jsonify({"success": True, "state": get_board_state()})
        else:
            return jsonify({"success": False, "error": "Illegal move"})
    except ValueError:
        return jsonify({"success": False, "error": "Invalid move format"})

@app.route("/api/bot_move", methods=["POST"])
def api_bot_move():
    global board
    if board.is_game_over():
        return jsonify({"success": False, "error": "Game over"})
        
    if board.turn == chess.WHITE:
        ai_move = bestmove_for_white(board)
    else:
        ai_move = bestmove_for_black(board)
        
    if ai_move:
        board.push(ai_move)
        return jsonify({
            "success": True, 
            "move": ai_move.uci(), 
            "state": get_board_state()
        })
    return jsonify({"success": False, "error": "No move found"})

@app.route("/api/reset", methods=["POST"])
def api_reset():
    global board
    board = chess.Board()
    return jsonify({"success": True, "state": get_board_state()})

if __name__ == "__main__":
    app.run(debug=True)
