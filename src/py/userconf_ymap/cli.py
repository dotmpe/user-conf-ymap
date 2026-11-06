"""Command-line entry point.

See doc/TOOL_USERCONF_YMAP_CLI.md for the manual.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from collections.abc import Mapping

from .leaf import ConfigError, ContextError
from .merge import run_merge_settings
from .profile import (
    Pipeline,
    build_pipeline,
    parse_env_profile,
    read_document_profile,
    resolve_profile,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="user-conf-ymap")
    parser.add_argument("--verbose")
    parser.add_argument("--debug")

    sub = parser.add_subparsers(dest="command", required=True)
    merge = sub.add_parser("merge")
    merge.add_argument("yml")
    merge.add_argument("select", nargs="*")
    merge.add_argument("--profile", default=None)
    merge.add_argument("-D", "--defines", default=None)
    merge.add_argument("-M", "--maps", default=None)
    merge.add_argument("-F", "--from", default=None, dest="source_format")
    merge.add_argument("--resolver", default=None)
    merge.add_argument("--expander", default=None)
    merge.add_argument("--store", default=None)
    merge.add_argument("--store-from", default=None)
    return parser.parse_args(argv)


def pipeline_for_merge(
    args: argparse.Namespace,
    environ: Mapping[str, str] | None = None,
) -> Pipeline:
    """Build the merge pipeline from CLI fields, the env, and the document."""

    env_map = os.environ if environ is None else environ
    env = env_map.get("UC_YMAP_PROFILE")
    env_name, _, _ = parse_env_profile(env)
    document_name = None
    if args.profile is None and env_name is None:
        document_name = read_document_profile(args.yml, args.source_format)
    profile = resolve_profile(
        name=args.profile,
        defines=args.defines,
        maps=args.maps,
        resolver=args.resolver,
        expander=args.expander,
        store=args.store,
        store_from=args.store_from,
        document_name=document_name,
        env=env,
    )
    return build_pipeline(profile)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    if args.command == "merge":
        try:
            pipeline = pipeline_for_merge(args)
            run_merge_settings(pipeline, args.yml, args.select)
        except (ConfigError, ContextError) as exc:
            print(f"user-conf-ymap: {exc}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()

# vim:fenc=utf-8
