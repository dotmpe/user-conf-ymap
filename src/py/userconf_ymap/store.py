"""JSON store backends.

A backend may already hold preloaded profiles or parts. This slice opens
that document and does not address anything inside it.
"""

from __future__ import annotations

import json
import logging

from .leaf import ConfigError, ContextError

log = logging.getLogger("user-conf-ymap.store")


class NullStore:
    """Backend that loads nothing."""


class JsonStore:
    """One JSON document, retained and not interpreted."""

    def __init__(self, path: str):
        self.path = path
        try:
            with open(path, encoding="utf-8") as handle:
                self.document = json.load(handle)
        except OSError as exc:
            log.error("JSON store failed: %s", exc)
            raise ContextError(exc) from exc
        except json.JSONDecodeError as exc:
            raise ConfigError(f"JSON store is not valid JSON: {path}") from exc


def build_null_store(store_from: str | None) -> NullStore:
    return NullStore()


def build_json_store(store_from: str | None) -> JsonStore:
    if not store_from:
        raise ConfigError("json store requires store_from")
    return JsonStore(store_from)

# vim:fenc=utf-8
