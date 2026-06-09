from pathlib import Path

import pytest

from mergeguard.config import ConfigError, MergeGuardConfig, load_config


def test_load_config_falls_back_to_defaults_when_file_is_missing(tmp_path):
    config = load_config(cwd=tmp_path)

    assert config == MergeGuardConfig()


def test_load_config_overrides_supported_keys(tmp_path):
    config_path = tmp_path / ".mergeguard.yml"
    config_path.write_text(
        """
thresholds:
  max_changed_files: 3
  max_line_changes: 25
test_patterns:
  - specs/
dependency_patterns:
  - "*.lock"
risk_paths:
  - src/payments/**
risk_keywords:
  - wire-transfer
""".strip(),
        encoding="utf-8",
    )

    config = load_config(cwd=tmp_path)

    assert config.max_changed_files == 3
    assert config.max_line_changes == 25
    assert config.test_patterns == ("specs/",)
    assert config.dependency_patterns == ("*.lock",)
    assert config.risk_paths == ("src/payments/**",)
    assert config.risk_keywords == ("wire-transfer",)


def test_load_config_rejects_unknown_keys(tmp_path):
    config_path = tmp_path / ".mergeguard.yml"
    config_path.write_text("surprise: true\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="unsupported config keys"):
        load_config(config_path)


def test_load_config_rejects_invalid_thresholds(tmp_path):
    config_path = tmp_path / ".mergeguard.yml"
    config_path.write_text(
        """
thresholds:
  max_changed_files: -1
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="max_changed_files"):
        load_config(config_path)
