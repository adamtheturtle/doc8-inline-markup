"""Lint inline code nested inside reStructuredText emphasis."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser
from docutils.parsers.rst.states import Inliner
from docutils.utils import escape2null, new_document

if TYPE_CHECKING:
    from re import Match
    from types import SimpleNamespace

type _InlineResult = tuple[
    str, list[nodes.Node], str, list[nodes.system_message]
]


class _LintInliner(Inliner):
    """Look for inline literals left as text by the emphasis handlers."""

    # Docutils interpolates these patterns from the concrete class namespace.
    simplename = Inliner.simplename
    emailc = Inliner.emailc
    non_whitespace_after = Inliner.non_whitespace_after
    non_whitespace_escape_before = Inliner.non_whitespace_escape_before
    uric = Inliner.uric
    uri_end = Inliner.uri_end
    non_unescaped_whitespace_escape_before = (
        Inliner.non_unescaped_whitespace_escape_before
    )

    def __init__(self) -> None:
        super().__init__()
        self.dispatch = {
            **self.dispatch,
            # Docutils dispatches to unbound methods with the inliner as
            # the first argument. types-docutils models these as bound.
            "*": _LintInliner._emphasis,  # type: ignore[dict-item]
            "**": _LintInliner._emphasis,  # type: ignore[dict-item]
        }
        self.lines: list[int] = []
        self._paragraph_lines = 0

    @override
    def parse(
        self,
        text: str,
        lineno: int,
        memo: SimpleNamespace,
        parent: nodes.Element,
    ) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        self._paragraph_lines = text.count("\n")
        return super().parse(text, lineno, memo, parent)

    def _emphasis(self, match: Match[str], lineno: int) -> _InlineResult:
        delimiter = match["start"]
        handler = Inliner.strong if delimiter == "**" else Inliner.emphasis
        before, inlines, remaining, messages = handler(self, match, lineno)
        if inlines and isinstance(inlines[0], (nodes.strong, nodes.emphasis)):
            raw = inlines[0].rawsource
            body = raw[len(delimiter) : -len(delimiter)]
            offset = self._literal_offset(text=body)
            if offset is not None:
                # Docutils passes the unconsumed suffix of the paragraph to
                # each inline handler and keeps its original line number.
                span_offset = self._paragraph_lines - match.string.count("\n")
                self.lines.append(
                    lineno + span_offset + before.count("\n") + offset
                )
        return before, list(inlines), remaining, messages

    def _literal_offset(self, *, text: str) -> int | None:
        escaped = escape2null(text)
        for match in self.patterns.initial.finditer(escaped):
            if match["start"] != "\x60\x60" or self.quoted_start(match):
                continue
            end = self.patterns.literal.search(escaped[match.end("start") :])
            if end and end.start(1):
                return escaped.count("\n", 0, match.start("start"))
        return None


def lint(*, text: str, source: str) -> list[int]:
    """Return the line of the first nested inline literal per emphasis span."""
    inliner = _LintInliner()
    parser = Parser(inliner=inliner)
    settings = get_default_settings(Parser)
    settings.file_insertion_enabled = False
    settings.raw_enabled = False
    settings.report_level = 5
    settings.halt_level = 6
    settings.syntax_highlight = "none"
    document = new_document(source, settings=settings)
    parser.parse(text, document)
    return sorted(inliner.lines)
