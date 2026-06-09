"""Shared rule helpers."""

from __future__ import annotations

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
    normalized = path.replace("\\", "/").lower()
    return any(pattern.lower() in normalized for pattern in config.test_patterns)


def is_dependency_file(path: str, config: MergeGuardConfig) -> bool:
    filename = PurePosixPath(path.replace("\\", "/")).name.lower()
    return filename in {dependency_file.lower() for dependency_file in config.dependency_files}


def is_source_file(changed_file: ChangedFile, config: MergeGuardConfig) -> bool:
    path = changed_file.path.lower()
    if is_test_file(path, config) or is_dependency_file(path, config):
        return False
    return path.endswith(config.source_extensions)
