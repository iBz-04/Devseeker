from __future__ import annotations

import json
import sqlite3
import uuid

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SessionRecord:
    session_id: str
    project_path: str
    model_name: str
    mode: str
    created_at: str
    updated_at: str


class SessionStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def resolve_session(
        self,
        project_path: Path,
        model_name: str,
        mode: str,
        session_id: str = "",
        resume_last: bool = False,
    ) -> SessionRecord:
        if session_id:
            record = self.get_session(session_id)
            if record is None:
                raise KeyError(f"Unknown session id: {session_id}")
            return record

        if resume_last:
            record = self.latest_session(project_path)
            if record is not None:
                return record

        created_session_id = uuid.uuid4().hex[:12]
        now = _now()
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO sessions (
                    session_id, project_path, model_name, mode, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (created_session_id, str(project_path), model_name, mode, now, now),
            )
        return SessionRecord(
            session_id=created_session_id,
            project_path=str(project_path),
            model_name=model_name,
            mode=mode,
            created_at=now,
            updated_at=now,
        )

    def get_session(self, session_id: str) -> Optional[SessionRecord]:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT session_id, project_path, model_name, mode, created_at, updated_at
                FROM sessions
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return SessionRecord(*row)

    def latest_session(self, project_path: Path) -> Optional[SessionRecord]:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT session_id, project_path, model_name, mode, created_at, updated_at
                FROM sessions
                WHERE project_path = ?
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (str(project_path),),
            ).fetchone()
        if row is None:
            return None
        return SessionRecord(*row)

    def log_turn(self, session_id: str, role: str, content: str, kind: str = "message") -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO turns (session_id, role, kind, content, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, role, kind, content, _now()),
            )
            connection.execute(
                "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                (_now(), session_id),
            )

    def replace_plan(self, session_id: str, steps: Iterable[dict]) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM plan_steps WHERE session_id = ?", (session_id,))
            for index, step in enumerate(steps):
                connection.execute(
                    """
                    INSERT INTO plan_steps (session_id, step_index, title, status, metadata_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        index,
                        step.get("title", ""),
                        step.get("status", "pending"),
                        json.dumps(step, ensure_ascii=True),
                    ),
                )
            connection.execute(
                "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                (_now(), session_id),
            )

    def record_tool_event(
        self,
        session_id: str,
        tool_name: str,
        risk: str,
        allowed: bool,
        details: str,
    ) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO tool_events (
                    session_id, tool_name, risk, allowed, details, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session_id, tool_name, risk, int(allowed), details, _now()),
            )

    def update_state(
        self,
        session_id: str,
        *,
        selected_files: Optional[list[str]] = None,
        token_cost: Optional[float] = None,
        total_tokens: Optional[int] = None,
        last_failing_command: Optional[str] = None,
        repo_map_summary: Optional[str] = None,
    ) -> None:
        current = self.get_state(session_id)
        if selected_files is not None:
            current["selected_files"] = selected_files
        if token_cost is not None:
            current["token_cost"] = token_cost
        if total_tokens is not None:
            current["total_tokens"] = total_tokens
        if last_failing_command is not None:
            current["last_failing_command"] = last_failing_command
        if repo_map_summary is not None:
            current["repo_map_summary"] = repo_map_summary

        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO session_state (session_id, state_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    state_json = excluded.state_json,
                    updated_at = excluded.updated_at
                """,
                (session_id, json.dumps(current, ensure_ascii=True), _now()),
            )
            connection.execute(
                "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                (_now(), session_id),
            )

    def get_state(self, session_id: str) -> dict:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT state_json FROM session_state WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            return {}
        return json.loads(row[0])

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    project_path TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS plan_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    step_index INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tool_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    risk TEXT NOT NULL,
                    allowed INTEGER NOT NULL,
                    details TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS session_state (
                    session_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
