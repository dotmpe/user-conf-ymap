from __future__ import annotations

import json
import logging
import os
import subprocess

from dataclasses import dataclass

from .format import render_placeholders
from .leaf import ContextError

log = logging.getLogger("user-conf-ymap.merge")

filter_template = os.getenv('UC_YMAP_OBJ_FILTER', 'yq -r "${1}" "${2}"')


def run_merge(definitions, placeholders) -> None:
    data = {}
    for k, v in placeholders.items():
        data[k] = render_placeholders(v, definitions)
    return data

def run_merge_settings(args) -> None:
    datasets = {}
    for key in ('define', 'map'):
        selector = getattr(args, key)
        log.info("Loading JSON %s: %s", key, selector)
        try:
            result = subprocess.run(["sh", "-c", filter_template, "--",
                                     selector, args.yml],
                                    check=True, capture_output=True,
                                    text=True)
        except OSError as exc:
            log.error("Object resolver failed: %s", exc)
            raise ContextError(exc)

        datasets[key] = json.loads(result.stdout)

    if args.select: select = args.select
    else: select = datasets['map'].keys()

    for key in select:
        log.debug(f"Merging for {key} map {datasets['map'][key]}")
        data = run_merge(datasets['define'], datasets['map'][key])
        print(json.dumps(data))

# vim:fenc=utf-8
