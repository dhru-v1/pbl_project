import chess

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def bestmove_for_white(board):
    return get_best_move(board, depth=4)

def bestmove_for_black(board):
    return get_best_move(board, depth=4)


def get_best_move(board, depth):
    best_move = None
    max_eval = -99999
    alpha = -99999
    beta = 99999

    for move in order_moves(board):
        board.push(move)
        eval = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()

        if eval > max_eval:
            max_eval = eval
            best_move = move

        alpha = max(alpha, eval)

    return best_move


def negamax(board, depth, alpha, beta):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    max_eval = -99999
    for move in order_moves(board):
        board.push(move)
        eval = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()

        max_eval = max(max_eval, eval)
        alpha = max(alpha, eval)

        if alpha >= beta:
            break 

    return max_eval


def get_move_score(board, move):
    score = 0
    if board.is_capture(move):
        if board.is_en_passant(move):
            return 105 
        
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        
        if victim and attacker:
            victim_val = PIECE_VALUES.get(victim.piece_type, 0)
            attacker_val = PIECE_VALUES.get(attacker.piece_type, 0)
            # Prioritizes moves like Pawn taking Queen over Queen taking Pawn
            score = 100 + victim_val * 10 - attacker_val
    return score

def order_moves(board):
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: get_move_score(board, m), reverse=True)
    return moves

# =========================
# EVALUATION FUNCTION
# =========================

def evaluate_board(board):
    if board.is_checkmate():
        # In Negamax, returning a highly negative number means the CURRENT player to move lost
        return -99999
    
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0

    # Material Calculation
    for piece_type, value in PIECE_VALUES.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value

    # Mobility Calculation (Patched Null Move Bug)
    mobility_bonus = 0.1
    white_moves = 0
    black_moves = 0

    if board.turn == chess.WHITE:
        white_moves = len(list(board.legal_moves))
        if not board.is_check():
            board.push(chess.Move.null())
            black_moves = len(list(board.legal_moves))
            board.pop()
    else:
        black_moves = len(list(board.legal_moves))
        if not board.is_check():
            board.push(chess.Move.null())
            white_moves = len(list(board.legal_moves))
            board.pop()

    score += (white_moves - black_moves) * mobility_bonus

    # Negamax requires the evaluation to be from the perspective of the side whose turn it is
    perspective = 1 if board.turn == chess.WHITE else -1
    return score * perspective

# =========================
# CLI (UNCHANGED)
# =========================

def get_move(board):
    while True:
        move_input = input("Enter move: ")
        try:
            move = chess.Move.from_uci(move_input)
            if move in board.legal_moves:
                return move
            else:
                print("Illegal move. Try again.")
        except ValueError:
            if move_input == "quit":
                return move_input
            print("Invalid format. Use UCI like e2e4 or g7g8q.")

def pvp():
    board = chess.Board()

    print("White moves first")

    while not board.is_game_over():
        print(board)

        player = "White" if board.turn == chess.WHITE else "Black"
        print(f"{player} to move")

        move = get_move(board)

        if move == "quit":
            break

        board.push(move)

        if board.is_check():
            print("CHECK!")

    print(board)
    print("Game Over")

    if board.is_game_over():
        reason = board.outcome().termination
        print(f"{player} won")
        print("Reason:", reason)
    else:
        print(f"{player} resigned")

def pvb():
    pass

def bvb():
    board = chess.Board()

    while not board.is_game_over():
        print(board)

        if board.turn == chess.WHITE:
            move = bestmove_for_white(board)
        else:
            move = bestmove_for_black(board)

        board.push(move)
        print(f"AI plays: {move.uci()}")

    print(board)
    print("Game over!")
    print("Result:", board.result())


if __name__ == "__main__":
    pass
