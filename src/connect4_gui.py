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

class Button:
    def __init__(self, label, rect, color=GREY, text_color=WHITE, font=None):
        self.label = label
        self.rect = pygame.Rect(rect)
        self.color = color
        self.hover_color = tuple(min(c + 40, 255) for c in color)
        self.text_color = text_color
        self.font = font or _get_font(28)

    def draw(self, screen, mouse_pos):
        col = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, col, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        surf = self.font.render(self.label, True, self.text_color)
        screen.blit(surf, surf.get_rect(center=self.rect.center))

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
def run_start_screen(screen):
    """
    Home screen where user picks a mode and clicks start
    """
    font_title = _get_font(64)
    font_label = _get_font(22)

    cx = WIDTH // 2
    mode = None
    # whether the user wants to be red or yellow
    color_choice = None

    # button dims
    bw, bh = 260, 55  

    mode_buttons = {
        "human_vs_ai": Button("Human vs AI", (cx - bw - 10, 160, bw, bh)),
        "ai_vs_ai": Button("AI vs AI", (cx + 10, 160, bw, bh))
    }   
    color_choice_buttons = {
        1: Button("Play as Red", (cx - bw - 10, 290, bw, bh), text_color=RED),
        2: Button("Play as Yellow", (cx + 10, 290, bw, bh), text_color=YELLOW)
    }   

    start_button = Button("Start Game", (cx - 100, HEIGHT - 110, 200, 55), color=BLUE)

    clock = pygame.time.Clock()
    while True:
        mouse = pygame.mouse.get_pos()
        screen.fill(BLACK)

        t = font_title.render("Connect 4", True, WHITE)
        screen.blit(t, t.get_rect(center=(cx, 80)))

        for key, button in mode_buttons.items():
            button.color = BLUE if key == mode else GREY
            button.draw(screen, mouse)

        if mode == "human_vs_ai":
            label = font_label.render("Choose your color:", True, LIGHT_GREY)
            screen.blit(label, label.get_rect(center=(cx, 262)))
            for key, button in color_choice_buttons.items():
                button.color = BLUE if key == color_choice else GREY
                button.draw(screen, mouse)

        ready = (mode == "ai_vs_ai") or (mode == "human_vs_ai" and color_choice is not None)
        if ready:
            start_button.draw(screen, mouse)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for key, button in mode_buttons.items():
                    if button.is_clicked(mouse):
                        mode = key
                        color_choice = None
                
                if mode == "human_vs_ai":
                    for key, button in color_choice_buttons.items():
                        if button.is_clicked(mouse):
                            color_choice = key

                if ready and start_button.is_clicked(mouse):
                    return {
                        "mode": mode,
                        "human_player" : color_choice
                    }
        clock.tick(60)


def make_ai_players(n_simulations: int):
    return {
        1: AIPlayer(player_num=1, n_simulations=n_simulations),
        2: AIPlayer(player_num=2, n_simulations=n_simulations),
    }

class Connect4Board:
    def __init__(self, screen, rows, cols, game, config, n_simulations=500):
        self.screen = screen
        self.rows = rows
        self.cols = cols
        self.game: Connect4Game = game
        self.config = config

        # self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Connect 4")

        self.font_lg = _get_font(60)
        self.font_med = _get_font(36)
        self.font_sm = _get_font(22)

        self.hover_col = None
        self.anim_speed = 8
        self.n_simulations = n_simulations 
        self.players = self._make_players(config, n_simulations)

        self.ai_thread = None
        self.ai_player = None

    def _make_players(self, config, n_simulations):
        """
        Sets up the players based on the config chosen at the beginning of the game
        """
        if config["mode"] == "ai_vs_ai":
            return {1: AIPlayer(1, n_simulations), 2: AIPlayer(2, n_simulations)}
        human_player = config["human_player"]
        ai = 2 if human_player == 1 else 1
        return {human_player: None, ai: AIPlayer(ai, n_simulations)}
    
    def _draw_hover(self):
        self.screen.fill(BLACK, (0, 0, WIDTH, SQUARESIZE))
        is_human = self.players[self.game.player_turn] is None
        if is_human and self.hover_col is not None and not self.game.is_terminal():
            color = PLAYER_COLORS[self.game.player_turn]
            cx = self.hover_col * SQUARESIZE + SQUARESIZE // 2
            pygame.draw.circle(self.screen, color, (cx, SQUARESIZE // 2), RADIUS)

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

    def _do_drop(self, col):
        """
        Drops the piece with the animation
        """
        color = PLAYER_COLORS[self.game.player_turn]
        self._animate_drop(col, color)
        self.game.drop_piece(col)



    def _restart(self):  
        """
        Reset the game to a starting state without reopening the window
        """
        self.ai_thread = None
        self.ai_move = None
        config = run_start_screen(self.screen)
        self.game = Connect4Game(
            rows=self.rows,
            cols=self.cols,
            board=np.zeros((self.rows, self.cols), dtype=int)
        )
        self.hover_col = None
        self.players = self._make_players(config, self.n_simulations)


    def run(self):
        clock = pygame.time.Clock()

        while True:
            current_player = self.game.player_turn
            is_human = self.players[current_player] is None
            thinking = self.ai_thread is not None and self.ai_thread.is_alive()

            if not self.game.is_terminal() and not is_human and not thinking:
                self.ai_player = self.players[current_player]
                self.ai_thread = self.ai_player._run_in_thread(self.game)

            if self.ai_thread is not None and not self.ai_thread.is_alive():
                col = self.ai_player.result
                self.ai_thread = None
                self.ai_player = None
                if col is not None and not self.game.is_terminal():
                    self._do_drop(col)

            for event in pygame.event.get() :
                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r:
                        self._restart()

                if is_human and not self.game.is_terminal():
                    if event.type == pygame.MOUSEMOTION:
                        x, _ = event.pos
                        col = x // SQUARESIZE
                        self.hover_col = col if 0 <= col < self.cols else None

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, _ = event.pos
                        col = x // SQUARESIZE
                        if 0 <= col < self.cols and col in self.game.get_valid_moves():
                            self._do_drop(col)


            # # AI turn logic
            # if not self.game.is_terminal():

            #     current_player = self.game.player_turn
            #     player_obj = players[current_player]

            #     if self.ai_thread is None:
            #         self.ai_thread = player_obj._run_in_thread(self.game)

            #     elif not self.ai_thread.is_alive():
            #         col = player_obj.result

            #         if col in self.game.get_valid_moves():
            #             color = PLAYER_COLORS[current_player]
            #             self._animate_drop(col, color)
            #             self.game.drop_piece(col)

            #         self.ai_thread = None
            #         self.ai_move = None

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
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Connect 4")

    config = run_start_screen(screen)
    game = Connect4Game(ROWS, COLS, np.zeros((ROWS, COLS), dtype=int))
    board = Connect4Board(screen, ROWS, COLS, game, config, n_simulations=100)

    board.run()
