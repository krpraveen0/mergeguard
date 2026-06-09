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
            old_path, new_path = _parse_diff_header(line)
            current = ChangedFile(path=new_path or old_path or "", old_path=old_path)
            continue

        if current is None:
            continue

        if line.startswith("new file mode"):
            current.status = "added"
            current.old_path = None
            continue
        if line.startswith("deleted file mode"):
            current.status = "deleted"
            continue
        if line.startswith("rename from "):
            current.old_path = _strip_git_prefix(
                line.removeprefix("rename from ").strip()
            )
            current.status = "renamed"
            continue
        if line.startswith("rename to "):
            current.path = (
                _strip_git_prefix(line.removeprefix("rename to ").strip()) or ""
            )
            current.status = "renamed"
            continue
        if line.startswith("--- "):
            old_path = _parse_marker_path(line)
            if old_path == "/dev/null":
                current.old_path = None
                if current.status == "modified":
                    current.status = "added"
            else:
                current.old_path = old_path
            continue
        if line.startswith("+++ "):
            new_path = _parse_marker_path(line)
            if new_path == "/dev/null":
                current.status = "deleted"
                if current.old_path:
                    current.path = current.old_path
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


def _parse_diff_header(line: str) -> tuple[Optional[str], Optional[str]]:
    header = line.removeprefix("diff --git ").strip()
    if " b/" in header:
        old_path, new_path = header.split(" b/", maxsplit=1)
        return _strip_git_prefix(old_path), _strip_git_prefix(f"b/{new_path}")

    parts = header.split()
    old_path = _strip_git_prefix(parts[0]) if parts else None
    new_path = _strip_git_prefix(parts[1]) if len(parts) > 1 else old_path
    return old_path, new_path


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
