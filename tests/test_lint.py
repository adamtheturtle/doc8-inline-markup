"""Exercise the inline-markup check through Docutils."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from doc8_inline_markup._rst import lint

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    ("text", "lines"),
    [
        (".. note:: **``event_id`` deduplication**\n", [1]),
        ("*Use ``event_id`` for lookup.*\n", [1]),
        ("First line.\n**Use\n``event_id`` here.**\n", [3]),
        ("``ok``\n**``first``** and **``second``**\n", [2, 2]),
        ("**``first`` and ``second``**\n", [1]),
        ("**Use ``event\nid`` here.**\n", [1]),
        ("**Documentation** and ``event_id``.\n", []),
        ("**An unmatched ``marker**\n", []),
        ("**A quoted pair '``' and ``.**\n", []),
        ("**An escaped \\\x60\x60event_id``.**\n", []),
        ("**``event_id`` with an unclosed span.\n", []),
        (".. comment **``event_id``**\n", []),
        (".. code-block:: rst\n\n   **``event_id``**\n", []),
        ("Example::\n\n   **``event_id``**\n", []),
        ("``**event_id**``\n", []),
        (".. extension-directive::\n\n   **``event_id``**\n", []),
    ],
)
def test_inline_markup(*, text: str, lines: list[int]) -> None:
    """Report emphasis spans that contain an inline literal."""
    assert lint(text=text, source="test.rst") == lines


def test_include_is_not_read(*, tmp_path: Path) -> None:
    """Leave included documents for independent lint runs."""
    included = tmp_path / "included.rst"
    _ = included.write_text("**``event_id``**\n", encoding="utf-8")
    source = tmp_path / "guide.rst"
    assert lint(text=".. include:: included.rst\n", source=str(source)) == []
