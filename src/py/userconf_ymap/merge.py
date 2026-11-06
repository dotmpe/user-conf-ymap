from __future__ import annotations

import json
import logging
from collections.abc import Sequence

from .format import PlaceholderExpander
from .profile import Pipeline

log = logging.getLogger("user-conf-ymap.merge")


def run_merge(definitions, placeholders, expander=None) -> dict:
    if expander is None:
        expander = PlaceholderExpander()
    return expander.expand(definitions, placeholders)


def run_merge_settings(pipeline: Pipeline, source: str, select: Sequence[str]) -> None:
    selectors = {
        "definitions": pipeline.profile.defines,
        "maps": pipeline.profile.maps,
    }
    datasets = {}
    for slot, selector in selectors.items():
        log.info("Loading JSON %s: %s", slot, selector)
        datasets[slot] = pipeline.resolver.resolve(source, selector)

    chosen = select if select else datasets["maps"].keys()

    for key in chosen:
        log.debug("Merging for %s map %s", key, datasets["maps"][key])
        data = run_merge(datasets["definitions"], datasets["maps"][key], pipeline.expander)
        print(json.dumps(data))

# vim:fenc=utf-8
