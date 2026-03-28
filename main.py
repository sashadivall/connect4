import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from connect4_game import Connect4Game
from connect4_gui import Connect4GUI
from mcts_agent import MCTSAgent


if __name__ == '__main__':
    game = Connect4Game()
    agent1 = MCTSAgent(player=1, n_simulations=800)
    agent2 = MCTSAgent(player=2, n_simulations=800)
    gui = Connect4GUI(game, agent1, agent2)
    gui.run()
