"""Command-line interface for translating configuration files to JSON."""

import argparse
import json
import sys
from pathlib import Path

from src.configlang.errors import ConfigError
from src.configlang.parser import parse_source
from src.configlang.resolver import resolve_constants


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Translate the educational configuration language to JSON."
    )
    parser.add_argument("input_file", type=Path, help="Path to the input file")
    return parser


def main() -> int:
    """Read a source file, translate it, and print JSON to stdout."""
    args = build_parser().parse_args()
    try:
        source = args.input_file.read_text(encoding="utf-8")
        declarations = parse_source(source)
        result = resolve_constants(declarations)
    except (OSError, UnicodeError, ConfigError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
