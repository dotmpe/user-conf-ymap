"""Substitute placeholders and expand one map template."""

from __future__ import annotations

import re
import shlex
from collections.abc import Callable, Mapping

PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9\|_]*)\}")

FILTERS: dict[str, Callable[[object], str]] = {
    "str": str,
    "hex": lambda x: (hex(int(x))),
    "bit": lambda x: ('1' if x else '0'),
    "revbit": lambda x: ('1' if not x else '0'),
}


class PlaceholderExpander:
    """Expand ``{key|filter}`` strings in a flat map template."""

    def __init__(self, value_filters: Mapping[str, Callable[[object], str]] | None = None):
        self.filters = dict(FILTERS if value_filters is None else value_filters)

    def expand(self, definitions: dict, template: dict) -> dict:
        return {
            key: render_placeholders(value, definitions, self.filters)
            for key, value in template.items()
        }


def render_placeholders(
    template: str,
    values: dict[str, object],
    value_filters: Mapping[str, Callable[[object], str]] | None = None,
) -> str:
    """Replace placeholders like ``{id}``

    Unknown braces are left as written.
    ``value_filters`` defaults to the built-in registry.
    """

    active = FILTERS if value_filters is None else value_filters

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        vfilter = None
        if '|' in key:
            key, vfilter = key.split('|')
        if key not in values:
            return match.group(0)
        return active[vfilter or 'str'](values[key])

    return PLACEHOLDER.sub(repl, template)

def render_placeholders_shell(template: str, values: dict[str, object]) -> str:
    """Replace placeholders like ``{id}``

    Unknown braces are left as written.
    Each inserted value is quoted for ``shlex`` / ``shell=True``.
    """

    data = render_placeholders(template, values)
    return {key: shlex.quote(value) for key, value in data.items()}

# vim:fenc=utf-8
