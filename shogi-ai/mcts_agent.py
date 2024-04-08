
import time
import random
import math

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
        self.children = []
        self.visits = 0
        self.value = 0

        if parent:
            parent.children.append(self)

    def get_child_from_move(self, move: Move):
        for child in self.children:
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
        self.positions_checked = 0
        self.rollouts = 0
        self.exploration_coefficient = 1.41
        super().__init__(env=env, player=player, strategy=strategy)

    def select_action(self):
        if self.player != self.env.board.turn:
            raise ValueError("Not the MCTS_AGENT's turn")

        self.tree = Node(move=None, parent=None)
        self.games_simulated = 0
        start_time = time.time()
        time_delta = 0

        # Seed initial expansion
        self._expansion(self.env.board, self.tree)

        while time_delta < self.time_limit or self.games_simulated < 1000:
            time_delta = time.time() - start_time
            node_to_simulate = self._selection()
            self._simulation(node_to_simulate)
            self.games_simulated += 1

        # select the immediate child (depth 1) with the most visits
        # as we revisit the most promising nodes
        best_node = max(self.tree.children, key=lambda n: n.visits)

        return best_node.move

    def _selection(self) -> Node:
        queue = []
        queue.extend(self.tree.children)
        max_uct_ucb1 = float("-inf")
        node_to_rollout = None

        while queue:
            current_node: Node = queue.pop(0)

            curr_node_visits = max(1, current_node.visits)
            tree_visits = max(1, self.tree.visits)

            uct_ucb1 = current_node.value / curr_node_visits + self.exploration_coefficient * math.sqrt(
                math.log(tree_visits) / curr_node_visits
            )
            if uct_ucb1 > max_uct_ucb1:
                max_uct_ucb1 = uct_ucb1
                node_to_rollout = current_node
            queue.extend(current_node.children)

        return node_to_rollout

    def _simulation(self, node_to_rollout: Node):
        board_copy = Board(self._env.board.sfen())

        # make all the moves to the board that got us to this node.
        moves_stack = []
        inspect = node_to_rollout
        while inspect.parent:
            moves_stack.append(inspect.move)
            inspect = inspect.parent
        while moves_stack:
            board_copy.push(moves_stack.pop())

        if node_to_rollout.visits == 0:
            value = self._rollout(board_copy=board_copy)
        else:
            self._expansion(board_copy, node_to_rollout)
            value = self._rollout(board_copy=board_copy)

        self._backpropagation(node_to_rollout, value)

    def _rollout(self, board_copy: Board) -> int:
        # we just play moves after we get to the current move position
        self.rollouts += 1

        while not board_copy.is_game_over() and board_copy.move_number < 100:
            new_random_move = self._random_move(board_copy)
            board_copy.push(new_random_move)

        return self._utility(board_copy)

    def _utility(self, board_copy: Board):
        if board_copy.is_checkmate():
            if board_copy.turn != self.player:
                return 1
            else:
                return -1
        return 0

    def _backpropagation(self, leaf_node: Node, value: int):
        leaf_node.value += value
        p = leaf_node.parent
        while p:
            p.visits += 1
            p.value += value
            p = p.parent

    def _random_move(self, board: Board) -> Move:
        self.positions_checked += 1
        moves = [move for move in board.pseudo_legal_moves]
        move = None
        while True:
            move = random.choice(moves)
            # only need to ensure we dont win with dropping a pawn
            if not board.was_check_by_dropping_pawn(move):
                break
        return move

    def _expansion(self, board: Board, parent_node: Node) -> None:
        move = self._random_move(board)
        node = Node(move=move, parent=parent_node)

    @classmethod
    def from_board(cls, board: Board):
        return MctsAgent(env=Environment(board), player=board.turn)
