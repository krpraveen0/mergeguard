"""Core data models for scans and reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional

from mergeguard.config import MergeGuardConfig


@dataclass(frozen=True)
class Finding:
    category: str
    severity: str
    message: str
    file_path: Optional[str] = None

    def to_dict(self) -> dict[str, str]:
        payload = asdict(self)
        return {key: value for key, value in payload.items() if value is not None}


@dataclass
class ChangedFile:
    path: str
    old_path: Optional[str] = None
    status: str = "modified"
    added_lines: list[str] = field(default_factory=list)
    removed_lines: list[str] = field(default_factory=list)

    @property
    def additions(self) -> int:
        return len(self.added_lines)

    @property
    def deletions(self) -> int:
        return len(self.removed_lines)


@dataclass(frozen=True)
class DiffStats:
    files_changed: int
    additions: int
    deletions: int

    @classmethod
    def from_files(cls, changed_files: list[ChangedFile]) -> "DiffStats":
        return cls(
            files_changed=len(changed_files),
            additions=sum(changed_file.additions for changed_file in changed_files),
            deletions=sum(changed_file.deletions for changed_file in changed_files),
        )

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(frozen=True)
class ScanContext:
    description: str
    changed_files: list[ChangedFile]
    stats: DiffStats
    config: MergeGuardConfig


@dataclass(frozen=True)
class MergeGuardReport:
    findings: list[Finding]
    stats: DiffStats

    @property
    def overall_status(self) -> str:
        return "Needs attention" if self.findings else "Ready"

    def findings_for(self, category: str) -> list[Finding]:
        return [finding for finding in self.findings if finding.category == category]

    def to_dict(self) -> dict[str, object]:
        return {
            "overall_status": self.overall_status,
            "stats": self.stats.to_dict(),
            "findings": [finding.to_dict() for finding in self.findings],
        }
