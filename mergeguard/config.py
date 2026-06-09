"""Default deterministic configuration for MergeGuard."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Optional


CATEGORY_ORDER = (
    "Meaning",
    "Evidence",
    "Risk",
    "Guardrails",
    "Explainability",
)

CONFIG_FILE_NAMES = (".mergeguard.yml", ".mergeguard.yaml")


class ConfigError(ValueError):
    """Raised when a MergeGuard config file cannot be parsed or validated."""


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
    risk_keywords: tuple[str, ...] = (
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
    risk_paths: tuple[str, ...] = ()
    dependency_patterns: tuple[str, ...] = (
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

    @property
    def risky_terms(self) -> tuple[str, ...]:
        return self.risk_keywords

    @property
    def dependency_files(self) -> tuple[str, ...]:
        return self.dependency_patterns


def load_config(
    path: Optional[str | Path] = None,
    cwd: Optional[str | Path] = None,
) -> MergeGuardConfig:
    """Load MergeGuard config from a YAML file, falling back to defaults."""

    config_path = _resolve_config_path(path, cwd)
    if config_path is None:
        return MergeGuardConfig()

    mapping = _parse_yaml_subset(config_path.read_text(encoding="utf-8"), config_path)
    return _config_from_mapping(mapping)


def _resolve_config_path(
    path: Optional[str | Path],
    cwd: Optional[str | Path],
) -> Optional[Path]:
    if path is not None:
        return Path(path)

    search_root = Path(cwd) if cwd is not None else Path.cwd()
    for config_name in CONFIG_FILE_NAMES:
        candidate = search_root / config_name
        if candidate.exists():
            return candidate

    return None


def _config_from_mapping(mapping: dict[str, Any]) -> MergeGuardConfig:
    allowed_keys = {
        "thresholds",
        "max_changed_files",
        "max_line_changes",
        "test_patterns",
        "dependency_patterns",
        "dependency_files",
        "risk_paths",
        "risk_keywords",
        "risk_terms",
        "risky_terms",
    }
    unknown_keys = sorted(set(mapping) - allowed_keys)
    if unknown_keys:
        raise ConfigError(f"unsupported config keys: {', '.join(unknown_keys)}")

    defaults = MergeGuardConfig()
    thresholds = _thresholds_mapping(mapping.get("thresholds"))

    return replace(
        defaults,
        test_patterns=_list_value(mapping, "test_patterns", defaults.test_patterns),
        dependency_patterns=_list_value(
            mapping,
            "dependency_patterns",
            defaults.dependency_patterns,
            aliases=("dependency_files",),
        ),
        risk_paths=_list_value(mapping, "risk_paths", defaults.risk_paths),
        risk_keywords=_list_value(
            mapping,
            "risk_keywords",
            defaults.risk_keywords,
            aliases=("risk_terms", "risky_terms"),
        ),
        max_changed_files=_threshold_value(
            mapping,
            thresholds,
            "max_changed_files",
            defaults.max_changed_files,
        ),
        max_line_changes=_threshold_value(
            mapping,
            thresholds,
            "max_line_changes",
            defaults.max_line_changes,
        ),
    )


def _thresholds_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError("thresholds must be a mapping")
    unknown_keys = sorted(set(value) - {"max_changed_files", "max_line_changes"})
    if unknown_keys:
        raise ConfigError(f"unsupported threshold keys: {', '.join(unknown_keys)}")
    return value


def _threshold_value(
    mapping: dict[str, Any],
    thresholds: dict[str, Any],
    key: str,
    default: int,
) -> int:
    if key in mapping and key in thresholds:
        raise ConfigError(f"{key} cannot be set both top-level and under thresholds")

    value = thresholds.get(key, mapping.get(key, default))
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ConfigError(f"{key} must be a non-negative integer")
    return value


def _list_value(
    mapping: dict[str, Any],
    key: str,
    default: tuple[str, ...],
    aliases: tuple[str, ...] = (),
) -> tuple[str, ...]:
    candidate_keys = (key, *aliases)
    present_keys = [
        candidate_key for candidate_key in candidate_keys if candidate_key in mapping
    ]
    if not present_keys:
        return default
    if len(present_keys) > 1:
        raise ConfigError(f"use only one of: {', '.join(candidate_keys)}")

    value = mapping[present_keys[0]]
    if not isinstance(value, list):
        raise ConfigError(f"{present_keys[0]} must be a list")

    list_values: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ConfigError(f"{present_keys[0]} must contain only strings")
        if item.strip():
            list_values.append(item.strip())

    return tuple(list_values)


def _parse_yaml_subset(text: str, path: Path) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    current_key: Optional[str] = None

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw_line).rstrip()
        if not line.strip():
            continue
        if line.startswith("\t"):
            raise ConfigError(f"{path}:{line_number}: tabs are not supported")

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0:
            key, separator, value = stripped.partition(":")
            if not separator or not key.strip():
                raise ConfigError(f"{path}:{line_number}: expected 'key: value'")
            current_key = key.strip()
            mapping[current_key] = (
                None
                if not value.strip()
                else _parse_yaml_value(value.strip(), path, line_number)
            )
            if value.strip():
                current_key = None
            continue

        if indent != 2 or current_key is None:
            raise ConfigError(f"{path}:{line_number}: expected two-space indentation")

        if stripped.startswith("- "):
            if mapping[current_key] is None:
                mapping[current_key] = []
            if not isinstance(mapping[current_key], list):
                raise ConfigError(f"{path}:{line_number}: mixed list and mapping values")
            mapping[current_key].append(
                _parse_yaml_value(stripped[2:].strip(), path, line_number)
            )
            continue

        nested_key, separator, value = stripped.partition(":")
        if not separator or not nested_key.strip():
            raise ConfigError(f"{path}:{line_number}: expected nested 'key: value'")
        if mapping[current_key] is None:
            mapping[current_key] = {}
        if not isinstance(mapping[current_key], dict):
            raise ConfigError(f"{path}:{line_number}: mixed mapping and list values")
        mapping[current_key][nested_key.strip()] = _parse_yaml_value(
            value.strip(),
            path,
            line_number,
        )

    return mapping


def _strip_comment(line: str) -> str:
    quote: Optional[str] = None
    for index, character in enumerate(line):
        if character in {"'", '"'}:
            quote = None if quote == character else character if quote is None else quote
        if character == "#" and quote is None:
            return line[:index]
    return line


def _parse_yaml_value(value: str, path: Path, line_number: int) -> Any:
    if value.startswith("[") and value.endswith("]"):
        inner_value = value[1:-1].strip()
        if not inner_value:
            return []
        return [
            _parse_yaml_scalar(item.strip(), path, line_number)
            for item in inner_value.split(",")
        ]

    return _parse_yaml_scalar(value, path, line_number)


def _parse_yaml_scalar(value: str, path: Path, line_number: int) -> Any:
    if not value:
        return ""
    if value[0] in {"'", '"'} or value[-1:] in {"'", '"'}:
        if len(value) < 2 or value[0] != value[-1]:
            raise ConfigError(f"{path}:{line_number}: unterminated quoted value")
        return value[1:-1]

    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False

    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)

    return value
