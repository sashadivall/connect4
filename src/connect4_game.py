from src.connect4_gui import *
import random


class Connect4Game:
    def __init__(self, rows, cols, board):
        # think about what variables we need to track
        # player turn?
        # we should structure this similar to hw1 - have a different file handle the AI stuff
        self.turn_counter = 0
        # for now, we shift the board every 7 turns
        # eventually, we will shift the board with some probability at any given turn
        self.shift_interval = 7
        self.rows = rows
        self.cols = cols
        self.board = board
        self.player_turn = 1  # player 1 starts
        self.won = False
        self.last_shift = None

    def get_valid_moves(self):
        """
        Retrieves all legal moves from the current board state
        """
        # think about how we want to visually handle users choosing the wrong move
        valid_moves = []

        for col in range(self.cols):
            if self._is_valid_move(col):
                valid_moves.append(col)

        return valid_moves

    def _is_valid_move(self, col):
        return self.board[0][col] == 0

    def drop_piece(self, col):
        """
        Drops a piece corresponding to the current player in the
        chosen move
        Updates the board with the current players value
        """

        if not self._is_valid_move(col):
            raise ValueError(f"Column {col} is full")
        # find the most recently empty row
        i = self.board.shape[0] - 1
        while i >= 0:
            cur_cell = self.board[i][col]
            if cur_cell == 0:
                self.board[i][col] = self.player_turn
                break
            else:
                i -= 1
        # change player move
        self.player_turn = (self.player_turn % 2) + 1
        # increment turn count
        self.turn_counter += 1
        # trigger shift?
        self.last_shift = self.maybe_trigger_shift()

    def maybe_trigger_shift(self):
        """
        Called after every drop_piece()
        Applies gravity shift if the current turn is a multiple of the shfit interval 
        """
        if self.turn_counter % self.shift_interval == 0:
            self.apply_gravity_shift()
            return self.last_shift

        self.last_shift = None
        return None
       

    def check_win(self):
        # Returns the winning player (1 or 2), or None if no winner yet.
        for player in [1, 2]:
            if self.has_won(player):
                return player
        return None

    def check_draw(self):
        # checks if the game has ended in a tie
        return (self.board[0] != 0).all()

    def has_won(self, player):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        return any(
            self.check_direction(player, row, col, dr, dc)  # dr, dc are direction steps
            for row in range(self.rows)
            for col in range(self.cols)
            for dr, dc in directions
        )

    def check_direction(self, player, row, col, dr, dc):
        # Checks if there are 4 consecutive pieces for the given player, starts at row and col and direction dr,dc
        for i in range(4):
            r, c = row + dr * i, col + dc * i
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                return False
            if self.board[r][c] != player:
                return False
        return True

    def apply_gravity_shift(self):
        """Randomly shifts the board left or right, then re-applies gravity."""
        direction = random.choice(["left", "right"])
        self.last_shift = direction

        # Step 1: shift each row left or right by 1, wrapping pieces around
        shift_amount = 1 if direction == "right" else -1
        self.board = np.roll(self.board, shift_amount, axis=1)

        # Step 2: re-apply gravity column by column
        for col in range(self.cols):
            pieces = self.board[:, col][self.board[:, col] != 0]
            empty = self.rows - len(pieces)
            self.board[:, col] = np.concatenate([np.zeros(empty, dtype=int), pieces])

    def clone(self):
        """Deep copy of game state — required by MCTS."""
        new_game = Connect4Game(self.rows, self.cols, self.board.copy())
        new_game.player_turn = self.player_turn
        new_game.turn_counter = self.turn_counter
        new_game.won = self.won
        new_game.shift_interval = self.shift_interval
        new_game.last_shift = self.last_shift
        return new_game

    def is_terminal(self):
        """Returns True if the game is over (win or draw)."""
        return self.check_win() is not None or self.check_draw()


def main():
    rows = 6
    cols = 7
    board = np.zeros((rows, cols))
    game = Connect4Game(rows, cols, board)
    print(game.get_valid_moves())
    # winning vertically
    game.drop_piece(0)
    print(game.board)

    game.drop_piece(2)
    print(game.board)

    game.drop_piece(0)
    print(game.board)

    game.drop_piece(1)
    print(game.board)

    game.drop_piece(0)
    print(game.board)

    game.drop_piece(2)
    print(game.board)

    game.drop_piece(0)
    print(game.board)

    print(game.check_win())

    board = np.zeros((rows, cols))
    game = Connect4Game(rows, cols, board)
    # win horizontally
    game.drop_piece(0)
    game.drop_piece(1)

    game.drop_piece(0)
    game.drop_piece(2)

    # check that no one has won yet
    print(game.check_win())
    game.drop_piece(1)
    game.drop_piece(3)

    game.drop_piece(1)
    game.drop_piece(4)
    print(game.check_win())

    # win diagonally
    game.drop_piece(0)
    game.drop_piece(1)

    game.drop_piece(1)
    game.drop_piece(2)

    game.drop_piece(3)
    game.drop_piece(2)

    game.drop_piece(2)
    game.drop_piece(3)

    game.drop_piece(3)
    game.drop_piece(4)

    game.drop_piece(3)
    print(game.check_win())


if __name__ == "__main__":
    main()
