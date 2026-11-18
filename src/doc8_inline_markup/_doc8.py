"""Expose the inline-markup check to doc8."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from doc8.checks import ContentCheck

from doc8_inline_markup._rst import lint

if TYPE_CHECKING:
    from collections.abc import Iterator

    from doc8.parser import ParsedFile


_DIAGNOSTIC_CODE = "RST001"
_DIAGNOSTIC_MESSAGE = "Move inline code outside emphasis."


class CheckInlineMarkup(ContentCheck):
    """Report inline literals inside reStructuredText emphasis."""

    REPORTS = frozenset({_DIAGNOSTIC_CODE})

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
                yield line, _DIAGNOSTIC_CODE, _DIAGNOSTIC_MESSAGE
