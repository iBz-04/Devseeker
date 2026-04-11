from pathlib import Path

from devseeker.runtime.native import chunk_text
from devseeker.runtime.repo_map import RepoMapBuilder


def test_repo_map_extracts_symbols_and_relevant_files(tmp_path: Path):
    app_py = tmp_path / "src" / "app.py"
    app_py.parent.mkdir(parents=True)
    app_py.write_text(
        "import os\n\nclass Planner:\n    pass\n\ndef build_plan():\n    return 'ok'\n",
        encoding="utf-8",
    )
    utils_ts = tmp_path / "src" / "utils.ts"
    utils_ts.write_text(
        "export function compactContext() { return true; }\n",
        encoding="utf-8",
    )

    repo_map = RepoMapBuilder(tmp_path).build()
    paths = [item.path for item in repo_map.files]
    selected = repo_map.select_relevant_files("build planner context compact", limit=5)

    assert "src/app.py" in paths
    assert "src/utils.ts" in paths
    assert "src/app.py" in selected
    assert repo_map.files[0].symbols


def test_chunk_text_python_fallback():
    chunks = chunk_text("abcdefghij", max_chars=4, overlap=1)
    assert chunks == ["abcd", "defg", "ghij", "j"]
