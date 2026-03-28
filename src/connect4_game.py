from connect4_gui import *


class Connect4Game:
    def __init__(self, rows, cols, board):
        # think about what variables we need to track
        # player turn?
        # we should structure this similar to hw1 - have a different file handle the AI stuff
        self.rows = rows
        self.cols = cols
        self.board = board
        self.player_turn = 1  # player 1 starts
        self.won = False

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
