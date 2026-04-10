# Connect 4 with Gravity Shift — MCTS AI

A fully autonomous Connect 4 implementation in Python featuring a Monte Carlo Tree Search (MCTS) AI engine, a real-time pygame GUI, and a stochastic gravity shift mechanic that periodically reshuffles the board. Two AI agents compete against each other without any human input required.

---

## Project Overview

This project extends the classic Connect 4 game with two core additions:

**MCTS-driven AI** — Rather than relying on a handcrafted heuristic, each player is powered by a Monte Carlo Tree Search agent that runs thousands of simulated playouts per turn to determine the statistically strongest move.

**Gravity Shift** — At each turn with 15% probability, the game board randomly shifts to the left or the right, a concept we call "gravity shift". All pieces slide to the tilt side and re-settle under gravity, forcing both agents to adapt to a constantly changing board state.

The game runs entirely autonomously: both players are AI-controlled, the GUI renders each move with a drop animation, and a restart/quit interface is provided for repeated play.

---

## Project Structure

```
connect4/
│
├── src/
│   ├── connect4_game.py     # Game logic: rules, win detection, gravity shift
│   ├── mcts_agent.py        # MCTS algorithm: selection, expansion, simulation, backpropagation
│   ├── player.py            # AIPlayer: thread management and agent interface
│   ├── connect4_gui.py      # pygame GUI: rendering, animation, main game loop
│   └── main.py              # Test suite: unit and integration tests
│
└── README.md
```

### Module Responsibilities

| File               | Responsibility                                                                   |
| ------------------ | -------------------------------------------------------------------------------- |
| `connect4_game.py` | Board state, move validation, win/draw detection, gravity shift logic            |
| `mcts_agent.py`    | UCB1-based tree search, random playout simulation, backpropagation               |
| `player.py`        | Wraps the MCTS agent in a background daemon thread so the GUI stays responsive   |
| `connect4_gui.py`  | Draws the board, animates piece drops, manages the AI turn loop, handles restart |
| `main.py`          | Seven automated tests covering core game logic and a full AI vs AI game          |

---

## Requirements

- Python 3.8 or higher
- pygame
- numpy

Install dependencies with:

```bash
pip install pygame numpy
```

---

## How to Run

### Run the Game

From the root `connect4/` directory:

```bash
python src/connect4_gui.py
```

A pygame window will open. Both players are AI-controlled so no mouse input is needed to play. The top bar displays whose turn it is and shows "AI is thinking..." while the MCTS agent computes its move.

### Run the Test Suite

```bash
python src/main.py
```

This runs seven tests covering piece placement, win detection, draw detection, gravity shift behaviour, game state cloning, MCTS move validity, and a complete AI vs AI game.

---

## Controls

| Key | Action           |
| --- | ---------------- |
| `R` | Restart the game |
| `Q` | Quit the game    |

---

## How It Works

### Game Logic — `connect4_game.py`

The `Connect4Game` class maintains the 6×7 board as a NumPy array. Player 1 is represented by `1`, Player 2 by `2`, and empty cells by `0`. Win detection checks all four directions (horizontal, vertical, and both diagonals) using a direction-stepping approach. The gravity shift is triggered every 7 turns via `maybe_trigger_shift()`, which calls `apply_gravity_shift()` to randomly tilt the board and re-settle all pieces under gravity.

### AI Engine — `mcts_agent.py`

The `MCTSAgent` implements the four-phase MCTS loop:

1. **Selection** — traverse the tree from the root, choosing the child with the highest UCB1 score at each step. UCB1 balances exploitation (winning moves) against exploration (less-visited moves) using the exploration constant C = √2.

2. **Expansion** — once a node with untried moves is reached, pick one at random and add it as a new child node.

3. **Simulation** — from the new node, play out the remainder of the game using uniformly random moves until a terminal state is reached.

4. **Backpropagation** — walk back up the tree, incrementing visit counts and crediting wins to the player who moved into each node.

After `n_simulations` iterations, the agent selects the most visited child of the root as its best move.

### Threading — `player.py`

MCTS is computationally expensive. Running it on the main thread would freeze the pygame window. `AIPlayer` wraps the agent so that `_run_in_thread()` spawns a daemon thread to compute `best_move()` in the background, storing the result in `self.result`. The GUI polls `thread.is_alive()` each frame and reads `player.result` once the thread completes — keeping the window fully responsive throughout.

### GUI & Main Loop — `connect4_gui.py`

`Connect4Board` manages all rendering and game flow. Each frame of the `run()` loop:

1. Checks if an AI thread is currently running — if not, spawns one via `player._run_in_thread()`.
2. If the thread has finished, reads `player.result`, animates the piece drop, and calls `game.drop_piece()`.
3. Redraws the board, updates the status bar, and checks for a terminal state.

On game end, an overlay displays the result and prompts the player to press `R` to restart or `Q` to quit. Restarting calls `_restart()`, which reinitialises both the board and the AI player objects via `make_ai_players()`, ensuring no stale thread state carries over between games.

---

## Configuration

The number of MCTS simulations per move can be adjusted in `connect4_gui.py`:

```python
board = Connect4Board(ROWS, COLS, game, n_simulations=500)
```

Higher values produce stronger play at the cost of longer thinking time. The gravity shift interval (default: every 7 turns) can be adjusted in `connect4_game.py`:

```python
self.shift_interval = 7
```

---

## Testing

The test suite in `main.py` covers the following scenarios:

1. **`test_drop_piece`** — verifies pieces land in the correct row and turns alternate correctly
2. **`test_check_win`** — verifies horizontal win detection
3. **`test_check_draw`** — verifies a full top row is detected as a draw
4. **`test_gravity_shift`** — verifies pieces survive and re-settle after a shift
5. **`test_clone`** — verifies `clone()` produces a fully independent copy of game state
6. **`test_mcts_returns_valid_move`** — verifies the agent returns a legal move on an empty board
7. **`test_full_game`** — runs a complete AI vs AI game and verifies it reaches a terminal state

---

## Authors

Authors
Developed as a collaborative group project by:

Ruchira Ravindra Karle
Sasha DiVall
Dhruhi Patel

Responsibilities were equally divided across the entire project.