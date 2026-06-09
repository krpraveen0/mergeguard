"""Meaning checks for PR description quality."""

from __future__ import annotations

from mergeguard.models import Finding, ScanContext
from mergeguard.rules.base import Rule, normalize_text


class MeaningRule(Rule):
    category = "Meaning"

    def run(self, context: ScanContext) -> list[Finding]:
        description = normalize_text(context.description)
        matching_signals = [
            signal for signal in context.config.meaning_signals if signal in description
        ]
        has_expected_behavior = "expected behavior" in description

        if not description or len(matching_signals) < 2 or not has_expected_behavior:
            return [
                self.finding(
                    "WARNING",
                    "PR description does not clearly explain expected behavior.",
                )
            ]

        return []
