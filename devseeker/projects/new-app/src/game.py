from __future__ import annotations

import sys
from dataclasses import dataclass

import pygame

from .direction import Direction
from .food import Food
from .highscore import HighScoreManager
from .position import Position
from .settings import GameSettings
from .snake import Snake
from .ui import draw_panel, draw_text_centered


@dataclass
class GameState:
    """Mutable runtime state for the game."""

    score: int = 0
    game_over: bool = False


class SnakeGame:
    """Main game controller for input, update, and rendering."""

    def __init__(self, settings: GameSettings | None = None) -> None:
        self.settings = settings or GameSettings()
        self.state = GameState()
        self.highscore_manager = HighScoreManager(self.settings.highscore_file)
        self.high_score = self.highscore_manager.load()

        self.snake = Snake.create_initial(
            start=Position(self.settings.cols // 2, self.settings.rows // 2),
            length=3,
        )
        self.food = Food.spawn(self.settings.cols, self.settings.rows, self.snake)

        self.screen: pygame.Surface | None = None
        self.clock = pygame.time.Clock()
        self.font_small: pygame.font.Font | None = None
        self.font_medium: pygame.font.Font | None = None
        self.font_large: pygame.font.Font | None = None

    def run(self) -> None:
        """Initialize pygame and start the main loop."""
        pygame.init()
        pygame.display.set_caption(self.settings.title)
        self.screen = pygame.display.set_mode(
            (self.settings.window_width, self.settings.window_height)
        )

        self.font_small = pygame.font.SysFont("arial", 20)
        self.font_medium = pygame.font.SysFont("arial", 28, bold=True)
        self.font_large = pygame.font.SysFont("arial", 48, bold=True)

        while True:
            self.handle_events()
            if not self.state.game_over:
                self.update()
            self.render()
            self.clock.tick(self.settings.fps)

    def handle_events(self) -> None:
        """Process user input and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE,):
                    self.quit()

                if self.state.game_over:
                    if event.key == pygame.K_r:
                        self.restart()
                    continue

                if event.key in (pygame.K_UP, pygame.K_w):
                    self.snake.set_direction(Direction.UP)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.snake.set_direction(Direction.DOWN)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.snake.set_direction(Direction.LEFT)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.snake.set_direction(Direction.RIGHT)

    def update(self) -> None:
        """Advance game state by one tick."""
        self.snake.move()

        if self.is_out_of_bounds(self.snake.head) or self.snake.collides_with_self():
            self.end_game()
            return

        if self.snake.head == self.food.position:
            self.state.score += 1
            self.snake.grow(1)
            self.food.respawn(self.settings.cols, self.settings.rows, self.snake)

    def render(self) -> None:
        """Draw the full game frame."""
        assert self.screen is not None
        assert self.font_small is not None
        assert self.font_medium is not None
        assert self.font_large is not None

        self.screen.fill(self.settings.background_color)
        self.draw_grid()
        self.draw_food()
        self.draw_snake()
        self.draw_hud()

        if self.state.game_over:
            self.draw_game_over_overlay()

        pygame.display.flip()

    def draw_grid(self) -> None:
        """Render the subtle background grid."""
        assert self.screen is not None
        gs = self.settings.grid_size
        for x in range(0, self.settings.window_width, gs):
            pygame.draw.line(
                self.screen, self.settings.grid_color, (x, 0), (x, self.settings.window_height)
            )
        for y in range(0, self.settings.window_height, gs):
            pygame.draw.line(
                self.screen, self.settings.grid_color, (0, y), (self.settings.window_width, y)
            )

    def draw_snake(self) -> None:
        """Render the snake body with a distinct head."""
        assert self.screen is not None
        gs = self.settings.grid_size
        for index, segment in enumerate(self.snake.body):
            color = self.settings.snake_head_color if index == 0 else self.settings.snake_body_color
            rect = pygame.Rect(segment.x * gs, segment.y * gs, gs, gs)
            pygame.draw.rect(self.screen, color, rect.inflate(-2, -2), border_radius=6)

    def draw_food(self) -> None:
        """Render the food as a rounded square."""
        assert self.screen is not None
        gs = self.settings.grid_size
        rect = pygame.Rect(
            self.food.position.x * gs,
            self.food.position.y * gs,
            gs,
            gs,
        )
        pygame.draw.rect(self.screen, self.settings.food_color, rect.inflate(-4, -4), border_radius=6)

    def draw_hud(self) -> None:
        """Render score and high score panels."""
        assert self.screen is not None
        assert self.font_small is not None

        score_rect = pygame.Rect(12, 12, 160, 52)
        high_rect = pygame.Rect(self.settings.window_width - 172, 12, 160, 52)

        draw_panel(
            self.screen,
            score_rect,
            self.settings.panel_color,
            self.settings.panel_border_color,
        )
        draw_panel(
            self.screen,
            high_rect,
            self.settings.panel_color,
            self.settings.panel_border_color,
        )

        draw_text_centered(
            self.screen,
            f"Score: {self.state.score}",
            self.font_small,
            self.settings.text_color,
            score_rect.center,
        )
        draw_text_centered(
            self.screen,
            f"Best: {self.high_score}",
            self.font_small,
            self.settings.text_color,
            high_rect.center,
        )

    def draw_game_over_overlay(self) -> None:
        """Render the game over overlay and restart prompt."""
        assert self.screen is not None
        assert self.font_large is not None
        assert self.font_medium is not None
        assert self.font_small is not None

        overlay = pygame.Surface((self.settings.window_width, self.settings.window_height), pygame.SRCALPHA)
        overlay.fill(self.settings.game_over_overlay)
        self.screen.blit(overlay, (0, 0))

        draw_text_centered(
            self.screen,
            "Game Over",
            self.font_large,
            self.settings.text_color,
            (self.settings.window_width // 2, self.settings.window_height // 2 - 40),
        )
        draw_text_centered(
            self.screen,
            f"Final Score: {self.state.score}",
            self.font_medium,
            self.settings.text_color,
            (self.settings.window_width // 2, self.settings.window_height // 2 + 10),
        )
        draw_text_centered(
            self.screen,
            "Press R to restart or ESC to quit",
            self.font_small,
            self.settings.text_color,
            (self.settings.window_width // 2, self.settings.window_height // 2 + 50),
        )

    def is_out_of_bounds(self, position: Position) -> bool:
        """Check whether a position is outside the playfield."""
        return not (0 <= position.x < self.settings.cols and 0 <= position.y < self.settings.rows)

    def end_game(self) -> None:
        """Transition into the game over state and persist high score."""
        self.state.game_over = True
        if self.state.score > self.high_score:
            self.high_score = self.state.score
            self.highscore_manager.save(self.high_score)

    def restart(self) -> None:
        """Reset the game to its initial state."""
        self.state = GameState()
        self.snake = Snake.create_initial(
            start=Position(self.settings.cols // 2, self.settings.rows // 2),
            length=3,
        )
        self.food = Food.spawn(self.settings.cols, self.settings.rows, self.snake)

    def quit(self) -> None:
        """Exit the application cleanly."""
        pygame.quit()
        sys.exit(0)