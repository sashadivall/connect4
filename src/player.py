import threading 
from mcts_agent import MCTSAgent

class AIPlayer:
    def __init__(self, player_num, n_simulations):
        self.player_num = player_num
        self.agent = MCTSAgent(player=player_num, n_simulations=n_simulations)
        self.result = None
        self._thread = None

    def get_move(self, game):
        """
        Runs MCTSAgent.best_move() in the background and returns chosen column
        """
        self.result = None
        self._thread = self._run_in_thread(game)
        self._thread.join()
        return self.result 
    
    def _run_in_thread(self, game):
        """
        Spawns and starts a daemon thread that calls
        best_move()
        """
        def _task():
            self.result = self.agent.best_move(game)
        t = threading.Thread(target=_task, daemon=True)
        t.start()
        return t
    
    def is_thinking(self):
        """
        Returns True if the background thread is running
        """
        return self._thread is not None and self._thread.is_alive()