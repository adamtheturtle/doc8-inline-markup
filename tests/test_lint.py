"""Exercise the linter through Docutils and the installed command."""

from __future__ import annotations

import codecs
import shutil
import subprocess
from typing import TYPE_CHECKING

import pytest

from rst_inline_markup_lint import lint

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


def test_cli(*, tmp_path: Path) -> None:
    """Check the installed command's output and exit codes."""
    command = shutil.which("rst-inline-markup-lint")
    assert command is not None
    clean = tmp_path / "clean.rst"
    bad = tmp_path / "bad.rst"
    missing = tmp_path / "missing.rst"
    invalid = tmp_path / "invalid.rst"
    _ = clean.write_text("``event_id`` deduplication\n", encoding="utf-8")
    _ = bad.write_bytes(codecs.BOM_UTF8 + b"\n**``event_id``**\n")
    _ = invalid.write_bytes(b"\xff")

    result = subprocess.run(
        [command, str(clean)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")

    result = subprocess.run(
        [command, str(clean), str(bad)],
        check=False,
        capture_output=True,
        text=True,
    )
    diagnostic = f"{bad}:2: RST001 Move inline code outside emphasis.\n"
    assert (result.returncode, result.stdout, result.stderr) == (
        1,
        diagnostic,
        "",
    )

    result = subprocess.run(
        [command, str(missing), str(bad), str(invalid)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert result.stdout == diagnostic
    assert f"{missing}:" in result.stderr
    assert f"{invalid}:" in result.stderr

    result = subprocess.run(
        [command],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert "FILE" in result.stderr
