"""

This is the main function for an example of how you can have two
agents play against each other. The agents are random agents, so
the game will be random.

This example with random moves also serves as a good example of
how viable monte carlo tree search would be for this game.
"""

import shogi
from agents.mcts_agent import MctsAgent
from agents.random_agent import RandomAgent
from environments.environment import Environment
from shogi import Board, Move


def main() -> None:
    """
    Main function for the example.
    """
    board: Board = shogi.Board()

    agent1: MctsAgent = MctsAgent.from_board(board)
    env: Environment = agent1.env

    agent2: RandomAgent = RandomAgent(env, player=1)

    while not board.is_game_over():
        agent1_action: Move = agent1.select_action(board)
        board.push(agent1_action)
        print(f"Agent 1 move: {agent1_action}")
        print(f"Games simulated: {agent1.current_board_sims()}")
        print(board)
        print(f"Move: {len(board.move_stack)}")
        if board.is_game_over():
            break

        agent2_action: Move = agent2.select_action()
        board.push(agent2_action)

    print("Final State of board:")
    print(board)
    print(f"Player {board.turn} Lost!")
    print(f"Number of moves {len(board.move_stack)}")
    print(f"Simulated games: {agent1.total_games_simulated}")
    print(f"Rollouts: {agent1.rollouts}")
    print(f"Positions Checked: {agent1.positions_checked}")
    with open("game.txt", "w", encoding="utf-8") as f:
        for move in board.move_stack:
            f.write(str(move) + "\n")


if __name__ == "__main__":
    main()
