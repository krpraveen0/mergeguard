"""Explainability checks for author ownership signals."""

from __future__ import annotations

from mergeguard.models import Finding, ScanContext
from mergeguard.rules.base import Rule, normalize_text


class ExplainabilityRule(Rule):
    category = "Explainability"

    def run(self, context: ScanContext) -> list[Finding]:
        description = normalize_text(context.description)
        has_ownership_signal = any(
            signal in description for signal in context.config.explainability_signals
        )
        has_rollback_note = "rollback" in description
        has_verification_detail = any(
            signal in description for signal in context.config.verification_signals
        )

        if not has_ownership_signal or not has_rollback_note or not has_verification_detail:
            return [
                self.finding(
                    "WARNING",
                    "No rollback note or author verification detail found.",
                )
            ]

        return []
