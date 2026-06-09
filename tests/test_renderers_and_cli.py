import json

from mergeguard.cli import main
from mergeguard.engine import MergeGuardEngine
from mergeguard.renderers.json import render_json
from mergeguard.renderers.markdown import render_markdown


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
    assert "### Meaning" in markdown
    assert "- **HIGH**: Risk-sensitive terms found: payment, refund." in markdown


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
