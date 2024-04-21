"""

This contains the mapping used for
the Grimbergen evaluation of pieces.

"""

from shogi import (
    BISHOP,
    GOLD,
    KNIGHT,
    LANCE,
    PAWN,
    PROM_BISHOP,
    PROM_KNIGHT,
    PROM_LANCE,
    PROM_PAWN,
    PROM_ROOK,
    PROM_SILVER,
    ROOK,
    SILVER,
)

GRIMBERGEN = {
    PAWN: 1,
    LANCE: 3,
    KNIGHT: 3,
    SILVER: 5,
    GOLD: 5,
    BISHOP: 8,
    ROOK: 9,
    PROM_PAWN: 5,
    PROM_LANCE: 5,
    PROM_KNIGHT: 5,
    PROM_SILVER: 5,
    PROM_BISHOP: 12,
    PROM_ROOK: 13,
}
