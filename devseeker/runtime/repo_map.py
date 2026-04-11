from __future__ import annotations

import ast
import os
import re
import subprocess

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

from devseeker.core.git import filter_by_gitignore, is_git_repo
from devseeker.runtime.native import compact_lines, scan_repo_files

IGNORE_FOLDERS = {"site-packages", "node_modules", "venv", "__pycache__", ".git"}


@dataclass
class RepoFileSummary:
    path: str
    language: str
    line_count: int
    symbols: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    last_modified: float = 0.0


@dataclass
class RepoMap:
    root: Path
    files: List[RepoFileSummary]
    directory_tree: str
    hot_files: List[str]
    recent_edits: List[str]
    git_diff_context: str

    def to_summary(self, max_files: int = 20) -> str:
        file_lines = []
        for file_summary in self.files[:max_files]:
            symbols = ", ".join(file_summary.symbols[:6]) or "no symbols"
            imports = ", ".join(file_summary.imports[:4]) or "no imports"
            file_lines.append(
                f"- {file_summary.path} [{file_summary.language}] "
                f"lines={file_summary.line_count} symbols={symbols} imports={imports}"
            )

        hot_files = ", ".join(self.hot_files[:10]) or "none"
        recent_edits = ", ".join(self.recent_edits[:10]) or "none"
        diff_context = self.git_diff_context or "No git diff context."
        return "\n".join(
            [
                "Directory tree:",
                self.directory_tree or "(empty)",
                "",
                "Indexed files:",
                "\n".join(file_lines) or "(none)",
                "",
                f"Hot files: {hot_files}",
                f"Recent edits: {recent_edits}",
                f"Git diff context: {diff_context}",
            ]
        )

    def select_relevant_files(self, prompt_text: str, limit: int = 12) -> List[str]:
        prompt_terms = {term for term in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]+", prompt_text.lower()) if len(term) > 2}
        scored = []
        hot_bonus = {path: 8 for path in self.hot_files[:10]}
        recent_bonus = {path: 4 for path in self.recent_edits[:10]}
        for file_summary in self.files:
            haystack = " ".join(
                [
                    file_summary.path.lower(),
                    " ".join(file_summary.symbols).lower(),
                    " ".join(file_summary.imports).lower(),
                ]
            )
            score = sum(3 for term in prompt_terms if term in haystack)
            score += hot_bonus.get(file_summary.path, 0)
            score += recent_bonus.get(file_summary.path, 0)
            if file_summary.path in self.hot_files:
                score += 2
            if score > 0:
                scored.append((score, file_summary.path))

        scored.sort(key=lambda item: (-item[0], item[1]))
        selected = [path for _, path in scored[:limit]]

        if not selected:
            selected = self.hot_files[:limit] or [file.path for file in self.files[:limit]]
        return selected


class RepoMapBuilder:
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path).resolve()

    def build(self, max_indexed_files: int = 200) -> RepoMap:
        file_paths = self._scan_files()[:max_indexed_files]
        summaries = [self._summarize_file(path) for path in file_paths]
        summaries = [summary for summary in summaries if summary is not None]
        hot_files = self._hot_files(file_paths)
        recent_edits = self._recent_edits(file_paths)
        return RepoMap(
            root=self.project_path,
            files=summaries,
            directory_tree=self._directory_tree(file_paths),
            hot_files=hot_files,
            recent_edits=recent_edits,
            git_diff_context=self._git_diff_context(),
        )

    def load_files(self, relative_paths: Iterable[str]) -> dict[str, str]:
        files: dict[str, str] = {}
        for relative_path in relative_paths:
            full_path = self.project_path / relative_path
            if not full_path.is_file():
                continue
            try:
                files[relative_path] = full_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
        return files

    def _scan_files(self) -> List[str]:
        native_paths = scan_repo_files(self.project_path)
        if native_paths is not None:
            return sorted(self._filter_paths(native_paths))

        file_paths: List[str] = []
        for path in self.project_path.glob("**/*"):
            if not path.is_file():
                continue
            relative_path = str(path.relative_to(self.project_path))
            if self._should_skip(relative_path):
                continue
            file_paths.append(relative_path)

        if is_git_repo(self.project_path):
            file_paths = filter_by_gitignore(self.project_path, file_paths)

        return sorted(file_paths)

    def _filter_paths(self, file_paths: Iterable[str]) -> List[str]:
        filtered = [path for path in file_paths if not self._should_skip(path)]
        if is_git_repo(self.project_path):
            filtered = filter_by_gitignore(self.project_path, filtered)
        return filtered

    def _should_skip(self, relative_path: str) -> bool:
        path = Path(relative_path)
        parts = path.parts
        if any(part in IGNORE_FOLDERS for part in parts):
            return True
        if any(part.startswith(".") for part in parts):
            return True
        return False

    def _summarize_file(self, relative_path: str) -> RepoFileSummary | None:
        full_path = self.project_path / relative_path
        try:
            content = full_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return None

        language = self._detect_language(full_path)
        symbols = self._extract_symbols(language, content)
        imports = self._extract_imports(language, content)
        return RepoFileSummary(
            path=relative_path,
            language=language,
            line_count=content.count("\n") + 1,
            symbols=symbols[:20],
            imports=imports[:20],
            last_modified=full_path.stat().st_mtime,
        )

    def _detect_language(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".py":
            return "python"
        if suffix in {".ts", ".tsx", ".js", ".jsx"}:
            return "typescript"
        if suffix == ".rs":
            return "rust"
        if suffix in {".toml", ".yaml", ".yml", ".json"}:
            return "config"
        if suffix in {".md", ".rst"}:
            return "docs"
        return suffix.lstrip(".") or "text"

    def _extract_symbols(self, language: str, content: str) -> List[str]:
        if language == "python":
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return []
            return [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            ]

        patterns = {
            "typescript": r"(?:export\s+)?(?:async\s+)?(?:function|class|interface|type|const)\s+([A-Za-z_][A-Za-z0-9_]*)",
            "rust": r"(?:pub\s+)?(?:fn|struct|enum|trait|mod)\s+([A-Za-z_][A-Za-z0-9_]*)",
        }
        pattern = patterns.get(language)
        if not pattern:
            return []
        return re.findall(pattern, content)

    def _extract_imports(self, language: str, content: str) -> List[str]:
        if language == "python":
            imports = re.findall(r"^\s*import\s+([A-Za-z0-9_., ]+)", content, re.MULTILINE)
            from_imports = re.findall(r"^\s*from\s+([A-Za-z0-9_\.]+)\s+import\s+", content, re.MULTILINE)
            flattened = []
            for item in imports:
                flattened.extend([part.strip() for part in item.split(",") if part.strip()])
            flattened.extend(from_imports)
            return flattened

        if language in {"typescript", "rust"}:
            return re.findall(r"""["']([^"']+)["']""", "\n".join(content.splitlines()[:80]))

        return []

    def _directory_tree(self, file_paths: Iterable[str]) -> str:
        lines = []
        seen_directories = set()
        for relative_path in sorted(file_paths):
            path = Path(relative_path)
            for depth, part in enumerate(path.parts[:-1]):
                prefix = "  " * depth
                directory_key = tuple(path.parts[: depth + 1])
                if directory_key in seen_directories:
                    continue
                lines.append(f"{prefix}{part}/")
                seen_directories.add(directory_key)
            lines.append(f"{'  ' * (len(path.parts) - 1)}{path.name}")
        return compact_lines(lines, max_chars=3000)

    def _git_diff_context(self) -> str:
        if not is_git_repo(self.project_path):
            return ""
        try:
            status = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=False,
            ).stdout.strip()
            diff_stat = subprocess.run(
                ["git", "diff", "--stat"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=False,
            ).stdout.strip()
        except OSError:
            return ""
        return " | ".join(part for part in [status, diff_stat] if part)

    def _hot_files(self, file_paths: Iterable[str]) -> List[str]:
        git_changed = self._git_changed_files()
        if git_changed:
            return git_changed[:15]
        return self._recent_edits(file_paths)

    def _recent_edits(self, file_paths: Iterable[str]) -> List[str]:
        decorated = []
        for relative_path in file_paths:
            full_path = self.project_path / relative_path
            try:
                decorated.append((full_path.stat().st_mtime, relative_path))
            except OSError:
                continue
        decorated.sort(reverse=True)
        return [path for _, path in decorated[:15]]

    def _git_changed_files(self) -> List[str]:
        if not is_git_repo(self.project_path):
            return []
        try:
            output = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=False,
            ).stdout
        except OSError:
            return []
        files = []
        for line in output.splitlines():
            if len(line) < 4:
                continue
            files.append(line[3:].strip())
        return files
