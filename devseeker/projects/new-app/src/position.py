from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Position:
    """Immutable grid coordinate."""

    x: int
    y: int

    def moved(self, dx: int, dy: int) -> "Position":
        """Return a new position offset by the given delta."""
        return Position(self.x + dx, self.y + dy)