# MergeGuard

Deterministic review-readiness and governance checks for AI-assisted pull requests.

**AI may generate the diff. Engineers still own the merge.**

MergeGuard is not another AI code reviewer. It does not try to infer intent, judge code style, or replace human review. It is a low-noise, deterministic readiness layer that asks whether a pull request is prepared for responsible review before it reaches the merge button.

## Product Positioning

AI-assisted development changes the shape of code review. Teams now need fast ways to separate review-ready pull requests from diffs that are under-explained, under-tested, risky, or hard to own.

MergeGuard applies the MERGE Framework before code is merged:

- It checks review readiness, not code cleverness.
- It produces deterministic findings, not probabilistic review prose.
- It favors governance signals developers can act on quickly.
- It keeps ownership with engineers, even when AI helped generate the diff.

MVP 1 is intentionally local and boring in the best way: no network calls, no LLM review, no GitHub App, no SaaS dashboard, and no automatic PR commenting.

## MERGE Framework

MERGE is a lightweight checklist for AI-assisted pull requests:

- **Meaning**: Does the PR solve the right problem?
  Checks whether the PR description explains the requirement, expected behavior, issue, user impact, acceptance criteria, or why the change exists.
- **Evidence**: What proves the change works?
  Flags source changes that do not include matching test changes.
- **Risk**: What can this break?
  Detects configured risk keywords and risk-sensitive paths such as auth, payments, credentials, migrations, infrastructure, and config.
- **Guardrails**: Did the change respect system boundaries?
  Flags dependency/config changes and large PRs based on configured thresholds.
- **Explainability**: Can the developer explain the diff?
  Looks for author ownership signals such as tests run, rollback notes, known risks, manual review, or verification.

## Installation

MergeGuard requires Python 3.14 or newer.

Recommended development setup uses `uv`:

```bash
uv python install 3.14.5
uv sync --dev
```

Plain `pip` installation is also supported on Python 3.14+:

```bash
pip install mergeguard-cli
```

On macOS, Homebrew installation is available through this repository as a tap:

```bash
brew tap krpraveen0/mergeguard https://github.com/krpraveen0/mergeguard
brew trust krpraveen0/mergeguard
brew install krpraveen0/mergeguard/mergeguard-cli
```

The package/formula name is `mergeguard-cli`; the installed command is `mergeguard`.
The misspelled name `mergegaurd-cli` is not available.

For editable local development from this repository:

```bash
pip install -e .
```

Confirm the CLI is available:

```bash
mergeguard --help
```

When using `uv` without activating the virtual environment:

```bash
uv run mergeguard --help
```

## Quickstart

Run MergeGuard against the included risky example:

```bash
mergeguard scan \
  --diff examples/sample-risky.diff \
  --description examples/pr-description-weak.md \
  --format markdown
```

Or with `uv`:

```bash
uv run mergeguard scan \
  --diff examples/sample-risky.diff \
  --description examples/pr-description-weak.md \
  --format markdown
```

Try the safe example:

```bash
uv run mergeguard scan \
  --diff examples/sample-safe.diff \
  --description examples/pr-description-good.md \
  --format markdown
```

Supported output formats:

- `text`
- `markdown`
- `json`

The `markdown` format is designed for GitHub PR comments. It includes a compact status summary, diff stats, category findings, and readable inline file paths.

## Sample Output

The full sample report is available at [`examples/sample-report.md`](examples/sample-report.md).

```markdown
## MERGE Review Readiness Report

### Overall status: Needs attention

| Metric | Value |
| --- | ---: |
| Files changed | 2 |
| Additions | 7 |
| Deletions | 1 |

| Category | Status | Findings |
| --- | --- | ---: |
| Meaning | Needs attention | 1 |
| Evidence | Needs attention | 1 |
| Risk | Needs attention | 1 |
| Guardrails | Needs attention | 1 |
| Explainability | Needs attention | 1 |

### Meaning
- **WARNING**: PR description does not clearly explain expected behavior.

### Evidence
- **WARNING**: Source files changed but no test files were modified.

### Risk
- **HIGH**: Risk-sensitive terms found: payment, refund.

### Guardrails
- **WARNING**: Dependency file changed: package.json. (`package.json`)

### Explainability
- **WARNING**: No rollback note or author verification detail found.
```

## Configuration

MergeGuard automatically reads `.mergeguard.yml` or `.mergeguard.yaml` from the current directory when present. You can also pass a config file explicitly:

```bash
mergeguard scan \
  --diff examples/sample-risky.diff \
  --description examples/pr-description-weak.md \
  --format markdown \
  --config examples/mergeguard-config.yml
```

All settings are optional. Missing config files and missing keys fall back to deterministic defaults.

```yaml
thresholds:
  max_changed_files: 20
  max_line_changes: 500

test_patterns:
  - tests/
  - test_
  - _test
  - .test.
  - .spec.
  - __tests__

dependency_patterns:
  - requirements.txt
  - pyproject.toml
  - package.json
  - package-lock.json
  - yarn.lock
  - poetry.lock
  - go.mod
  - Cargo.toml
  - pom.xml
  - build.gradle

risk_paths:
  - src/payments/**
  - infra/**

risk_keywords:
  - auth
  - login
  - token
  - password
  - permission
  - role
  - payment
  - billing
  - invoice
  - refund
  - migration
  - delete
  - drop
  - encrypt
  - secret
  - credential
  - infra
  - terraform
  - config
```

## MVP Roadmap

MVP 1:

- Python CLI package
- Unified diff parser
- Deterministic MERGE rule engine
- `.mergeguard.yml` configuration
- Text, Markdown, and JSON renderers
- Example diffs, descriptions, and report output

Near-term:

- Exit-code policy for CI gating
- More precise config examples for common stacks
- Additional renderer fixtures
- Better large-PR and dependency-change explanations
- GitHub Actions usage documentation

Explicit non-goals for MVP 1:

- LLM-based code review
- GitHub App
- SaaS dashboard
- Automatic PR commenting
- Deep AST analysis
- Vulnerability scanner replacement
- External network calls

## Contributing

Use Python 3.14.5 and `uv` for local development:

```bash
uv sync --dev
uv run pytest
```

Before opening a PR:

- Keep rules deterministic and explainable.
- Keep the rule engine separate from the CLI.
- Add or update tests for parser, rules, renderers, and examples.
- Avoid unnecessary runtime dependencies.
- Preserve the product boundary: MergeGuard checks readiness and governance, not code quality by opinion.

Useful local checks:

```bash
uv run pytest
uv run mergeguard scan --diff examples/sample-risky.diff --description examples/pr-description-weak.md --format markdown
uv run mergeguard scan --diff examples/sample-safe.diff --description examples/pr-description-good.md --format json
```

## Release

Release readiness and publishing steps for `v0.1.0` are documented in [`RELEASE.md`](RELEASE.md).

## License

MergeGuard is licensed under the Apache License, Version 2.0. See [`LICENSE`](LICENSE).
