
import time
import random

from shogi import Board
from shogi import Move
from environment import Environment
from agent import Agent
from typing import Optional


class Node:
    # we are at first going to have a max depth of recorded
    # nodes of 1. This might be a bad idea, but we will see

    def __init__(self, move: Optional[Move], parent=None):
        self.move = move
        self.parent = parent
        self.explored_children = []
        self.visits = 1
        self.value = 0

        if parent:
            parent.explored_children.append(self)

        p = self.parent
        while p:
            p.visits += 1
            p = p.parent

    def get_child_from_move(self, move: Move):
        for child in self.explored_children:
            if child.move == move:
                return child
        return None


class MctsAgent(Agent):
    """
    Monte Carlo Tree Search Agent class for shogi.

    ```
    from shogi import Board
    from mcts_agent import MctsAgent

    board = Board()
    agent = MctsAgent.from_board(board, player=0)

    move: Move = agent.select_action(board)
    ```
    """

    def __init__(self, env: Environment, player: int, strategy=None):
        strategy = "mcts"
        self.time_limit = 5
        self.tree = Node(move=None, parent=None)
        self.games_simulated = 0
        super().__init__(env=env, player=player, strategy=strategy)

    def select_action(self):
        if self.player != self.env.board.turn:
            raise ValueError("Not the MCTS_AGENT's turn")

        self.tree = Node(move=None, parent=None)
        self.games_simulated = 0
        start_time = time.time()
        time_delta = 0

        while time_delta < self.time_limit:
            time_delta = time.time() - start_time
            self._simulation()
            self.games_simulated += 1

        best_node = max(self.tree.explored_children, key=lambda n: n.value)

        return best_node.move

    def _simulation(self):
        base_board = Board(self._env.board.sfen())
        node = self._expansion(board=base_board)
        if node.visits == 0:
            value = self._rollout(board_copy=base_board, move=node.move)
        else:
            board_after_explored_node = Board(base_board.sfen())
            board_after_explored_node.push(node.move)

            # need to consider when we pick a move that
            # loses us the game
            if board_after_explored_node.is_game_over():
                value = self._utility(board_after_explored_node)
                self._backpropagation(node, value)

            expanded_move = self._select_random_move(board=board_after_explored_node)
            value = self._rollout(board_copy=board_after_explored_node,
                                  move=expanded_move)

        self._backpropagation(node, value)

    def _rollout(self, board_copy: Board, move: Move) -> int:
        board_copy.push(move)

        while not board_copy.is_game_over():
            move = self._select_random_move(board_copy)
            board_copy.push(move)

        return self._utility(board_copy)

    def _utility(self, board_copy: Board):
        if board_copy.is_checkmate():
            if board_copy.turn != self.player:
                return 1
            else:
                return -1
        return 0

    def _backpropagation(self, node: Node, value: int):
        node.value += value

    def _select_random_move(self, board: Board) -> Move:
        moves = [move for move in board.legal_moves]
        return random.choice(moves)

    def _expansion(self, board: Board) -> Node:
        move = self._select_random_move(board)

        existing_node = self.tree.get_child_from_move(move)
        if existing_node:
            existing_node.visits += 1
            return existing_node

        node = Node(move, self.tree)
        return node

    @classmethod
    def from_board(cls, board: Board):
        return MctsAgent(env=Environment(board), player=board.turn)
