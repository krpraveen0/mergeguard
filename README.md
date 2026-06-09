# MergeGuard

Deterministic review-readiness and governance checks for AI-assisted pull requests using the MERGE Framework.

AI may generate the diff. Engineers still own the merge.

MergeGuard is not another AI code reviewer. It is a low-noise governance layer that checks whether a pull request is ready for human review before it is merged.

## Install

MergeGuard requires Python 3.14 or newer.

For development, use `uv`:

```bash
uv python install 3.14.5
uv sync --dev
uv run mergeguard --help
uv run pytest
```

Plain `pip` installation is also supported when running on Python 3.14+:

```bash
pip install -e .
```

## Usage

```bash
mergeguard scan --diff examples/sample-risky.diff --description examples/pr-description-weak.md --format markdown
```

Supported formats:

- `text`
- `markdown`
- `json`

## MERGE Framework

- Meaning: Does the PR solve the right problem?
- Evidence: What proves the change works?
- Risk: What can this break?
- Guardrails: Did the change respect system boundaries?
- Explainability: Can the developer explain the diff?

## MVP Scope

MergeGuard MVP 1 is deterministic. It does not make external network calls, use LLM-based code review, perform deep AST analysis, or replace vulnerability scanners.
