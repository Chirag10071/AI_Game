import math
import random

# Constants for board
BLACK = 'B'
WHITE = 'W'
EMPTY = '.'

# Directions (up, down, left, right)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

class ClobberGame:
    def __init__(self, rows=None, cols=None):
        # If rows and cols are not provided, ask the user for grid size
        if rows is None or cols is None:
            self.rows, self.cols = self.get_grid_size_from_user()
        else:
            self.rows = rows
            self.cols = cols
        
        self.board = self.init_board()
        self.current_player = BLACK
    
    def get_grid_size_from_user(self):
        """Prompt user for grid size with error handling."""
        while True:
            try:
                rows = int(input("Enter number of rows for the grid: "))
                cols = int(input("Enter number of columns for the grid: "))
                if rows > 1 and cols > 1:
                    return rows, cols
                else:
                    print("Grid size must be at least 2x2. Please try again.")
            except ValueError:
                print("Invalid input. Please enter numeric values.")

    def init_board(self):
        """Initialize the board with alternating BLACK and WHITE stones."""
        board = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                if (i + j) % 2 == 0:
                    row.append(BLACK)
                else:
                    row.append(WHITE)
            board.append(row)
        return board
    
    def display_board(self):
        for row in self.board:
            print(" ".join(row))
        print()

    def get_legal_moves(self, player):
        """Returns a list of all legal moves for the player."""
        moves = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == player:
                    for d in DIRECTIONS:
                        ni, nj = i + d[0], j + d[1]
                        if 0 <= ni < self.rows and 0 <= nj < self.cols and self.board[ni][nj] != player and self.board[ni][nj] != EMPTY:
                            moves.append(((i, j), (ni, nj)))
        return moves

    def make_move(self, move):
        """Executes a move and updates the board with error handling."""
        try:
            (i, j), (ni, nj) = move
            if self.board[i][j] != self.current_player:
                raise ValueError("You cannot move a piece that doesn't belong to you.")
            self.board[ni][nj] = self.board[i][j]  # Move the stone
            self.board[i][j] = EMPTY               # Set old position to empty
            self.switch_player()
        except IndexError:
            print("Invalid move. Please try again.")
        except ValueError as e:
            print(e)

    def switch_player(self):
        """Switches the player turn."""
        self.current_player = WHITE if self.current_player == BLACK else BLACK

    def is_terminal(self):
        """Returns True if the game is over."""
        return not self.get_legal_moves(BLACK) and not self.get_legal_moves(WHITE)

    def evaluate(self):
        """Simple evaluation function based on the number of stones."""
        black_count = sum(row.count(BLACK) for row in self.board)
        white_count = sum(row.count(WHITE) for row in self.board)
        return black_count - white_count if self.current_player == BLACK else white_count - black_count

    def alpha_beta(self, depth, alpha, beta, maximizing_player):
        """Alpha-beta pruning algorithm."""
        if depth == 0 or self.is_terminal():
            return self.evaluate()

        if maximizing_player:
            max_eval = -math.inf
            for move in self.get_legal_moves(self.current_player):
                self.make_move(move)
                eval = self.alpha_beta(depth - 1, alpha, beta, False)
                self.undo_move(move)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in self.get_legal_moves(self.current_player):
                self.make_move(move)
                eval = self.alpha_beta(depth - 1, alpha, beta, True)
                self.undo_move(move)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def undo_move(self, move):
        """Undo the move and restore the previous board state."""
        try:
            (i, j), (ni, nj) = move
            self.board[i][j] = self.board[ni][nj]
            self.board[ni][nj] = WHITE if self.board[i][j] == BLACK else BLACK
            self.switch_player()
        except IndexError:
            print("Error: Attempted to undo a move that is out of bounds.")

    def ai_move(self, depth=5):
        """AI selects the best move using alpha-beta pruning."""
        best_move = None
        best_value = -math.inf if self.current_player == BLACK else math.inf
        alpha, beta = -math.inf, math.inf

        for move in self.get_legal_moves(self.current_player):
            self.make_move(move)
            move_value = self.alpha_beta(depth - 1, alpha, beta, False)
            self.undo_move(move)

            if self.current_player == BLACK and move_value > best_value:
                best_value = move_value
                best_move = move
            elif self.current_player == WHITE and move_value < best_value:
                best_value = move_value
                best_move = move

        return best_move

    def play(self):
        """Main game loop for AI vs manual player."""
        last_player = None  # Keep track of the last player who made a move
        
        while not self.is_terminal():
            self.display_board()

            if self.current_player == BLACK:
                print("AI's (BLACK) turn:")
                move = self.ai_move()
                if move is not None:  # Check if the AI found a legal move
                    self.make_move(move)
                    last_player = BLACK  # Track the last player
                else:
                    print("AI has no legal moves left.")
                    break
            else:
                print("Manual Player's (WHITE) turn:")
                move = self.get_manual_move()
                if move is not None:  # Check if a valid move was received
                    self.make_move(move)
                    last_player = WHITE  # Track the last player
                else:
                    print("No valid move was made.")
                    break

        print("Game over!")
        self.display_board()

        # The winner is the player who made the last move
        if last_player == BLACK:
            print("AI (BLACK) wins by making the last move!")
        else:
            print("Manual Player (WHITE) wins by making the last move!")

    def get_manual_move(self):
        """Prompts manual player to make a move with error handling."""
        legal_moves = self.get_legal_moves(self.current_player)
        while True:
            move = input(f"Enter your move as 'row1 col1 row2 col2' (e.g., 1 0 0 0): ").split()
            if len(move) != 4:
                print("Invalid input. Enter exactly four numbers.")
                continue
            try:
                row1, col1, row2, col2 = map(int, move)
                if ((row1, col1), (row2, col2)) in legal_moves:
                    return ((row1, col1), (row2, col2))
                else:
                    print("Invalid move, please try again.")
            except ValueError:
                print("Invalid input. Please enter numeric values.")

# Running the game
game = ClobberGame()
game.play()