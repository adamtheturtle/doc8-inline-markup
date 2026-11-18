"""Command-line interface for rst-inline-markup-lint."""

import argparse
import sys
from pathlib import Path

from rst_inline_markup_lint import DIAGNOSTIC_CODE, DIAGNOSTIC_MESSAGE, lint


def main() -> int:
    """Check each supplied UTF-8 file and report its diagnostics."""
    parser = argparse.ArgumentParser(
        description="Flag inline literals inside reStructuredText emphasis."
    )
    parser.add_argument("files", nargs="+", type=Path, metavar="FILE")
    args = parser.parse_args()

    status = 0
    for path in args.files:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            print(f"{path}: {error}", file=sys.stderr)  # noqa: T201
            status = 2
            continue

        for line in lint(text=text, source=str(path)):
            print(  # noqa: T201
                f"{path}:{line}: {DIAGNOSTIC_CODE} {DIAGNOSTIC_MESSAGE}"
            )
            status = max(status, 1)
    return status
