"""Expose the inline-markup check to doc8."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from doc8.checks import ContentCheck

from rst_inline_markup_lint import DIAGNOSTIC_CODE, DIAGNOSTIC_MESSAGE, lint

if TYPE_CHECKING:
    from collections.abc import Iterator

    from doc8.parser import ParsedFile


class CheckInlineMarkup(ContentCheck):
    """Report inline literals inside reStructuredText emphasis."""

    REPORTS = frozenset({DIAGNOSTIC_CODE})

    @override
    def report_iter(
        self,
        parsed_file: ParsedFile,
    ) -> Iterator[tuple[int, str, str]]:
        if parsed_file.extension.lower() == ".rst":
            for line in lint(
                text=parsed_file.contents,
                source=parsed_file.filename,
            ):
                yield line, DIAGNOSTIC_CODE, DIAGNOSTIC_MESSAGE
