"""Named pipeline presets and the composition root that builds one."""

from __future__ import annotations

import json
import logging
import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace

from .format import FILTERS, PlaceholderExpander
from .leaf import ConfigError, ContextError
from .resolve import YqResolver
from .store import build_json_store, build_null_store

log = logging.getLogger("user-conf-ymap.profile")


@dataclass(frozen=True)
class Profile:
    name: str
    resolver: str = "yq"
    defines: str = 'first(.definitions[]|select(type=="object"))'
    maps: str = ".maps"
    expander: str = "placeholder"
    filters: tuple[str, ...] = ("str", "hex", "bit", "revbit")
    store: str = "none"
    store_from: str | None = None


@dataclass
class Pipeline:
    profile: Profile
    resolver: object
    expander: object
    store: object


SETTINGS = Profile(name="settings")

PROFILES: dict[str, Profile] = {
    SETTINGS.name: SETTINGS,
}

RESOLVERS: dict[str, Callable[[], object]] = {
    "yq": YqResolver,
}

EXPANDERS: dict[str, Callable[[Mapping[str, Callable]], object]] = {
    "placeholder": PlaceholderExpander,
}

STORES: dict[str, Callable[[str | None], object]] = {
    "none": build_null_store,
    "json": build_json_store,
}


def parse_env_profile(value: str | None) -> tuple[str | None, str | None, str | None]:
    """Split ``UC_YMAP_PROFILE=name[,defines[,maps]]``.

    Empty fields are unset. The store is not part of this string.
    """

    if not value:
        return None, None, None
    parts = value.split(",")
    name = parts[0] or None
    defines = parts[1] if len(parts) > 1 and parts[1] else None
    maps = parts[2] if len(parts) > 2 and parts[2] else None
    return name, defines, maps


def read_document_profile(source: str, source_format: str | None) -> str | None:
    """Read the top-level ``profile`` scalar with a fixed reader.

    The pipeline resolver is chosen by this name, so the prelude cannot use it.
    A missing scalar returns ``None``. ``source_format`` omitted means YAML.
    """

    kind = (source_format or "yaml").lower()
    if kind == "json":
        return _profile_from_json(source)
    if kind in {"yaml", "yml"}:
        return _profile_from_yaml(source)
    raise ConfigError(f"unknown document format: {kind}")


def resolve_profile(
    *,
    name: str | None,
    defines: str | None,
    maps: str | None,
    resolver: str | None,
    expander: str | None,
    store: str | None,
    store_from: str | None,
    document_name: str | None,
    env: str | None,
) -> Profile:
    """Apply CLI, then env, then the document name, then the command default."""

    env_name, env_defines, env_maps = parse_env_profile(env)
    chosen = name or env_name or document_name or SETTINGS.name
    try:
        base = PROFILES[chosen]
    except KeyError:
        raise ConfigError(f"unknown profile: {chosen}") from None
    return replace(
        base,
        defines=defines or env_defines or base.defines,
        maps=maps or env_maps or base.maps,
        resolver=resolver or base.resolver,
        expander=expander or base.expander,
        store=store or base.store,
        store_from=store_from if store_from is not None else base.store_from,
    )


def build_pipeline(profile: Profile) -> Pipeline:
    """Resolve component names. This is the only place that constructs them."""

    try:
        resolver_type = RESOLVERS[profile.resolver]
    except KeyError:
        raise ConfigError(f"unknown resolver: {profile.resolver}") from None
    try:
        expander_type = EXPANDERS[profile.expander]
    except KeyError:
        raise ConfigError(f"unknown expander: {profile.expander}") from None
    try:
        store_type = STORES[profile.store]
    except KeyError:
        raise ConfigError(f"unknown store: {profile.store}") from None

    selected: dict[str, Callable] = {}
    for filter_name in profile.filters:
        try:
            selected[filter_name] = FILTERS[filter_name]
        except KeyError:
            raise ConfigError(f"unknown filter: {filter_name}") from None

    return Pipeline(
        profile=profile,
        resolver=resolver_type(),
        expander=expander_type(selected),
        store=store_type(profile.store_from),
    )


def _profile_from_json(source: str) -> str | None:
    try:
        with open(source, encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise ContextError(exc) from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"document is not valid JSON: {source}") from exc
    if not isinstance(data, dict):
        return None
    value = data.get("profile")
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ConfigError("document profile must be a string")
    return value


def _profile_from_yaml(source: str) -> str | None:
    log.info("Reading profile scalar from %s", source)
    try:
        result = subprocess.run(
            ["yq", "-r", ".profile", source],
            check=True,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        log.error("Profile prelude failed: %s", exc)
        raise ContextError(exc) from exc
    text = result.stdout.strip()
    if text in {"", "null"}:
        return None
    return text

# vim:fenc=utf-8
