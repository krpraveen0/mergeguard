# Release Readiness: v0.1.1

This document is the release runbook for publishing MergeGuard `v0.1.1`.

MergeGuard is a Python 3.14+ CLI package. The release should be built from a clean `master` checkout and published only after TestPyPI validation succeeds.

## Release Scope

Version `0.1.1` includes:

- `mergeguard scan`
- Deterministic MERGE rule engine
- Unified diff parsing for modified, added, deleted, and renamed files
- `.mergeguard.yml` configuration support
- Text, Markdown, and JSON renderers
- Example diffs, descriptions, config, and sample report
- Step-by-step usage documentation in `EXAMPLES.md`
- Pytest coverage for parser, engine, config, renderers, and CLI

## Package Metadata

Release metadata lives in `pyproject.toml`.

Before publishing, verify:

- `project.name` is `mergeguard-cli`
- `project.version` is `0.1.1`
- `mergeguard.__version__` is `0.1.1`
- `requires-python` is `>=3.14`
- `README.md` renders as the long description
- `project.urls` point to documentation, the GitHub repository, issues, and releases
- Package discovery includes only `mergeguard*`
- License metadata is `Apache-2.0`
- `LICENSE` contains `Copyright 2026 Praveen Kumar`

The package uses Apache-2.0 license metadata and includes the repository `LICENSE` file in built distributions.

## Build Instructions

Start from a clean checkout:

```bash
git switch master
git pull --ff-only origin master
git status --short
```

Install development dependencies:

```bash
uv python install 3.14.5
uv sync --dev
```

Run the full test suite:

```bash
uv run --python 3.14.5 pytest
```

Run representative CLI checks:

```bash
uv run --python 3.14.5 mergeguard --help
uv run --python 3.14.5 mergeguard scan --diff examples/sample-risky.diff --description examples/pr-description-weak.md --format markdown
uv run --python 3.14.5 mergeguard scan --diff examples/sample-safe.diff --description examples/pr-description-good.md --format json
```

Build source and wheel distributions:

```bash
uv build --python 3.14.5 --out-dir dist --clear
```

Expected artifacts:

```text
dist/mergeguard_cli-0.1.1.tar.gz
dist/mergeguard_cli-0.1.1-py3-none-any.whl
```

Dry-run the upload command before publishing:

```bash
uv publish --dry-run --trusted-publishing never dist/*
```

## Homebrew Formula Notes

The Homebrew formula lives in [`Formula/mergeguard-cli.rb`](Formula/mergeguard-cli.rb) and installs the published PyPI source distribution into a Homebrew-managed Python 3.14 virtual environment.

For each release:

- Update the formula `url` to the new PyPI source distribution
- Update the formula `sha256` from the released source distribution
- Keep the formula name as `mergeguard-cli`
- Keep the installed command as `mergeguard`
- Verify the formula through the tap with `brew install --build-from-source krpraveen0/mergeguard/mergeguard-cli`
- Run `brew test krpraveen0/mergeguard/mergeguard-cli`

Users can install from this repository as a tap:

```bash
brew tap krpraveen0/mergeguard https://github.com/krpraveen0/mergeguard
brew trust krpraveen0/mergeguard
brew install krpraveen0/mergeguard/mergeguard-cli
```

## TestPyPI Notes

Use TestPyPI before publishing to PyPI.

Create a TestPyPI API token and provide it through `UV_PUBLISH_TOKEN`. Do not commit tokens.

```bash
UV_PUBLISH_TOKEN="pypi-..." \
uv publish \
  --publish-url https://test.pypi.org/legacy/ \
  --check-url https://test.pypi.org/simple/mergeguard-cli/ \
  dist/*
```

Validate installation from TestPyPI in a fresh environment:

```bash
uv venv /tmp/mergeguard-testpypi --python 3.14.5
uv pip install \
  --python /tmp/mergeguard-testpypi/bin/python \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  mergeguard-cli==0.1.1
/tmp/mergeguard-testpypi/bin/mergeguard --help
```

TestPyPI may not mirror every dependency. MergeGuard has no runtime dependencies, but `--extra-index-url https://pypi.org/simple/` is included for consistency with common package validation flows.

## PyPI Notes

Publish to PyPI only after TestPyPI install validation succeeds.

Create a PyPI API token and provide it through `UV_PUBLISH_TOKEN`. Do not commit tokens.

```bash
UV_PUBLISH_TOKEN="pypi-..." \
uv publish \
  --publish-url https://upload.pypi.org/legacy/ \
  --check-url https://pypi.org/simple/mergeguard-cli/ \
  dist/*
```

Validate installation from PyPI in a fresh environment:

```bash
uv venv /tmp/mergeguard-pypi --python 3.14.5
uv pip install --python /tmp/mergeguard-pypi/bin/python mergeguard-cli==0.1.1
/tmp/mergeguard-pypi/bin/mergeguard --help
```

## Release Checklist

Pre-release:

- [ ] Confirm `master` is clean and synced with `origin/master`
- [ ] Confirm `pyproject.toml` distribution name is `mergeguard-cli`
- [ ] Confirm `pyproject.toml` version is `0.1.1`
- [ ] Confirm `mergeguard.__version__` is `0.1.1`
- [ ] Confirm Python requirement is `>=3.14`
- [ ] Confirm Apache-2.0 license metadata and copyright line
- [ ] Run `uv run --python 3.14.5 pytest`
- [ ] Run risky and safe sample CLI checks
- [ ] Confirm `README.md` includes product positioning, quickstart, sample output, roadmap, and contribution notes

Build:

- [ ] Remove stale artifacts with `uv build --python 3.14.5 --out-dir dist --clear`
- [ ] Confirm both sdist and wheel exist in `dist/`
- [ ] Inspect package metadata and wheel contents if needed
- [ ] Run `uv publish --dry-run --trusted-publishing never dist/*`

TestPyPI:

- [ ] Upload to TestPyPI
- [ ] Install `mergeguard-cli==0.1.1` from TestPyPI in a fresh environment
- [ ] Run `mergeguard --help`
- [ ] Run at least one sample scan from an installed package

PyPI:

- [ ] Upload to PyPI
- [ ] Install `mergeguard-cli==0.1.1` from PyPI in a fresh environment
- [ ] Run `mergeguard --help`
- [ ] Run at least one sample scan from an installed package

GitHub:

- [ ] Tag the release as `v0.1.1`
- [ ] Create GitHub release notes
- [ ] Link PyPI package from the GitHub release
- [ ] Close or update any release tracking issues
