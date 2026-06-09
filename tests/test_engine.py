from pathlib import Path

from mergeguard.config import MergeGuardConfig
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


def test_sample_safe_diff_with_good_description_is_ready():
    diff_text = (ROOT / "examples" / "sample-safe.diff").read_text(encoding="utf-8")
    description = (ROOT / "examples" / "pr-description-good.md").read_text(
        encoding="utf-8"
    )

    report = MergeGuardEngine().scan(diff_text, description)

    assert report.overall_status == "Ready"
    assert report.findings == []


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


def test_configurable_test_patterns_satisfy_evidence_rule():
    diff_text = """diff --git a/src/app.py b/src/app.py
index 1111111..2222222 100644
--- a/src/app.py
+++ b/src/app.py
@@ -1 +1 @@
-print("old")
+print("new")
diff --git a/specs/app_spec.py b/specs/app_spec.py
new file mode 100644
index 0000000..3333333
--- /dev/null
+++ b/specs/app_spec.py
@@ -0,0 +1,2 @@
+def test_app():
+    assert True
"""
    config = MergeGuardConfig(test_patterns=("specs/",))

    report = MergeGuardEngine(config=config).scan(diff_text, "Small update.")

    assert not report.findings_for("Evidence")


def test_configurable_dependency_patterns_and_thresholds_flag_guardrails():
    diff_text = """diff --git a/service.lock b/service.lock
index 1111111..2222222 100644
--- a/service.lock
+++ b/service.lock
@@ -1 +1 @@
-old
+new
diff --git a/src/app.py b/src/app.py
index 3333333..4444444 100644
--- a/src/app.py
+++ b/src/app.py
@@ -1 +1 @@
-print("old")
+print("new")
"""
    config = MergeGuardConfig(
        dependency_patterns=("*.lock",),
        max_changed_files=1,
        max_line_changes=1,
    )

    report = MergeGuardEngine(config=config).scan(diff_text, "Small update.")
    messages = [finding.message for finding in report.findings_for("Guardrails")]

    assert "Dependency file changed: service.lock." in messages
    assert "Large PR touches 2 files." in messages
    assert "Large PR changes 4 lines." in messages


def test_configurable_risk_paths_and_keywords_flag_risk():
    diff_text = """diff --git a/src/payments/settlement.py b/src/payments/settlement.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/src/payments/settlement.py
@@ -0,0 +1,2 @@
+def settle():
+    return "wire-transfer"
"""
    config = MergeGuardConfig(
        risk_paths=("src/payments/**",),
        risk_keywords=("wire-transfer",),
    )

    report = MergeGuardEngine(config=config).scan(diff_text, "Small update.")
    messages = [finding.message for finding in report.findings_for("Risk")]

    assert "Risk-sensitive terms found: wire-transfer." in messages
    assert "Risk-sensitive paths changed: src/payments/settlement.py." in messages
