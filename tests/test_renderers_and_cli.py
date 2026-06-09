import json
from pathlib import Path

from mergeguard.cli import main
from mergeguard.engine import MergeGuardEngine
from mergeguard.renderers.json import render_json
from mergeguard.renderers.markdown import render_markdown
from mergeguard.renderers.text import render_text


ROOT = Path(__file__).resolve().parents[1]


def test_markdown_renderer_matches_report_shape():
    diff_text = """diff --git a/src/payments/refund.py b/src/payments/refund.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/src/payments/refund.py
@@ -0,0 +1,2 @@
+def refund(payment_id):
+    return payment_id
"""
    report = MergeGuardEngine().scan(diff_text, "Small update.")

    markdown = render_markdown(report)

    assert markdown.startswith("## MERGE Review Readiness Report")
    assert "### Overall status: Needs attention" in markdown
    assert "| Metric | Value |" in markdown
    assert "| Files changed | 1 |" in markdown
    assert "| Category | Status | Findings |" in markdown
    assert "| Risk | Needs attention | 1 |" in markdown
    assert "### Meaning" in markdown
    assert "- **HIGH**: Risk-sensitive terms found: payment, refund." in markdown


def test_markdown_renderer_includes_file_paths_for_pr_comments():
    report = MergeGuardEngine().scan(
        """diff --git a/package.json b/package.json
index 1111111..2222222 100644
--- a/package.json
+++ b/package.json
@@ -1 +1 @@
-{}
+{"dependencies": {}}
""",
        "Small update.",
    )

    markdown = render_markdown(report)

    assert "- **WARNING**: Dependency file changed: package.json. (`package.json`)" in markdown


def test_sample_report_matches_risky_example_markdown():
    diff_text = (ROOT / "examples" / "sample-risky.diff").read_text(encoding="utf-8")
    description = (ROOT / "examples" / "pr-description-weak.md").read_text(
        encoding="utf-8"
    )
    expected_report = (ROOT / "examples" / "sample-report.md").read_text(
        encoding="utf-8"
    )

    report = MergeGuardEngine().scan(diff_text, description)

    assert render_markdown(report) == expected_report


def test_text_renderer_outputs_plain_text_report():
    report = MergeGuardEngine().scan("", "")

    text = render_text(report)

    assert text.startswith("MERGE Review Readiness Report")
    assert "Overall status: Needs attention" in text
    assert "Stats: 0 files changed, 0 additions, 0 deletions" in text
    assert "- WARNING: PR description does not clearly explain expected behavior." in text


def test_json_renderer_outputs_machine_readable_report():
    report = MergeGuardEngine().scan("", "")

    payload = json.loads(render_json(report))

    assert payload["overall_status"] == "Needs attention"
    assert payload["stats"] == {"additions": 0, "deletions": 0, "files_changed": 0}
    assert payload["findings"][0]["category"] == "Meaning"


def test_cli_scan_outputs_markdown(capsys):
    exit_code = main(
        [
            "scan",
            "--diff",
            "examples/sample-risky.diff",
            "--description",
            "examples/pr-description-weak.md",
            "--format",
            "markdown",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "## MERGE Review Readiness Report" in captured.out
    assert "- **WARNING**: Dependency file changed: package.json." in captured.out


def test_cli_scan_uses_explicit_config(tmp_path, capsys):
    diff_path = tmp_path / "sample.diff"
    description_path = tmp_path / "description.md"
    config_path = tmp_path / ".mergeguard.yml"
    diff_path.write_text(
        """diff --git a/src/payments/settlement.py b/src/payments/settlement.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/src/payments/settlement.py
@@ -0,0 +1,2 @@
+def settle():
+    return "wire-transfer"
""",
        encoding="utf-8",
    )
    description_path.write_text("Small update.", encoding="utf-8")
    config_path.write_text(
        """
risk_paths:
  - src/payments/**
risk_keywords:
  - wire-transfer
""".strip(),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "scan",
            "--diff",
            str(diff_path),
            "--description",
            str(description_path),
            "--format",
            "markdown",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "- **HIGH**: Risk-sensitive terms found: wire-transfer." in captured.out
    assert (
        "- **HIGH**: Risk-sensitive paths changed: src/payments/settlement.py."
        in captured.out
    )
