"""Shared rule helpers."""

from __future__ import annotations

import fnmatch
from pathlib import PurePosixPath
from typing import Optional

from mergeguard.config import MergeGuardConfig
from mergeguard.models import ChangedFile, Finding, ScanContext


class Rule:
    category: str

    def run(self, context: ScanContext) -> list[Finding]:
        raise NotImplementedError

    def finding(
        self,
        severity: str,
        message: str,
        file_path: Optional[str] = None,
    ) -> Finding:
        return Finding(
            category=self.category,
            severity=severity.upper(),
            message=message,
            file_path=file_path,
        )


def normalize_text(value: str) -> str:
    return " ".join(value.lower().split())


def is_test_file(path: str, config: MergeGuardConfig) -> bool:
    return path_matches_patterns(path, config.test_patterns)


def is_dependency_file(path: str, config: MergeGuardConfig) -> bool:
    return path_matches_patterns(path, config.dependency_patterns)


def is_source_file(changed_file: ChangedFile, config: MergeGuardConfig) -> bool:
    path = changed_file.path.lower()
    if is_test_file(path, config) or is_dependency_file(path, config):
        return False
    return path.endswith(config.source_extensions)


def path_matches_patterns(path: str, patterns: tuple[str, ...]) -> bool:
    normalized_path = path.replace("\\", "/").lower()
    filename = PurePosixPath(normalized_path).name

    for raw_pattern in patterns:
        pattern = raw_pattern.replace("\\", "/").lower().strip()
        if not pattern:
            continue
        if _has_glob(pattern) and (
            fnmatch.fnmatch(normalized_path, pattern)
            or fnmatch.fnmatch(f"/{normalized_path}", pattern)
        ):
            return True
        if pattern.endswith("/") and (
            normalized_path.startswith(pattern) or f"/{pattern}" in normalized_path
        ):
            return True
        if "/" not in pattern and filename == pattern:
            return True
        if pattern in normalized_path:
            return True

    return False


def _has_glob(pattern: str) -> bool:
    return any(character in pattern for character in "*?[]")
