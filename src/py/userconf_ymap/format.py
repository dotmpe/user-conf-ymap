"""Substitute the layout daemon's argv placeholders."""

from __future__ import annotations

import re
import shlex

PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9\|_]*)\}")

filters = dict(
    str=str,
    hex=lambda x: (hex(int(x))),
    bit=lambda x: ('1' if x else '0'),
    revbit=lambda x: ('1' if not x else '0'),
)

def render_placeholders(template: str, values: dict[str, object]) -> str:
    """Replace placeholders like ``{id}``

    Unknown braces are left as written.
    """

    def repl(match: re.Match[str]) -> str:
        global filters
        key = match.group(1)
        vfilter = None
        if '|' in key:
            key, vfilter = key.split('|')
        if key not in values:
            return match.group(0)
        return filters[vfilter or 'str'](values[key])

    return PLACEHOLDER.sub(repl, template)

def render_placeholders_shell(template: str, values: dict[str, object]) -> str:
    """Replace placeholders like ``{id}``

    Unknown braces are left as written.
    Each inserted value is quoted for ``shlex`` / ``shell=True``.
    """

    data = render_placeholders(template, values)
    return {key: shlex.quote(value) for key, value in data.items()}

# vim:fenc=utf-8
