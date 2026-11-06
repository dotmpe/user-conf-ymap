"""Object resolvers. A resolver turns a source path and a selector into one JSON value."""

from __future__ import annotations

import json
import logging
import os
import subprocess

from .leaf import ContextError

log = logging.getLogger("user-conf-ymap.resolve")

DEFAULT_YQ_COMMAND = 'yq -r "${1}" "${2}"'


class YqResolver:
    """Run a shell filter, default `yq`, and parse its stdout as JSON.

    ``UC_YMAP_OBJ_FILTER`` replaces the command when `command` is omitted.
    The selector and the source path are the two arguments after ``--``.
    """

    def __init__(self, command: str | None = None):
        if command is None:
            command = os.getenv("UC_YMAP_OBJ_FILTER", DEFAULT_YQ_COMMAND)
        self.command = command

    def resolve(self, source: str, selector: str) -> object:
        log.info("Resolving %s with %s", source, selector)
        try:
            result = subprocess.run(
                ["sh", "-c", self.command, "--", selector, source],
                check=True,
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            log.error("Object resolver failed: %s", exc)
            raise ContextError(exc) from exc
        return json.loads(result.stdout)

# vim:fenc=utf-8
