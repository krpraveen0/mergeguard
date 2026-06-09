"""Small unified diff parser for changed files and line counts."""

from __future__ import annotations

from typing import Optional

from mergeguard.models import ChangedFile


def parse_unified_diff(diff_text: str) -> list[ChangedFile]:
    changed_files: list[ChangedFile] = []
    current: Optional[ChangedFile] = None

    def flush_current() -> None:
        if current is not None:
            changed_files.append(current)

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            flush_current()
            parts = line.split()
            old_path = _strip_git_prefix(parts[2]) if len(parts) > 2 else None
            new_path = _strip_git_prefix(parts[3]) if len(parts) > 3 else old_path
            current = ChangedFile(path=new_path or old_path or "", old_path=old_path)
            continue

        if current is None:
            continue

        if line.startswith("new file mode"):
            current.status = "added"
            continue
        if line.startswith("deleted file mode"):
            current.status = "deleted"
            continue
        if line.startswith("rename from "):
            current.old_path = line.removeprefix("rename from ").strip()
            current.status = "renamed"
            continue
        if line.startswith("rename to "):
            current.path = line.removeprefix("rename to ").strip()
            current.status = "renamed"
            continue
        if line.startswith("--- "):
            old_path = _parse_marker_path(line)
            if old_path != "/dev/null":
                current.old_path = old_path
            continue
        if line.startswith("+++ "):
            new_path = _parse_marker_path(line)
            if new_path == "/dev/null":
                current.status = "deleted"
            else:
                current.path = new_path
            continue
        if line.startswith("+"):
            current.added_lines.append(line[1:])
            continue
        if line.startswith("-"):
            current.removed_lines.append(line[1:])

    flush_current()
    return changed_files


def _strip_git_prefix(path: Optional[str]) -> Optional[str]:
    if path is None:
        return None
    if path.startswith("a/") or path.startswith("b/"):
        return path[2:]
    return path


def _parse_marker_path(line: str) -> str:
    marker_path = line.split(maxsplit=1)[1]
    path = marker_path.split("\t", maxsplit=1)[0]
    return _strip_git_prefix(path) or path
