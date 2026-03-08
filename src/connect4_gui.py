import pygame
import numpy as np 

pygame.init()
ROWS = 6
COLS = 7
SQUARESIZE = 100
WIDTH = COLS * SQUARESIZE
HEIGHT = (ROWS + 1) * SQUARESIZE
RADIUS = SQUARESIZE // 2 - 5

class ConnectFourBoard:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((rows, cols))
        # self.board[rows - 1][0] = 1
        # self.board[rows - 1][1] = 2
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))


    def draw_board(self):
        for col in range(self.cols):
            for row in range(self.rows):
                pygame.draw.rect(self.screen, (0, 71, 187),
                                (col * SQUARESIZE, row * SQUARESIZE + SQUARESIZE,
                                SQUARESIZE, SQUARESIZE))
                color = (255, 255, 255)  # default color - white (empty space)
                if self.board[row][col] == 1:
                    color = (220,20,60)  # player 1 color - red
                elif self.board[row][col] == 2:
                    color = (255,215,0)  # player 2 color - yellow
                pygame.draw.circle(self.screen, color,
                                (col *SQUARESIZE + SQUARESIZE//2,
                                    row *SQUARESIZE + SQUARESIZE + SQUARESIZE//2),
                                RADIUS)
        pygame.display.update()

    def run(self):
        running = True
        while running:
            self.draw_board()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()


if __name__ == "__main__":
    board = ConnectFourBoard(rows=ROWS, cols=COLS)
    board.run()
