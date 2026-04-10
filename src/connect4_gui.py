import pygame
import numpy as np 
from connect4_game import Connect4Game
import sys

pygame.init()

# constants
ROWS = 6
COLS = 7
SQUARESIZE = 100
WIDTH = COLS * SQUARESIZE
HEIGHT = (ROWS + 1) * SQUARESIZE
RADIUS = SQUARESIZE // 2 - 5

BLUE = (0, 71, 187)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
GREY = (40, 40, 40)
LIGHT_GREY = (180, 180, 180)
PLAYER_COLORS = {1: RED, 2: YELLOW}
PLAYER_NAMES = {1: "red", 2: "yellow"}

def _get_font(size):
    """
    Returns a font that exists across all OS
    """
    for name in ("Arial", "Helvetica", "Verdana", "DejaVu Sans", ""):
        try: 
            f = pygame.font.SysFont(name, size)
            return f
        except Exception:
            continue
    return pygame.font.Font(None, size)

class Connect4Board:
    def __init__(self, rows, cols, game):
        self.rows = rows
        self.cols = cols
        self.game: Connect4Game = game
        # self.board[rows - 1][0] = 1
        # self.board[rows - 1][1] = 2
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Connect 4")

        self.font_lg = _get_font(60)
        self.font_med = _get_font(36)
        self.font_sm = _get_font(22)

        self.hover_col = None # column that our mouse is hovering over
        # animation speed for how fast the piece falls
        self.anim_speed = 8

    def _draw_hover(self):
        """
        Draws a floating piece over the column where the user's mouse is hovering
        """
        self.screen.fill(BLACK, (0, 0, WIDTH, SQUARESIZE))
        if self.hover_col is not None and not self.game.is_terminal():
            color = PLAYER_COLORS[self.game.player_turn]
            cx = self.hover_col * SQUARESIZE + SQUARESIZE // 2
            cy = SQUARESIZE // 2
            pygame.draw.circle(self.screen, color, (cx, cy), RADIUS)

    def _draw_board(self):
        """
        Draws the blue frame and all dropped pieces 
        """
        board = self.game.board
        for col in range(self.cols):
            for row in range(self.rows):
                pygame.draw.rect(self.screen, BLUE,
                                (col * SQUARESIZE, row * SQUARESIZE + SQUARESIZE,
                                SQUARESIZE, SQUARESIZE))
                color = PLAYER_COLORS.get(board[row][col], WHITE)
                cx = col * SQUARESIZE + SQUARESIZE // 2
                cy = row * SQUARESIZE + SQUARESIZE + SQUARESIZE // 2
                pygame.draw.circle(self.screen, color, (cx, cy), RADIUS)

    def _draw_shift_notice(self):
        """
        Shows user which direction the gravity shift went
        """
        direction = self.game.last_shift
        if direction is None:
            return
        arrow = "-> RIGHT" if direction == "right" else "<- LEFT"
        message = f"Gravity shift: {arrow}"
        surf = self.font_sm.render(message, True, WHITE)
        rect = surf.get_rect(center=(WIDTH // 2, SQUARESIZE // 2))
        self.screen.blit(surf, rect)

    def _draw_status(self):
        """
        Show whose turn it is, or the gravity shift notice 
        """
        if self.game.last_shift:
            self._draw_shift_notice()
        else:
            player = self.game.player_turn
            color = PLAYER_COLORS[player]
            name = PLAYER_NAMES[player]
            surf = self.font_sm.render(f"{name}'s turn", True, color)
            rect = surf.get_rect(center=(WIDTH // 2, SQUARESIZE // 2))
            self.screen.blit(surf, rect)
    
    def _draw_end_screen(self, winner):
        """
        Overlay a translucent panel with the result and a restart prompt
        """
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0,0))
        
        if winner:
            win_msg = f"{PLAYER_NAMES[winner]} wins!"
            color = PLAYER_COLORS[winner]
        else:
            win_msg = "It's a draw!"
            color = LIGHT_GREY
        
        surf = self.font_lg.render(win_msg, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        self.screen.blit(surf, rect)

        restart_msg = self.font_sm.render("Press R to restart | Q to quit", True, WHITE)
        srct = restart_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        self.screen.blit(restart_msg, srct)

    def _animate_drop(self, col, color):
        """
        Animate a piece falling 
        """
        landing_row = None
        for r in range(self.rows - 1, -1, -1):
            if self.game.board[r][col] == 0:
                landing_row = r
                break
        if landing_row is None:
             return 
            
        cx = col * SQUARESIZE + SQUARESIZE // 2
        y = float(SQUARESIZE // 2)
        target_y = float(landing_row * SQUARESIZE + SQUARESIZE + SQUARESIZE // 2)
        step = SQUARESIZE * self.anim_speed / 60

        clock = pygame.time.Clock()
        while y < target_y:
            y = min(y + step, target_y)

            self.screen.fill((0, 0, 0))
            self._draw_board()
            self._draw_status()

            pygame.draw.circle(self.screen, color, (cx, int(y)), RADIUS)
            pygame.display.update()
            clock.tick(60)


    def render(self):
        self.screen.fill(BLACK)
        self._draw_hover()
        self._draw_board()
        if not self.game.is_terminal():
            self._draw_status()
        else:
            winner = self.game.check_win()
            self._draw_end_screen(winner)
        pygame.display.update()


    def col_from_x(self, x):
        return x // SQUARESIZE
    
    def run(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():

                # on quit
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # key actions
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r:
                        self._restart()

                # mouse hovering 
                if event.type == pygame.MOUSEMOTION:
                    x, _ = event.pos
                    col = self.col_from_x(x)
                    self.hover_col = col if 0 <= col < self.cols else None
                # mouse click -> drop piece
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game.is_terminal():
                    x, _ = event.pos
                    col = self.col_from_x(x)
                    if 0 <= col < self.cols and col in self.game.get_valid_moves():
                        color = PLAYER_COLORS[self.game.player_turn]
                        self._animate_drop(col, color)
                        self.game.drop_piece(col)

            self.render()
            clock.tick(60)

    def _restart(self):
        """
        Reset the game to a starting state without reopening the window
        """
        self.game = Connect4Game(
            rows=self.rows,
            cols=self.cols,
            board=np.zeros((self.rows, self.cols), dtype=int)
        )
        self.hover_col = None

if __name__ == "__main__":
    game = Connect4Game(ROWS, COLS, np.zeros((ROWS, COLS), dtype=int))
    board = Connect4Board(ROWS, COLS, game)
    board.run()
