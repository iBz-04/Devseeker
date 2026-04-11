from src.direction import Direction
from src.position import Position
from src.snake import Snake


def test_snake_moves_forward() -> None:
    """Snake should advance one cell in its current direction."""
    snake = Snake.create_initial(Position(5, 5), length=3)
    snake.move()
    assert snake.head == Position(6, 5)
    assert len(snake.body) == 3


def test_snake_grows_on_next_moves() -> None:
    """Growth should be applied over subsequent moves."""
    snake = Snake.create_initial(Position(5, 5), length=3)
    snake.grow(2)
    snake.move()
    snake.move()
    assert len(snake.body) == 5


def test_snake_prevents_reverse_direction() -> None:
    """Snake should not be able to reverse directly into itself."""
    snake = Snake.create_initial(Position(5, 5), length=3)
    snake.set_direction(Direction.LEFT)
    assert snake.direction == Direction.RIGHT


def test_snake_self_collision_detected() -> None:
    """Self collision should be detected when head overlaps body."""
    snake = Snake(
        body=[
            Position(2, 2),
            Position(2, 3),
            Position(3, 3),
            Position(3, 2),
        ],
        direction=Direction.RIGHT,
    )
    assert snake.collides_with_self() is False
    snake.body[0] = Position(3, 3)
    assert snake.collides_with_self() is True