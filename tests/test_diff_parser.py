from mergeguard.parser import parse_unified_diff


def test_parse_unified_diff_tracks_files_and_line_counts():
    diff = """diff --git a/src/app.py b/src/app.py
index 1111111..2222222 100644
--- a/src/app.py
+++ b/src/app.py
@@ -1,2 +1,3 @@
 def handler():
-    return "old"
+    return "new"
+    return "done"
"""

    changed_files = parse_unified_diff(diff)

    assert len(changed_files) == 1
    assert changed_files[0].path == "src/app.py"
    assert changed_files[0].old_path == "src/app.py"
    assert changed_files[0].additions == 2
    assert changed_files[0].deletions == 1
