import copy 
from connect4_game import *
import random
import numpy as np

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

    def _is_terminal_state(self, node: MCTSNode):
        """
        Checks if the given node is terminal (win/lose or draw)
        """
        return node.game_state.check_win() is not None or node.game_state.check_draw()
    
    def _ucb1_score(self, node: MCTSNode):
        """
        Calculates the UCB1 score for a given node
        """
        if node.visits == 0:
            return float('inf')
        return (node.wins / node.visits) + self.C * np.sqrt((np.log(node.parent.visits) / node.visits))

    def select(self, node: MCTSNode):
        """
        Selects a node from the current game tree based on the highest UCB1 score
        """
        while not self._is_terminal_state(node):
            if node.untried_moves:
                return node 
            else:
                node = max(node.children, key = lambda child: self._ucb1_score(child))

        return node
        
    
    def expand(self, node: MCTSNode):
        """
        Expands hte given node and updates the tree with its children
        """
        # select a move from children at random
        random_move = random.choice(node.untried_moves)
        # remove that move from untried moves
        node.untried_moves.remove(random_move)

        # drop piece into random valid move
        state = copy.deepcopy(node.game_state)
        state.drop_piece(random_move)

        new_node = MCTSNode(game_state=state, parent=node, move=random_move)
        node.children.append(new_node)

        return new_node

    
    
def simulate(self, node: MCTSNode):
    """
    From this node, play random moves until the game ends.
    Returns the winning player (1 or 2), or 0 for a draw..
    Gravity shift fires automatically inside drop_piece() during rollout.
    """
    sim = copy.deepcopy(node.game_state)  

    while not sim.is_terminal():
        moves = sim.get_valid_moves()
        sim.drop_piece(random.choice(moves))

    winner = sim.check_win()
    return winner if winner is not None else 0  # 0 = draw
    
    
def backpropagate(self, node: MCTSNode, result):
    """
    Walk from this node back up to the root.
    Every node gets +1 visit.
    A node gets +1 win if the player who moved INTO that node is the winner.
    After drop_piece(), player_turn has already switched to the NEXT player,
    so we reverse it to find who actually just moved.
    """
    while node is not None:
        node.visits += 1
        # player_turn already flipped after drop_piece(), so reverse to get who just moved
        player_who_moved = (node.game_state.player_turn % 2) + 1
        if result == player_who_moved:
            node.wins += 1
        node = node.parent
    
    def best_move(self, game):
        """
        Run MCTS and return best column.
        """
        root = MCTSNode(game_state=game)

        for _ in range(self.n_simulations):
            # 1. Selection
            node = self.select(root)

            # 2. Expansion
            if not self._is_terminal_state(node) and node.untried_moves:
                node = self.expand(node)

            # 3. Simulation
            result = self.simulate(node)

            # 4. Backpropagation
            self.backpropagate(node, result)

        # fallback (safety)
        if not root.children:
            valid_moves = game.get_valid_moves()
            return random.choice(valid_moves) if valid_moves else None

        # choose most visited move
        best_child = max(root.children, key=lambda child: child.visits)
        return best_child.move
    




    