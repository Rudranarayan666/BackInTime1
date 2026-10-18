"""Command-line entry point."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from backintime import __version__
from backintime.core.config import ConfigStore
from backintime.core.exceptions import BackInTimeError


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        prog="backintime",
        description="Independent snapshot backup application.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--config",
        type=Path,
        default=ConfigStore.default_path(),
        help="configuration file path",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("check-config", help="load and validate the configuration")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit status."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check-config":
        try:
            configuration = ConfigStore(args.config).load()
        except BackInTimeError as exc:
            print(f"Configuration error: {exc}", file=sys.stderr)
            return 1
        count = len(configuration.profiles)
        print(f"Configuration is valid ({count} profile{'s' if count != 1 else ''}).")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
