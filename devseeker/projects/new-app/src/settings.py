from dataclasses import dataclass


@dataclass(frozen=True)
class GameSettings:
    """Container for all game configuration values."""

    window_width: int = 800
    window_height: int = 600
    grid_size: int = 20
    fps: int = 12
    title: str = "Polished Snake"
    background_color: tuple[int, int, int] = (18, 18, 24)
    grid_color: tuple[int, int, int] = (30, 30, 40)
    snake_head_color: tuple[int, int, int] = (80, 220, 120)
    snake_body_color: tuple[int, int, int] = (50, 180, 90)
    food_color: tuple[int, int, int] = (235, 80, 80)
    text_color: tuple[int, int, int] = (240, 240, 245)
    panel_color: tuple[int, int, int] = (24, 24, 32)
    panel_border_color: tuple[int, int, int] = (70, 70, 90)
    game_over_overlay: tuple[int, int, int, int] = (0, 0, 0, 160)
    highscore_file: str = "highscore.txt"

    @property
    def cols(self) -> int:
        """Return the number of horizontal grid cells."""
        return self.window_width // self.grid_size

    @property
    def rows(self) -> int:
        """Return the number of vertical grid cells."""
        return self.window_height // self.grid_size