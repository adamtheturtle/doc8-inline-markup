RST Inline Markup Lint
======================

Check reStructuredText for inline literals inside bold or italic text.
Docutils treats the inner backticks as text, which makes the code render
with visible backticks. This linter reports the location as RST001.

For example, change this note::

    .. note:: **``event_id`` deduplication**

to::

    .. note:: ``event_id`` deduplication

Command line
------------

Run the linter directly from GitHub with uv::

    uvx --from git+https://github.com/adamtheturtle/rst-inline-markup-lint rst-inline-markup-lint docs/guide.rst

Pass one or more UTF-8 files. Diagnostics use the format
``path:line: RST001 message``. The exit status is 0 for clean files,
1 for lint errors, and 2 for unreadable files or invalid arguments.

The linter checks each file with the standard Docutils RST parser. It skips
code blocks and comments. Run it on included files directly. Content in
extension directives that Docutils cannot parse is outside its scope.

prek and pre-commit
-------------------

Add this repository to your hook configuration:

.. code-block:: yaml

    repos:
      - repo: https://github.com/adamtheturtle/rst-inline-markup-lint
        rev: '2026.11.18'
        hooks:
          - id: rst-inline-markup-lint

The hook runs on reStructuredText files and uses Python 3.12 or newer.

Development
-----------

Run the tests and all lint stages with uv::

    uv run pytest --cov
    uv run prek run --all-files --hook-stage pre-commit
    uv run prek run --all-files --hook-stage pre-push
    uv run prek run --all-files --hook-stage manual
