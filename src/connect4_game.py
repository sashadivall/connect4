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
        pass

    def _is_valid_move(self, col):
        return self.board[0][col] == 0



    def drop_piece(self, col):
        """
        Drops a piece corresponding to the current player in the 
        chosen move 
        Updates the board with the current players value 
        """

        if self._is_valid_move(col):
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
        """
        Checks if, after the most recent move, a player has won
        return winning player 
        """
        pass 


def main():
    rows = 6
    cols = 7
    board = np.zeros((rows, cols))
    game = Connect4Game(rows, cols, board)

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

if __name__ == '__main__':
    main()
    