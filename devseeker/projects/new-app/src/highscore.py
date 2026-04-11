from __future__ import annotations

from pathlib import Path


class HighScoreManager:
    """Persistent high score storage using a simple text file."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def load(self) -> int:
        """Load the stored high score, returning 0 if unavailable."""
        try:
            return int(self.path.read_text(encoding="utf-8").strip())
        except (FileNotFoundError, ValueError, OSError):
            return 0

    def save(self, score: int) -> None:
        """Persist the provided high score."""
        self.path.write_text(f"{score}\n", encoding="utf-8")