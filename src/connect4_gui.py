import pygame
import numpy as np 
from connect4_game import Connect4Game
import sys
import threading
import random
from player import AIPlayer

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
DARK_GREY = (40, 40, 40)
PLAYER_COLORS = {1: RED, 2: YELLOW}
PLAYER_NAMES = {1: "red", 2: "yellow"}

# game modes
HUMAN_VS_AI = "human_vs_ai"
AI_VS_AI = "ai_vs_ai"
# rate difficulty by how many simulations the AI will run before it makes its choice
DIFFICULTY = {
    "Easy": 100, 
    "Medium": 500, 
    "Hard": 1000
}

def _get_font(size):
    for name in ("Arial", "Helvetica", "Verdana", "DejaVu Sans", ""):
        try: 
            return pygame.font.SysFont(name, size)
        except Exception:
            continue
    return pygame.font.Font(None, size)

class Button:
    def __init__(self, label, rect, color=DARK_GREY, text_color=WHITE, font=None):
        self.label = label
        self.rect = rect 
        self.color = color
        self.hover_color = tuple(min(c + 40, 255) for c in color)
        self.text_color = text_color 
        self.font = font or _get_font(28)

    def draw(self, screen, mouse_pos):
        """
        Draws the button on the screen 
        """
        col = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, col, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        surf = self.font.render(self.label, True, self.text_color)
        screen.blit(surf, surf.get_rect(center=self.rect.center))

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def run_start_screen(screen):
    """
    Draws the start screen until the user has chosen the game mode and what color they want to play as
    (if its human vs ai)
    """
    font_title = _get_font(64)
    font_sub = _get_font(28)
    font_label = _get_font(22)

    # current state 
    mode = None
    human_color = None
    difficulty = None
    
    # buttom dims
    bw, bh = 260, 55
    cx = WIDTH // 2

    mode_buttons = {
        HUMAN_VS_AI: Button("Human vs. AI", 
                            pygame.Rect(cx - bw - 10, 160, bw, bh)),
        AI_VS_AI: Button("AI vs. AI", 
                         pygame.Rect(cx + 10, 160, bw, bh))
    }
    color_choice_buttons = {
        1: Button("Play as Red", 
                  pygame.Rect(cx - bw - 10, 290, bw, bh), text_color=RED),
        2: Button("Play as Yellow",
                  pygame.Rect(cx + 10, 290, bw, bh), text_color=YELLOW)
    }

    difficulty_buttons = {
        d: Button(d, pygame.Rect(cx - bw // 2 + (i - 1) * (bw // 2 + 55), 
                                 290 if mode == AI_VS_AI else 420,
                                 bw // 2 + 20, bh))
        for i, d in enumerate(DIFFICULTY)
    }
    
    clock = pygame.time.Clock()
    while True:
        mouse = pygame.mouse.get_pos()
        screen.fill(BLACK)

        t = font_title.render("Connect 4", True, WHITE)
        screen.blit(t, t.get_rect(center=(cx, 80)))

        for key, button in mode_buttons.items():
            if key == mode:
                button.color = BLUE
            else:
                button.color = DARK_GREY
            
            button.draw(screen, mouse)
        if mode == HUMAN_VS_AI:
            label = font_label.render("Choose your color:", True, LIGHT_GREY)
            screen.blit(label, label.get_rect(center=(cx, 265)))

        color_choice_made = (mode == AI_VS_AI) or (mode == HUMAN_VS_AI and human_color)

        if color_choice_made:
            diff_y = 370 if mode == AI_VS_AI else 500
            label = font_label.render("Difficulty:", True, LIGHT_GREY)
            screen.blit(label, label.get_rect(center=(cx, diff_y - 30)))
            for i, (d, button) in enumerate(difficulty_buttons.items()):
                button.rect.y = diff_y
                button.color = BLUE if d == difficulty else DARK_GREY
                button.draw(screen, mouse)

        if color_choice_made and difficulty:
            start_button = Button("Start Game", 
                                  pygame.Rect(cx - 100, HEIGHT - 100, 200, 55),
                                  color=BLUE)
            start_button.draw(screen, mouse)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # select mode 
                for key, button in mode_buttons.items():
                    if button.is_clicked(mouse):
                        mode = key
                        human_color = None
                        difficulty = None
                    if mode == HUMAN_VS_AI:
                        for key, button in color_choice_buttons.items():
                            if button.is_clicked(mouse):
                                human_color = key
                    if color_choice_made:
                        for d, button in difficulty_buttons.items():
                            if button.is_clicked(mouse):
                                difficulty = d

                    if color_choice_made and difficulty:
                        start_button = Button("Start Game", 
                                              pygame.Rect(cx - 100, HEIGHT - 100, 200, 55))
                        if start_button.is_clicked(mouse):
                            return {
                                "mode": mode,
                                "human_player": human_color,
                                "n_simulations": DIFFICULTY[difficulty]
                            }
        clock.tick(60)

class Connect4Board:
    def __init__(self, rows, cols, game, config):
        self.rows = rows
        self.cols = cols
        self.game: Connect4Game = game
        self.config = config

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Connect 4")

        self.font_lg = _get_font(60)
        self.font_med = _get_font(36)
        self.font_sm = _get_font(22)

        self.hover_col = None
        self.anim_speed = 8

        self.players = self._make_players()

        self._ai_thread = None
        self._ai_result = None
        self._ai_player = None

    def _make_players(self):
        """
        Returns either 2 AI players or 1 AI 1 Human based on user selection
        """
        n = self.config["n_simulations"]
        if self.config["mode"] == AI_VS_AI:
            return {1: AIPlayer(1, n), 2: AIPlayer(2, n)}
        hp = self.config["human_player"]
        ai_slot = 2 if hp == 1 else 1
        return {hp: None, ai_slot: AIPlayer(ai_slot, n)}

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

    def col_from_x(self, x):
        return x // SQUARESIZE
    
    def _do_drop(self, col):
        """
        Animates and drops a piece 
        """
        color = PLAYER_COLORS[self.game.player_turn]
        self._animate_drop(col, color)
        self.game.drop_piece(col)

    def _run_in_thread(self, player_obj):
        def task():
            self._ai_result = player_obj.get_move(self.game)

        self.ai_thread = threading.Thread(target=task)
        self.ai_thread.start()

    def _restart(self):
        self._ai_thread = None
        self._ai_result = None
        self._ai_player = None
        config = run_start_screen(self.screen)
        self.config = config 
        self.game = Connect4Game(
            rows=self.rows,
            cols=self.cols,
            board=np.zeros((self.rows, self.cols), dtype=int)
        )
        self.players = self._make_players(config)
        self.hover_col = None

    def run(self):
        clock = pygame.time.Clock()

        while True:
            current_player = self.players[self.game.player_turn]
            is_human = current_player is None
            thinking = self._ai_thread is not None and self._ai_thread.is_alive()

            if not self.game.is_terminal() and not is_human and not thinking:
                if self._ai_result is None:
                    self._ai_player = current_player
                    self._ai_thread = current_player._run_in_thread(self.game)

            if self._ai_thread is not None and not self._ai_thread.is_alive():
                col = self._ai_player.result
                self._ai_thread = None 
                self._ai_result = None
                self._ai_player = None 
                if col is not None and not self.game.is_terminal():
                    self._do_drop(col)
                

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
                if is_human and not self.game.is_terminal():
                    if event.type == pygame.MOUSEMOTION:
                        x, _ = event.pos
                        col = self.col_from_x(x)
                        self.hover_col = col if 0 <= col < self.cols else None

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, _ = event.pos
                        col = self.col_from_x(x)
                        if 0 <= col < self.cols and col in self.game.get_valid_moves():
                            self._do_drop(col)
            clock.tick(60)

if __name__ == "__main__":
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Connect 4")

    config = run_start_screen(screen)
    game = Connect4Game(ROWS, COLS, np.zeros((ROWS, COLS), dtype=int))
    board = Connect4Board(ROWS, COLS, game, config)
    board.run()