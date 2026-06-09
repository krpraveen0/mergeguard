from pathlib import Path

from mergeguard.engine import MergeGuardEngine


ROOT = Path(__file__).resolve().parents[1]


def test_sample_risky_diff_produces_expected_findings():
    diff_text = (ROOT / "examples" / "sample-risky.diff").read_text(encoding="utf-8")
    description = (ROOT / "examples" / "pr-description-weak.md").read_text(
        encoding="utf-8"
    )

    report = MergeGuardEngine().scan(diff_text, description)

    findings = {(finding.category, finding.severity, finding.message) for finding in report.findings}
    assert report.overall_status == "Needs attention"
    assert (
        "Meaning",
        "WARNING",
        "PR description does not clearly explain expected behavior.",
    ) in findings
    assert (
        "Evidence",
        "WARNING",
        "Source files changed but no test files were modified.",
    ) in findings
    assert (
        "Risk",
        "HIGH",
        "Risk-sensitive terms found: payment, refund.",
    ) in findings
    assert (
        "Guardrails",
        "WARNING",
        "Dependency file changed: package.json.",
    ) in findings
    assert (
        "Explainability",
        "WARNING",
        "No rollback note or author verification detail found.",
    ) in findings


def test_source_changes_with_tests_satisfy_evidence_rule():
    diff_text = """diff --git a/src/app.py b/src/app.py
index 1111111..2222222 100644
--- a/src/app.py
+++ b/src/app.py
@@ -1 +1 @@
-print("old")
+print("new")
diff --git a/tests/test_app.py b/tests/test_app.py
new file mode 100644
index 0000000..3333333
--- /dev/null
+++ b/tests/test_app.py
@@ -0,0 +1,2 @@
+def test_app():
+    assert True
"""
    description = """
    Requirement: update the app output.
    Expected behavior: app prints the new value.
    Tests run: python -m pytest.
    Rollback: revert this commit.
    """

    report = MergeGuardEngine().scan(diff_text, description)

    assert not report.findings_for("Evidence")
    assert not report.findings_for("Meaning")
    assert not report.findings_for("Explainability")
