from __future__ import annotations

from enum import Enum


class Direction(Enum):
    """Cardinal movement directions for the snake."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def vector(self) -> tuple[int, int]:
        """Return the direction as a grid movement vector."""
        return self.value

    def opposite(self) -> "Direction":
        """Return the opposite direction."""
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        return opposites[self]