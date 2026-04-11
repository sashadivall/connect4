from src.connect4_game import Connect4Game
from src.connect4_gui import Connect4Board
from src.player import AIPlayer, RandomPlayer

def play_and_record_wins(agent1, agent2, n_games=25):
    """
    Has the agents play against each other and returns the win results

    agent1: can be either AIPlayer (MCTS) or RandomPlayer
    agent2: can be either AIPlayer (MCTS) or RandomPlayer

    This function should be called three times, once for each combination of 
    AI vs AI
    AI vs Random
    Random vs Random
    """
    pass 

def win_rate_by_sim(n_simulations, n_games=25):
    """
    Records the number of times the AI agent beats the random agent based on how many simulations 
    the AI agent runs for
    """
    pass