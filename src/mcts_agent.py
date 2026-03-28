import copy 
from connect4_game import *

###################### MCTS ALGORITHM ######################
# Works by running n_simulations of game play and learning what optimal moves are
# 1. Select state - traverse search tree starting from the root, choose child node with highest UCB1 score
# 2. Expand state - once we reach node with untried moves, pick a move at random, create a new child node representing that board state, and add it to the tree
# 3. Simulate state - from the newly expanded node, play out the rest of the game by making moves at random
###################### ############## ######################
class MCTSNode:
    def __init__(self, game_state: Connect4Game, parent=None, move=None):
        self.game_state = copy.deepcopy(game_state)
        self.parent = parent
        self.move = move  # most recent move 
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = self.game_state.get_valid_moves()


class MCTSAgent: 
    def __init__(self, player, n_simulations=500):
        self.player = player 
        self.n_simulations = n_simulations
        # exploration constant (how much to favor exploration over exploitation)
        self.C = np.sqrt(2)


    def select(self, node):
        raise NotImplementedError("implement me!")
    
    def expand(self, node):
        raise NotImplementedError("implement me!")
    
    def simulate(self, node):
        raise NotImplementedError("implement me!")
    
    def backpropagate(self, node, result):
        raise NotImplementedError("implement me!")
    
    def best_move(self, game):
        raise NotImplementedError("implement me!")




    