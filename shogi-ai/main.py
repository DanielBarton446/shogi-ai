"""

This is the main function for an example of how you can have two
agents play against each other. The agents are random agents, so
the game will be random.

This example with random moves also serves as a good example of
how viable monte carlo tree search would be for this game.
"""

import shogi
from shogi.Move import Move
from random_agent import RandomAgent


def main():
    """
    Main function for the example.
    """
    board = shogi.Board()

    agent1: RandomAgent = RandomAgent.from_board(board)
    env = agent1.env
    agent2: RandomAgent = RandomAgent(env)

    while not board.is_game_over():
        agent1_action: Move = agent1.select_action(board)
        board.push(agent1_action)
        if board.is_game_over():
            break

        agent2_action: Move = agent2.select_action(board)
        board.push(agent2_action)

    print("Final State of board:")
    print(board)
    print(f"Number of moves {len(board.move_stack)}")


if __name__ == "__main__":
    main()
