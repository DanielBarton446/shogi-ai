"""
Agent class is the base class for all agents.
"""

from environment import Environment
from shogi import Board


class Agent:
    """
    Agent is not a class itself, it is a base class for all agents.
    Agent should not be used for anything other than inheritance.
    """

    def __init__(self, env: Environment, player: int, strategy=None):
        self._env = env
        self.player = player
        self.strategy = strategy

    def select_action(self):
        """
        Select an action based on the state of the environment.

        NotImplementedError: This method must be implemented by the subclass
        """
        raise NotImplementedError("select_action method must be implemented")

    def action_space(self):
        """
        Get the action space of the environment.

        Returns:
            action_space: The action space of the environment.
        """
        return self._env.action_space

    @classmethod
    def from_board(cls, board: Board):
        """
        Generate an agent from a shogi board.
        """
        raise NotImplementedError("from_board method must be implemented")

    @property
    def env(self):
        """
        env: The environment the agent operates in.
        """
        return self._env
