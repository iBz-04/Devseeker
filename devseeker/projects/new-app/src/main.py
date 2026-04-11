from __future__ import annotations

from .game import SnakeGame


def main() -> None:
    """Program entrypoint."""
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()