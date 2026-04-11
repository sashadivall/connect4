from src.connect4_game import Connect4Game
from src.connect4_gui import Connect4Board
from src.player import AIPlayer, RandomPlayer


def make_game():
    return Connect4Game(rows=6, cols=7, board=np.zeros((6, 7), dtype=int))


def play_and_record_wins(agent1, agent2, n_games=25):
    """
    Has the agents play against each other and returns the win results

    agent1: can be either AIPlayer or RandomPlayer
    agent2: can be either AIPlayer or RandomPlayer

    """
    # agent1 is red (player 1), agent2 is yellow (player 2)
    wins = {"red": 0, "yellow": 0, "draws": 0}
    agents = {1: agent1, 2: agent2}

    for game_num in range(n_games):
        game = make_game()

        while not game.is_terminal():
            current = game.player_turn
            player = agents[current]
            col = player.get_move(game)

            if col is not None and col in game.get_valid_moves():
                game.drop_piece(col)

        winner = game.check_win()
        if winner == 1:
            wins["red"] += 1
            print(f"  game {game_num+1} - red wins")
        elif winner == 2:
            wins["yellow"] += 1
            print(f"  game {game_num+1} - yellow wins")
        else:
            wins["draws"] += 1
            print(f"  game {game_num+1} - draw")

    return wins

def win_rate_by_sim(n_simulations, n_games=25):
    """
    Records the number of times the AI agent beats the random agent based on how many simulations 
    the AI agent runs for
    """
    pass




if __name__ == "__main__":
    n_games = 25

    # change these to experiment with different values
    sim_counts = [50, 200, 500, 1000]  

    # AI vs AI 
    print("AI vs AI (500 sims each)")
    r1 = play_and_record_wins(
        AIPlayer(player_num=1, n_simulations=500), 
        AIPlayer(player_num=2, n_simulations=500),  
        n_games
    )
    print(f"red wins: {r1['red']}  yellow wins: {r1['yellow']}  draws: {r1['draws']}")

    # AI vs AI unequal i.e  weak vs strong
    print("\nAI vs AI (100 sims vs 1000 sims)")
    print("-" * 40)
    r2 = play_and_record_wins(
        AIPlayer(player_num=1, n_simulations=100),   
        AIPlayer(player_num=2, n_simulations=1000),  
        n_games
    )
    print(f"red wins: {r2['red']}  yellow wins: {r2['yellow']}  draws: {r2['draws']}")

    # AI vs Random
    print("\nAI vs Random (500 sims)")
    print("-" * 40)
    win_rate_by_sim(n_simulations=500, n_games=n_games)

    # Random vs Random
    print("\nRandom vs Random")
    print("-" * 40)
    r3 = play_and_record_wins(RandomPlayer(), RandomPlayer(), n_games)
    print(f"red wins: {r3['red']}  yellow wins: {r3['yellow']}  draws: {r3['draws']}")

    # win rate by sim count vs random 
    print("\nwin rate by simulation count vs random")
    print("-" * 40)
    for sims in sim_counts:  
        win_rate_by_sim(n_simulations=sims, n_games=n_games)

    print("\ndone!")