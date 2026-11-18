"""Check the packaged doc8 entry point with doc8's CLI."""

from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    ("filename", "content", "expected_status"),
    [
        ("bad.rst", "**``event_id`` deduplication**\n", 1),
        ("good.rst", "``event_id`` deduplication\n", 0),
        ("notes.txt", "**``event_id`` deduplication**\n", 0),
    ],
)
def test_doc8(
    *,
    tmp_path: Path,
    filename: str,
    content: str,
    expected_status: int,
) -> None:
    """Detect nested literals only in RST files processed by doc8."""
    command = shutil.which("doc8")
    assert command is not None
    source = tmp_path / filename
    _ = source.write_text(f"Sample\n======\n\n{content}", encoding="utf-8")

    result = subprocess.run(
        [command, "--quiet", str(source)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == expected_status
    assert result.stderr == ""
    assert result.stdout.splitlines() == (
        [f"{source}:4: RST001 Move inline code outside emphasis."]
        if expected_status
        else []
    )
