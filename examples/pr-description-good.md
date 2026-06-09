Requirement: normalize display names before showing them in account headers.

Expected behavior: blank or whitespace-only names fall back to Anonymous, and non-empty names are stripped before display.

User impact: users see consistent labels instead of empty profile headings.

Acceptance criteria:
- Names with leading or trailing whitespace render without surrounding spaces.
- Blank names render as Anonymous.

Why: this keeps account surfaces readable when upstream profile data is incomplete.

Tests run: uv run --python 3.14.5 pytest

Rollback: revert this PR if display labels regress.

Verified: manually reviewed the diff and confirmed the behavior is covered by tests.
