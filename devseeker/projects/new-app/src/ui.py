from __future__ import annotations

import pygame


def draw_text_centered(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    center: tuple[int, int],
) -> None:
    """Render text centered at the given position."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=center)
    surface.blit(rendered, rect)


def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fill_color: tuple[int, int, int],
    border_color: tuple[int, int, int],
    border_radius: int = 10,
    border_width: int = 2,
) -> None:
    """Draw a rounded panel with a border."""
    pygame.draw.rect(surface, fill_color, rect, border_radius=border_radius)
    pygame.draw.rect(
        surface,
        border_color,
        rect,
        width=border_width,
        border_radius=border_radius,
    )