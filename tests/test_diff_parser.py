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
    assert changed_files[0].status == "modified"
    assert changed_files[0].additions == 2
    assert changed_files[0].deletions == 1


def test_parse_unified_diff_tracks_added_file():
    diff = """diff --git a/src/new_feature.py b/src/new_feature.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/src/new_feature.py
@@ -0,0 +1,2 @@
+def enabled():
+    return True
"""

    changed_files = parse_unified_diff(diff)

    assert len(changed_files) == 1
    assert changed_files[0].path == "src/new_feature.py"
    assert changed_files[0].old_path is None
    assert changed_files[0].status == "added"
    assert changed_files[0].added_lines == ["def enabled():", "    return True"]
    assert changed_files[0].removed_lines == []


def test_parse_unified_diff_tracks_deleted_file():
    diff = """diff --git a/src/old_feature.py b/src/old_feature.py
deleted file mode 100644
index 1111111..0000000
--- a/src/old_feature.py
+++ /dev/null
@@ -1,2 +0,0 @@
-def enabled():
-    return False
"""

    changed_files = parse_unified_diff(diff)

    assert len(changed_files) == 1
    assert changed_files[0].path == "src/old_feature.py"
    assert changed_files[0].old_path == "src/old_feature.py"
    assert changed_files[0].status == "deleted"
    assert changed_files[0].added_lines == []
    assert changed_files[0].removed_lines == ["def enabled():", "    return False"]


def test_parse_unified_diff_tracks_renamed_file_without_content_changes():
    diff = """diff --git a/src/old_name.py b/src/new_name.py
similarity index 100%
rename from src/old_name.py
rename to src/new_name.py
"""

    changed_files = parse_unified_diff(diff)

    assert len(changed_files) == 1
    assert changed_files[0].path == "src/new_name.py"
    assert changed_files[0].old_path == "src/old_name.py"
    assert changed_files[0].status == "renamed"
    assert changed_files[0].additions == 0
    assert changed_files[0].deletions == 0


def test_parse_unified_diff_tracks_renamed_file_with_content_changes():
    diff = """diff --git a/src/old_name.py b/src/new_name.py
similarity index 70%
rename from src/old_name.py
rename to src/new_name.py
index 1111111..2222222 100644
--- a/src/old_name.py
+++ b/src/new_name.py
@@ -1 +1,2 @@
-print("old")
+print("new")
+print("renamed")
"""

    changed_files = parse_unified_diff(diff)

    assert len(changed_files) == 1
    assert changed_files[0].path == "src/new_name.py"
    assert changed_files[0].old_path == "src/old_name.py"
    assert changed_files[0].status == "renamed"
    assert changed_files[0].added_lines == ['print("new")', 'print("renamed")']
    assert changed_files[0].removed_lines == ['print("old")']
