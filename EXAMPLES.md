# MergeGuard Examples

This guide walks through runnable examples you can copy into your own terminal.

MergeGuard is published as the `mergeguard-cli` package. The installed command is `mergeguard`.

## 1. Install MergeGuard

MergeGuard requires Python 3.14 or newer.

macOS with Homebrew:

```bash
brew tap krpraveen0/mergeguard https://github.com/krpraveen0/mergeguard
brew trust krpraveen0/mergeguard
brew install krpraveen0/mergeguard/mergeguard-cli
```

Python with pip:

```bash
python3.14 -m pip install mergeguard-cli
```

Confirm the command is available:

```bash
mergeguard --help
```

Expected shape:

```text
usage: mergeguard [-h] {scan} ...
```

## 2. Clone The Example Repository

The package installs the CLI. To use the bundled example diffs and PR descriptions, clone the repository:

```bash
git clone https://github.com/krpraveen0/mergeguard.git
cd mergeguard
```

The example files are:

- `examples/sample-safe.diff`
- `examples/sample-risky.diff`
- `examples/pr-description-good.md`
- `examples/pr-description-weak.md`
- `examples/mergeguard-config.yml`

## 3. Run A Ready PR Example

This example changes source code, includes a matching test, and has a strong PR description.

```bash
mergeguard scan \
  --diff examples/sample-safe.diff \
  --description examples/pr-description-good.md \
  --format text
```

Expected output:

```text
MERGE Review Readiness Report
Overall status: Ready
Stats: 2 files changed, 11 additions, 0 deletions

Meaning
- OK: No issues found.

Evidence
- OK: No issues found.

Risk
- OK: No issues found.

Guardrails
- OK: No issues found.

Explainability
- OK: No issues found.
```

Use this case as the baseline for what MergeGuard considers review-ready:

- The description explains the requirement and expected behavior.
- Tests changed alongside source code.
- No configured risk keywords or paths are present.
- No dependency or large-change guardrail is triggered.
- The author included verification and rollback signals.

## 4. Run A Risky PR Example

This example touches payment/refund code, changes `package.json`, has no tests, and has a weak PR description.

```bash
mergeguard scan \
  --diff examples/sample-risky.diff \
  --description examples/pr-description-weak.md \
  --format text
```

Expected output:

```text
MERGE Review Readiness Report
Overall status: Needs attention
Stats: 2 files changed, 7 additions, 1 deletions

Meaning
- WARNING: PR description does not clearly explain expected behavior.

Evidence
- WARNING: Source files changed but no test files were modified.

Risk
- HIGH: Risk-sensitive terms found: payment, refund.

Guardrails
- WARNING: Dependency file changed: package.json. (package.json)

Explainability
- WARNING: No rollback note or author verification detail found.
```

This does not mean MergeGuard reviewed the code. It means the PR is not ready for responsible human review yet.

## 5. Generate GitHub-Friendly Markdown

Use markdown when you want output that can be pasted into a GitHub PR comment.

```bash
mergeguard scan \
  --diff examples/sample-risky.diff \
  --description examples/pr-description-weak.md \
  --format markdown
```

Expected shape:

```markdown
## MERGE Review Readiness Report

### Overall status: Needs attention

| Metric | Value |
| --- | ---: |
| Files changed | 2 |
| Additions | 7 |
| Deletions | 1 |

### Risk
- **HIGH**: Risk-sensitive terms found: payment, refund.
```

## 6. Generate JSON For Automation

Use JSON when another tool or CI job needs to parse the report.

```bash
mergeguard scan \
  --diff examples/sample-risky.diff \
  --description examples/pr-description-weak.md \
  --format json
```

Expected shape:

```json
{
  "findings": [
    {
      "category": "Meaning",
      "message": "PR description does not clearly explain expected behavior.",
      "severity": "WARNING"
    }
  ],
  "overall_status": "Needs attention",
  "stats": {
    "additions": 7,
    "deletions": 1,
    "files_changed": 2
  }
}
```

## 7. Use A Config File

MergeGuard reads `.mergeguard.yml` or `.mergeguard.yaml` from the current directory automatically. You can also pass a config file explicitly:

```bash
mergeguard scan \
  --diff examples/sample-risky.diff \
  --description examples/pr-description-weak.md \
  --format markdown \
  --config examples/mergeguard-config.yml
```

The example config customizes:

- `thresholds`
- `test_patterns`
- `dependency_patterns`
- `risk_paths`
- `risk_keywords`

## 8. Run MergeGuard On Your Own Branch

From inside your own Git repository, save a diff and PR description:

```bash
git diff origin/main...HEAD > /tmp/mergeguard.diff
```

Replace `origin/main` with your target branch if your repository uses a different default branch, such as `origin/master`.

Create a PR description file:

```bash
cat > /tmp/pr-description.md <<'EOF'
Requirement: describe the requirement or issue this PR addresses.

Expected behavior: describe what should happen after this change.

User impact: describe who is affected and how.

Acceptance criteria:
- Add the concrete behavior reviewers should check.

Tests run: describe the tests or manual checks you ran.

Rollback: describe how to revert or disable the change if needed.

Verified: describe the author review or validation performed.
EOF
```

Run the scan:

```bash
mergeguard scan \
  --diff /tmp/mergeguard.diff \
  --description /tmp/pr-description.md \
  --format markdown
```

## 9. Practical Review Loop

Use the report as a deterministic readiness checklist:

1. Fix Meaning warnings by improving the PR description.
2. Fix Evidence warnings by adding or updating tests, or explaining why no tests changed.
3. Review Risk findings before requesting review.
4. Review Guardrails findings for dependency, config, and large-change concerns.
5. Fix Explainability warnings by adding verification, rollback, or known-risk notes.

MergeGuard is intentionally low-noise. It does not replace code review; it helps make the PR ready for review.
