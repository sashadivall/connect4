import numpy as np
from src.connect4_game import Connect4Game
from src.mcts_agent import MCTSAgent


def make_game():
    """Creates a fresh empty 6x7 Connect 4 game."""
    return Connect4Game(rows=6, cols=7, board=np.zeros((6, 7), dtype=int))


def test_drop_piece():
    """Checks that pieces land in the correct row and turns alternate correctly."""
    game = make_game()
    game.drop_piece(3)  # Player 1
    game.drop_piece(3)  # Player 2
    assert game.board[5][3] == 1, "Player 1 should be at bottom of col 3"
    assert game.board[4][3] == 2, "Player 2 should be one above Player 1"
    assert game.player_turn == 1, "Should be Player 1's turn again"
    print("TEST 1 PASSED: drop_piece()")


def test_check_win():
    """Checks horizontal win detection for Player 1."""
    game = make_game()
    # set board directly to avoid triggering gravity shift via drop_piece
    game.board[5][0:4] = 1
    assert game.check_win() == 1, "Player 1 should have won horizontally"
    print("TEST 2 PASSED: check_win()")


def test_check_draw():
    """Checks that a full top row is correctly detected as a draw."""
    game = make_game()
    game.board[0] = [1, 2, 1, 2, 1, 2, 1]
    assert game.check_draw() == True, "Full top row should be detected as a draw"
    print("TEST 3 PASSED: check_draw()")


def test_gravity_shift():
    """Checks that pieces shift and re-settle to the bottom after a gravity shift."""
    game = make_game()
    game.board[5][0] = 1
    game.apply_gravity_shift()
    assert game.board.sum() > 0, "Piece should still exist after shift"
    assert game.board[5].sum() > 0, "Piece should settle to bottom row after gravity"
    print(f"TEST 4 PASSED: apply_gravity_shift() — direction was '{game.last_shift}'")


def test_clone():
    """Checks that clone() produces a fully independent copy of the game state."""
    game = make_game()
    game.drop_piece(0)
    clone = game.clone()
    clone.drop_piece(1)  # modify clone only
    assert (
        game.board[5][1] == 0
    ), "Original board must be untouched after modifying clone"
    print("TEST 5 PASSED: clone()")


def test_mcts_returns_valid_move():
    """Checks that the MCTS agent returns a legal move on an empty board."""
    game = make_game()
    agent = MCTSAgent(player=1, n_simulations=100)
    move = agent.best_move(game)
    assert move in game.get_valid_moves(), f"MCTS returned invalid move: {move}"
    print(f"TEST 6 PASSED: MCTSAgent.best_move() — chose column {move}")


def test_full_game():
    """Runs a complete AI vs AI game and checks it reaches a terminal state."""
    game = make_game()
    agents = {
        1: MCTSAgent(player=1, n_simulations=100),
        2: MCTSAgent(player=2, n_simulations=100),
    }

    move_count = 0
    while not game.is_terminal():
        current = game.player_turn
        move = agents[current].best_move(game)
        game.drop_piece(move)
        move_count += 1
        shift = f" [SHIFT {game.last_shift.upper()}]" if game.last_shift else ""
        print(f"  move {move_count:02d} | player {current} -> col {move}{shift}")

    winner = game.check_win()
    result = f"player {winner} wins" if winner else "draw"
    print(f"TEST 7 PASSED: full game completed in {move_count} moves — {result}")


if __name__ == "__main__":
    print("=" * 50)
    print("running connect4 tests")
    print("=" * 50)
    test_drop_piece()
    test_check_win()
    test_check_draw()
    test_gravity_shift()
    test_clone()
    test_mcts_returns_valid_move()
    test_full_game()

    print("all tests passed")
