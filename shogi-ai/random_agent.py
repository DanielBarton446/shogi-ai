"""
Random Agent:
- This agent selects a random move from the action space.
- This agent will be used for monte carlo tree search.

"""

import random

from agent import Agent
from environment import Environment
from shogi import Board
from shogi.Move import Move
from typing import Optional


class RandomAgent(Agent):
    """
    Random Agent class for shogi.

    ```
    from shogi import Board
    from random_agent import randomAgent

    board = Board()
    agent = randomAgent.from_board(board)

    move: Move = agent.select_action(board)
    ```
    """

    def __init__(self, env: Environment, player: int, strategy=None):
        strategy = "random"
        super().__init__(env=env, player=player, strategy=strategy)

    def select_action(self, board: Optional[Board] = None) -> Move:
        if self.player != self.env.board.turn:
            raise ValueError("Not the player's turn")
        legal_moves = self._env.action_space
        return random.choice(legal_moves)

    @classmethod
    def from_board(cls, board: Board):
        return RandomAgent(Environment(board), player=board.turn)
