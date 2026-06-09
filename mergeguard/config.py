"""Default deterministic configuration for MergeGuard."""

from __future__ import annotations

from dataclasses import dataclass


CATEGORY_ORDER = (
    "Meaning",
    "Evidence",
    "Risk",
    "Guardrails",
    "Explainability",
)


@dataclass(frozen=True)
class MergeGuardConfig:
    meaning_signals: tuple[str, ...] = (
        "requirement",
        "expected behavior",
        "issue",
        "user impact",
        "acceptance criteria",
        "why",
    )
    test_patterns: tuple[str, ...] = (
        "tests/",
        "test_",
        "_test",
        ".test.",
        ".spec.",
        "__tests__",
    )
    risky_terms: tuple[str, ...] = (
        "auth",
        "login",
        "token",
        "password",
        "permission",
        "role",
        "payment",
        "billing",
        "invoice",
        "refund",
        "migration",
        "delete",
        "drop",
        "encrypt",
        "secret",
        "credential",
        "infra",
        "terraform",
        "config",
    )
    dependency_files: tuple[str, ...] = (
        "requirements.txt",
        "pyproject.toml",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "poetry.lock",
        "go.mod",
        "Cargo.toml",
        "pom.xml",
        "build.gradle",
    )
    source_extensions: tuple[str, ...] = (
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".go",
        ".rs",
        ".java",
        ".kt",
        ".rb",
        ".php",
        ".cs",
        ".c",
        ".cc",
        ".cpp",
        ".h",
        ".hpp",
        ".swift",
    )
    explainability_signals: tuple[str, ...] = (
        "tests run",
        "rollback",
        "known risk",
        "ai generated",
        "generated with",
        "manual review",
        "verified",
    )
    verification_signals: tuple[str, ...] = (
        "tests run",
        "manual review",
        "verified",
    )
    max_changed_files: int = 20
    max_line_changes: int = 500
