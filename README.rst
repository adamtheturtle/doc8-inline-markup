doc8 Inline Markup
==================

A doc8 plugin that detects inline literals inside bold or italic
reStructuredText. Docutils treats the inner backticks as text, which
makes the code render with visible backticks. The check reports RST001.

For example, change this note::

    .. note:: **``event_id`` deduplication**

to::

    .. note:: ``event_id`` deduplication

Installation
------------

Install the plugin in the same environment as doc8. For a uv project,
add it as a development dependency::

    uv add --dev "doc8-inline-markup @ git+https://github.com/adamtheturtle/doc8-inline-markup@2026.11.18.2"

Run doc8 as usual::

    uv run doc8 docs/guide.rst

doc8 discovers the plugin automatically. It checks .rst files, skips code
blocks and comments, and supports doc8's standard ignore settings. Run doc8
on included files directly. Content in extension directives that Docutils
cannot parse is outside the check's scope.

If you used rst-inline-markup-lint, replace that dependency with
doc8-inline-markup and remove any standalone hook entry for the old package.
