"""Rule engine for deterministic MergeGuard scans."""

from __future__ import annotations

from typing import Optional

from mergeguard.config import MergeGuardConfig
from mergeguard.models import DiffStats, Finding, MergeGuardReport, ScanContext
from mergeguard.parser import parse_unified_diff
from mergeguard.rules import (
    EvidenceRule,
    ExplainabilityRule,
    GuardrailsRule,
    MeaningRule,
    RiskRule,
)
from mergeguard.rules.base import Rule


class MergeGuardEngine:
    def __init__(
        self,
        config: Optional[MergeGuardConfig] = None,
        rules: Optional[list[Rule]] = None,
    ) -> None:
        self.config = config or MergeGuardConfig()
        self.rules = rules or [
            MeaningRule(),
            EvidenceRule(),
            RiskRule(),
            GuardrailsRule(),
            ExplainabilityRule(),
        ]

    def scan(self, diff_text: str, description: str) -> MergeGuardReport:
        changed_files = parse_unified_diff(diff_text)
        stats = DiffStats.from_files(changed_files)
        context = ScanContext(
            description=description,
            changed_files=changed_files,
            stats=stats,
            config=self.config,
        )

        findings: list[Finding] = []
        for rule in self.rules:
            findings.extend(rule.run(context))

        return MergeGuardReport(findings=findings, stats=stats)
