from pathlib import Path

from devseeker.runtime.sessions import SessionStore


def test_session_store_creates_and_updates_session(tmp_path: Path):
    store = SessionStore(tmp_path / "sessions.db")
    session = store.resolve_session(
        tmp_path,
        model_name="gpt-4.1",
        mode="auto",
    )

    store.log_turn(session.session_id, "user", "hello")
    store.replace_plan(
        session.session_id,
        [{"title": "Inspect repo", "status": "pending"}],
    )
    store.update_state(
        session.session_id,
        selected_files=["src/app.py"],
        total_tokens=123,
        token_cost=0.45,
        last_failing_command="sh run.sh",
    )

    resolved = store.get_session(session.session_id)
    state = store.get_state(session.session_id)

    assert resolved is not None
    assert resolved.session_id == session.session_id
    assert state["selected_files"] == ["src/app.py"]
    assert state["total_tokens"] == 123
    assert state["last_failing_command"] == "sh run.sh"


def test_session_store_resume_last(tmp_path: Path):
    store = SessionStore(tmp_path / "sessions.db")
    first = store.resolve_session(tmp_path, "gpt-4.1", "plan")
    second = store.resolve_session(tmp_path, "gpt-4.1", "edit")

    resumed = store.resolve_session(
        tmp_path,
        "gpt-4.1",
        "edit",
        resume_last=True,
    )

    assert resumed.session_id == second.session_id
    assert resumed.session_id != first.session_id
