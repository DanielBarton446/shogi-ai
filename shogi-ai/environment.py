"""
You can use the Environment class to generate an environment from a shogi board

```
from shogi import Board
from environment import Environment

board = Board()
env = Environment(board)
```

"""

from shogi import Board


class Environment:
    """
    Environment class for a shogi board.
    """
    def __init__(self, board: Board):
        self.board = board
        self._moves = []
        self._last_state = board.piece_bb

    @property
    def action_space(self):
        """
        generate all legal moves if we haven't already and
        return them
        """
        if self._moves and (self.board == self._last_state):
            return self._moves

        self._moves = []
        self._last_state = self.board.piece_bb
        for move in self.board.legal_moves:
            self._moves.append(move)
        return self._moves

    def from_board(self, board: Board):
        """
        currently just is another constructor basically.
        """
        return Environment(board)
