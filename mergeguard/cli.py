"""Command line interface for MergeGuard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable, Optional

from mergeguard.engine import MergeGuardEngine
from mergeguard.renderers import render_json, render_markdown, render_text


RenderFunction = Callable[[object], str]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mergeguard",
        description="Deterministic review-readiness checks for AI-assisted pull requests.",
    )
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan a diff and PR description for MERGE review-readiness.",
    )
    scan_parser.add_argument("--diff", required=True, help="Path to a unified diff file.")
    scan_parser.add_argument(
        "--description",
        required=True,
        help="Path to the pull request description file.",
    )
    scan_parser.add_argument(
        "--format",
        choices=("text", "markdown", "json"),
        default="text",
        help="Output format.",
    )
    scan_parser.set_defaults(func=run_scan)

    return parser


def run_scan(args: argparse.Namespace) -> int:
    diff_text = _read_file(args.diff)
    description = _read_file(args.description)

    report = MergeGuardEngine().scan(diff_text, description)
    renderer = _renderer_for(args.format)
    print(renderer(report), end="")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"mergeguard: file not found: {exc.filename}", file=sys.stderr)
        return 2


def _read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _renderer_for(format_name: str) -> RenderFunction:
    renderers: dict[str, RenderFunction] = {
        "text": render_text,
        "markdown": render_markdown,
        "json": render_json,
    }
    return renderers[format_name]


if __name__ == "__main__":
    raise SystemExit(main())
