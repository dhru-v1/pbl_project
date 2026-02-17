import chess

def bestmove_for_black(board):
    bestmove = None
    depth = 1
    while depth <= 4:  # Maximum depth
        bestscore = -9999
        alpha = -9999
        beta = 9999
        for move in order_moves(board):
            temp_board = board.copy()
            temp_board.push(move)
            score = minimax(temp_board, depth - 1, alpha, beta, False)
            if score > bestscore:
                bestscore = score
                bestmove = move
            alpha = max(alpha, bestscore)
        depth += 1
    return bestmove

def bestmove_for_white(board):
    bestmove = None
    depth = 1
    while depth <= 4:  # Maximum depth
        bestscore = -9999
        alpha = -9999
        beta = 9999
        for move in order_moves(board):
            temp_board = board.copy()
            temp_board.push(move)
            score = minimax(temp_board, depth - 1, alpha, beta, True)
            if score > bestscore:   
                bestscore = score
                bestmove = move
            alpha = max(alpha, bestscore)
        depth += 1
    return bestmove


def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing:
        bestscore = -9999
        for move in order_moves(board):
            board.push(move)
            score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            bestscore = max(score, bestscore)
            alpha = max(alpha, bestscore)
            if beta <= alpha:
                break
        return bestscore
    else:
        bestscore = 9999
        for move in order_moves(board):
            board.push(move)
            score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            bestscore = min(score, bestscore)
            beta = min(beta, bestscore)
            if beta <= alpha:
                break
        return bestscore

def order_moves(board):
    moves = list(board.legal_moves)
    moves.sort(key=lambda move: board.is_capture(move), reverse=True)
    return moves

def evaluate_board(board):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -9999  
        else:
            return 9999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0 

    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0 
    }

    score = 0
    for piece_type in piece_values:
        score += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]

    mobility_bonus = 0.1
    score += len(list(board.legal_moves)) * mobility_bonus

    return score

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

        if move=="quit":
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
            print("White's turn")
            move = bestmove_for_black(board)
            
        else:
            print("Black's turn")
            move = bestmove_for_black(board)
        
        board.push(move)
        print(f"AI plays: {move.uci()}")
    
    print(board)
    print("Game over!")
    print("Result: " + board.result())

if __name__ == "__main__":
    pass
