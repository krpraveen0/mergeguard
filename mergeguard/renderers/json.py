"""JSON renderer for MergeGuard reports."""

from __future__ import annotations

import json

from mergeguard.models import MergeGuardReport


def render_json(report: MergeGuardReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
