from __future__ import annotations

from dataclasses import dataclass
import random

from .position import Position
from .snake import Snake


@dataclass
class Food:
    """Food item that can respawn on empty grid cells."""

    position: Position

    @classmethod
    def spawn(cls, cols: int, rows: int, snake: Snake) -> "Food":
        """Spawn food at a random unoccupied grid cell."""
        available = [
            Position(x, y)
            for y in range(rows)
            for x in range(cols)
            if not snake.occupies(Position(x, y))
        ]
        if not available:
            raise RuntimeError("No available cells to spawn food.")
        return cls(position=random.choice(available))

    def respawn(self, cols: int, rows: int, snake: Snake) -> None:
        """Move food to a new random unoccupied cell."""
        self.position = Food.spawn(cols, rows, snake).position