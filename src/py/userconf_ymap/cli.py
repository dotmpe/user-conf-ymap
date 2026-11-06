"""Command-line entry point.

See doc/TOOL_USERCONF_YMAP_CLI.md for the manual.
"""

from __future__ import annotations

import argparse
import logging
import sys

from .leaf import ConfigError
from .merge import run_merge_settings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="user-conf-ymap")
    parser.add_argument("--verbose")
    parser.add_argument("--debug")

    sub = parser.add_subparsers(dest="command", required=True)
    merge = sub.add_parser("merge")
    merge.add_argument("yml")
    merge.add_argument("select", nargs='*')
    merge.add_argument("--profile", default='settings')
    merge.add_argument("--define",
                       default='first(.definitions[]|select(type=="object"))')
    merge.add_argument("--map", default='.maps')
    merge.add_argument("--from", default=None)

    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.debug: level = logging.DEBUG
    elif args.verbose: level = logging.INFO
    else: level = logging.WARNING
    logging.basicConfig(level=level,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    if args.command == "merge":
        try:
            run_merge_settings(args)
        except ConfigError as exc:
            print(f"user-conf-ymap: {exc}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()

# vim:fenc=utf-8
