from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

try:
    import devseeker_native  # type: ignore
except ImportError:
    devseeker_native = None


def native_available() -> bool:
    return devseeker_native is not None


def scan_repo_files(root: Path, ignore_hidden: bool = True) -> List[str] | None:
    if devseeker_native is None:
        return None
    return list(devseeker_native.scan_repo_files(str(root), ignore_hidden))


def chunk_text(text: str, max_chars: int, overlap: int = 0) -> List[str]:
    if devseeker_native is not None:
        return list(devseeker_native.chunk_text(text, max_chars, overlap))

    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars")

    chunks: List[str] = []
    step = max_chars - overlap
    start = 0
    while start < len(text):
        chunks.append(text[start : start + max_chars])
        start += step
    return chunks


def compact_lines(lines: Iterable[str], max_chars: int = 2000) -> str:
    content = "\n".join(lines)
    chunks = chunk_text(content, max_chars=max_chars, overlap=120)
    return chunks[0] if chunks else ""
