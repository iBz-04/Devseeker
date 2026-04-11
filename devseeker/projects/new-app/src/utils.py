from __future__ import annotations

from .position import Position


def clamp(value: int, minimum: int, maximum: int) -> int:
    """Clamp an integer to the provided range."""
    return max(minimum, min(maximum, value))


def grid_to_pixels(position: Position, grid_size: int) -> tuple[int, int]:
    """Convert a grid position to pixel coordinates."""
    return position.x * grid_size, position.y * grid_size


def pixels_to_grid(x: int, y: int, grid_size: int) -> Position:
    """Convert pixel coordinates to a grid position."""
    return Position(x // grid_size, y // grid_size)