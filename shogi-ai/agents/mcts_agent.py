"""

A monte-carlo tree search for playing shogi

"""

import concurrent.futures
import math
import os
import random
import time
from typing import List, Optional, Tuple

from agents.agent import Agent
from env.environment import Environment
from shogi import Board, Move
from util.common import get_logger

logger = get_logger(__name__)
logger.setLevel("DEBUG")


class Node:  # pylint: disable=too-few-public-methods
    """
    Node class for moves in the MCTS tree.
    """

    # we are at first going to have a max depth of recorded
    # nodes of 1. This might be a bad idea, but we will see

    def __init__(self, move: Optional[Move], parent=None):
        self.move = move
        self.parent = parent
        self.children: List[Node] = []
        self.visits = 0
        self.value = 0
        self.ucb1 = float("inf")
        self.expanded = False

        if parent:
            parent.children.append(self)

    def get_child_from_move(self, move: Move):
        """
        Fetch a child move if it exists for the given move.
        """
        all_children = self.all_subchild_nodes()
        for child in all_children:
            if child.move == move:
                return child
        # logger.warning(f"Couldn't find {move} in current tree:\n {[node.move for node in self.all_subchild_nodes()]}")
        return None

    def all_subchild_nodes(self) -> List["Node"]:
        """
        returns a list of all subchild nodes. EXCLUDING the root.
        """
        bfs_queue = [self]
        nodes = []
        while bfs_queue:
            current_node = bfs_queue.pop()
            nodes.append(current_node)
            bfs_queue.extend(current_node.children)
        nodes.remove(self)  # remove the root node

        return nodes

    def __repr__(self):
        msg = f"Node from -- Move: {self.move} - Visits: {self.visits}\n"
        for child in self.children:
            msg += f"{[str(child.move) for child in self.children]}\n"
        return msg


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
        self.time_limit = 10
        self.tree = Node(move=None, parent=None)
        self.total_games_simulated = 0
        self.positions_checked = 0
        self.rollouts = 0
        self.exploration_coefficient = 1.41
        super().__init__(env=env, player=player, strategy=strategy)

    def current_board_sims(self) -> int:
        return self.tree.visits

    def select_action(self, board: Optional[Board] = None) -> Move:
        self._env.board = board or self._env.board

        if self.player != self.env.board.turn:
            raise ValueError("Not the MCTS_AGENT's turn")

        self.tree = Node(move=None, parent=None)
        start_time = time.time()
        time_delta = 0.0

        # Seed initial expansion
        self._expansion(self.env.board, self.tree)

        # this really shouldn't be done here, and should be a config
        num_workers = 1
        number_of_cores = os.cpu_count()
        if number_of_cores:
            num_workers = number_of_cores - 2

        while time_delta < self.time_limit:
            time_delta = time.time() - start_time
            with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
                futures = []
                for proc in range(num_workers):
                    futures.append(executor.submit(self._simulation, self._selection([self.tree])))
                results = [future.result() for future in concurrent.futures.as_completed(futures, self.time_limit)]
            for res in results:
                self._backpropagation(self.tree.get_child_from_move(res[0]), res[1])

            logger.debug("%s", [child.visits for child in self.tree.children])

        self.total_games_simulated += self.current_board_sims()
        logger.info("Games simulated: %i", self.tree.visits)

        # select the immediate child (depth 1) with the most visits
        # as we revisit the most promising nodes
        best_node = max(self.tree.children, key=lambda n: n.visits)
        logger.info("Selected move: %s", best_node.move)

        return best_node.move

    def _selection(self, nodes: List[Node]) -> Node:
        selection_queue: List[Node] = []
        for node in nodes:
            selection_queue.extend(node.all_subchild_nodes())
        random.shuffle(selection_queue)

        max_uct_ucb1 = float("-inf")
        node_to_rollout = None

        while selection_queue:
            current_node: Node = selection_queue.pop()

            # if current_node.visits == 0:
            #     return current_node
            visits = max(1, current_node.visits)
            tree_visits = max(1, self.tree.visits)

            uct_ucb1 = (
                current_node.value / visits
                + self.exploration_coefficient
                * math.sqrt(math.log(tree_visits) / visits)
            )
            current_node.ucb1 = uct_ucb1
            if uct_ucb1 > max_uct_ucb1:
                max_uct_ucb1 = uct_ucb1
                node_to_rollout = current_node
            selection_queue.extend(current_node.children)

        if node_to_rollout is None:
            raise ValueError("No node to rollout")

        return node_to_rollout

    def _utility(self, board_copy: Board):
        if board_copy.is_checkmate():
            if board_copy.turn != self.player:
                return 1
            return -1
        return 0

    def _rollout(self, board_copy: Board) -> int:
        # we just play moves after we get to the current move position
        self.rollouts += 1

        while not board_copy.is_game_over():
            new_random_move = self._random_move(board_copy)
            board_copy.push(new_random_move)

        return self._utility(board_copy)

    def _simulation(self, node_to_rollout: Node) -> Tuple[Move, int]:
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
            self._expansion(board_copy, node_to_rollout.parent)
            value = self._rollout(board_copy=board_copy)

        return (node_to_rollout.move, value)

    def _backpropagation(self, leaf_node: Node, value: int):
        leaf_node.value += value
        leaf_node.visits += 1  # turn out its important to say we visited this node
        p = leaf_node.parent
        while p:
            p.visits += 1
            p.value += value
            p = p.parent

    def _random_move(self, board: Board) -> Move:
        self.positions_checked += 1
        moves = list(board.pseudo_legal_moves)
        move = None
        while True:
            move = random.choice(moves)
            # only need to ensure we dont win with dropping a pawn
            if not board.was_check_by_dropping_pawn(move):
                break
        return move

    def _expansion(self, board: Board, parent_node: Node) -> None:
        # Seems really gross that we have to check if this layer
        # of the tree has already been expanded. We might
        # be able to just check if the move is fetchable already in
        # the tree and by that assertion we can know that we dont
        # need to create new nodes.
        if parent_node.expanded:
            return

        for legal_move in board.legal_moves:
            if self.tree.get_child_from_move(legal_move) is not None:
                logger.warning(
                    "Already expanded this legal move somehow: %s", legal_move
                )
                continue
            Node(move=legal_move, parent=parent_node)
        parent_node.expanded = True

    @classmethod
    def from_board(cls, board: Board):
        return MctsAgent(env=Environment(board), player=board.turn)
