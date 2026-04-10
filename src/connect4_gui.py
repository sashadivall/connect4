import pygame
import numpy as np 
from connect4_game import Connect4Game
from player import AIPlayer
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
    for name in ("Arial", "Helvetica", "Verdana", "DejaVu Sans", ""):
        try: 
            return pygame.font.SysFont(name, size)
        except Exception:
            continue
    return pygame.font.Font(None, size)


def make_ai_players(n_simulations: int) -> dict:
    return {
        1: AIPlayer(player_num=1, n_simulations=n_simulations),
        2: AIPlayer(player_num=2, n_simulations=n_simulations),
    }

class Connect4Board:
    def __init__(self, rows, cols, game, n_simulations=500):
        self.rows = rows
        self.cols = cols
        self.game: Connect4Game = game

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Connect 4")

        self.font_lg = _get_font(60)
        self.font_med = _get_font(36)
        self.font_sm = _get_font(22)

        self.hover_col = None
        self.anim_speed = 8
        self.n_simulations = n_simulations 
        self.players = make_ai_players(n_simulations)

        self.ai_thread = None
        self.ai_move = None

    def _draw_board(self):
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
        direction = self.game.last_shift
        if direction is None:
            return

        arrow = "-> RIGHT" if direction == "right" else "<- LEFT"
        message = f"Gravity shift: {arrow}"

        surf = self.font_sm.render(message, True, WHITE)
        rect = surf.get_rect(center=(WIDTH // 2, SQUARESIZE // 2))
        self.screen.blit(surf, rect)

    def _draw_status(self, message=None):
        if self.game.last_shift:
            self._draw_shift_notice()
            return

        if message:
            surf = self.font_sm.render(message, True, WHITE)

        elif self.ai_thread and self.ai_thread.is_alive():
            surf = self.font_sm.render("AI is thinking...", True, LIGHT_GREY)

        else:
            player = self.game.player_turn
            color = PLAYER_COLORS[player]
            name = PLAYER_NAMES[player]
            surf = self.font_sm.render(f"{name}'s turn", True, color)

        rect = surf.get_rect(center=(WIDTH // 2, SQUARESIZE // 2))
        self.screen.blit(surf, rect)

    def _draw_end_screen(self, winner):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0,0))
        
        if winner:
            msg = f"{PLAYER_NAMES[winner]} wins!"
            color = PLAYER_COLORS[winner]
        else:
            msg = "It's a draw!"
            color = LIGHT_GREY
        
        surf = self.font_lg.render(msg, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        self.screen.blit(surf, rect)

        restart = self.font_sm.render("Press R to restart | Q to quit", True, WHITE)
        rect2 = restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        self.screen.blit(restart, rect2)

    def _animate_drop(self, col, color):
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

            self.screen.fill(BLACK)
            self._draw_board()
            self._draw_status()

            pygame.draw.circle(self.screen, color, (cx, int(y)), RADIUS)
            pygame.display.update()
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
        self.ai_thread = None
        self.ai_move = None
        self.players = make_ai_players(self.n_simulations)  


    def run(self, players):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r:
                        self._restart()

            # AI turn logic
            if not self.game.is_terminal():

                current_player = self.game.player_turn
                player_obj = players[current_player]

                if self.ai_thread is None:
                    self.ai_thread = player_obj._run_in_thread(self.game)

                elif not self.ai_thread.is_alive():
                    col = player_obj.result

                    if col in self.game.get_valid_moves():
                        color = PLAYER_COLORS[current_player]
                        self._animate_drop(col, color)
                        self.game.drop_piece(col)

                    self.ai_thread = None
                    self.ai_move = None

            # Draw
            self.screen.fill(BLACK)
            self._draw_board()

            if not self.game.is_terminal():
                self._draw_status()
            else:
                winner = self.game.check_win()
                self._draw_end_screen(winner)

            pygame.display.update()
            clock.tick(60)


if __name__ == "__main__":
    game = Connect4Game(ROWS, COLS, np.zeros((ROWS, COLS), dtype=int))
    board = Connect4Board(ROWS, COLS, game, n_simulations=500)

    players = {
        1: AIPlayer(player_num=1, n_simulations=500),
        2: AIPlayer(player_num=2, n_simulations=500)
    }

    board.run(players)
