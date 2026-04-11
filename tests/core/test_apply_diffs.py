from devseeker.core.chat_to_files import apply_diffs, parse_diffs
from devseeker.core.files_dict import FilesDict


def test_apply_diffs_inserts_at_top_preserves_order():
    original = FilesDict({"file.txt": "b\nc"})
    diff_text = """
```diff
--- file.txt
+++ file.txt
@@ -1,2 +1,3 @@
+a
 b
 c
```
"""
    diffs = parse_diffs(diff_text)
    updated = apply_diffs(diffs, original)
    assert updated["file.txt"] == "a\nb\nc"


def test_apply_diffs_inserts_at_end_preserves_trailing_newline():
    original = FilesDict({"file.txt": "a\nb\n"})
    diff_text = """
```diff
--- file.txt
+++ file.txt
@@ -1,2 +1,3 @@
 a
 b
+c
```
"""
    diffs = parse_diffs(diff_text)
    updated = apply_diffs(diffs, original)
    assert updated["file.txt"] == "a\nb\nc\n"
