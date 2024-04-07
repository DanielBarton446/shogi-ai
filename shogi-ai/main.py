"""

This is the main function for an example of how you can have two
agents play against each other. The agents are random agents, so
the game will be random.

This example with random moves also serves as a good example of
how viable monte carlo tree search would be for this game.
"""

import shogi
import sys
from environment import Environment
from random_agent import RandomAgent
from mcts_agent import MctsAgent
from shogi import Board, Move

sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)


def main() -> None:
    """
    Main function for the example.
    """
    board: Board = shogi.Board()

    agent1: MctsAgent = MctsAgent.from_board(board)
    env: Environment = agent1.env

    agent2: RandomAgent = RandomAgent(env, player=1)

    while not board.is_game_over():
        agent1_action: Move = agent1.select_action()
        board.push(agent1_action)
        print(f"Agent 1 move: {agent1_action}")
        print(f"Games simulated: {agent1.games_simulated}")
        print(board)
        print(f"Move: {len(board.move_stack)}")
        if board.is_game_over():
            break

        agent2_action: Move = agent2.select_action()
        board.push(agent2_action)

    print("Final State of board:")
    print(board)
    print(f"Number of moves {len(board.move_stack)}")
    with open("game.txt", "w") as f:
        for move in board.move_stack:
            f.write(str(move) + "\n")


if __name__ == "__main__":
    main()
