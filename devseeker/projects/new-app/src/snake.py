from __future__ import annotations

from dataclasses import dataclass, field

from .direction import Direction
from .position import Position


@dataclass
class Snake:
    """Snake model handling movement, growth, and collision checks."""

    body: list[Position] = field(default_factory=list)
    direction: Direction = Direction.RIGHT
    pending_growth: int = 0

    @classmethod
    def create_initial(cls, start: Position, length: int = 3) -> "Snake":
        """Create a snake with a given starting position and length."""
        body = [Position(start.x - i, start.y) for i in range(length)]
        return cls(body=body, direction=Direction.RIGHT)

    @property
    def head(self) -> Position:
        """Return the current head position."""
        return self.body[0]

    def set_direction(self, new_direction: Direction) -> None:
        """Update direction unless it would reverse into itself."""
        if new_direction != self.direction.opposite():
            self.direction = new_direction

    def move(self) -> None:
        """Advance the snake by one cell in the current direction."""
        dx, dy = self.direction.vector
        new_head = self.head.moved(dx, dy)
        self.body.insert(0, new_head)

        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1) -> None:
        """Queue growth to be applied on subsequent moves."""
        self.pending_growth += amount

    def occupies(self, position: Position) -> bool:
        """Check whether the snake occupies a given position."""
        return position in self.body

    def collides_with_self(self) -> bool:
        """Check whether the snake head overlaps its body."""
        return self.head in self.body[1:]