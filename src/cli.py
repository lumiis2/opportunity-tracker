"""Command-line interface for local calendar generation."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Optional, Sequence, Union

from src.core import CalendarEvent, generate_calendar
from src.parsers import (
    parse_ai_ml_research_fellowships,
    parse_conferences,
    parse_graduation,
    parse_industry,
    parse_masters,
)


Parser = Callable[[Union[str, Path]], list[CalendarEvent]]

TRACKS: dict[str, tuple[Parser, str]] = {
    "ai_ml_research_fellowships": (
        parse_ai_ml_research_fellowships,
        "AI/ML Research & Fellowships",
    ),
    "graduation": (parse_graduation, "Graduation Opportunities"),
    "masters": (parse_masters, "Masters Programs"),
    "industry": (parse_industry, "Industry Opportunities"),
    "conferences": (parse_conferences, "Conferences"),
}


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="opportunity-calendar",
        description="Generate an ICS calendar from a local Opportunity Tracker CSV.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser(
        "generate-ics",
        help="Generate an ICS file without Google Sheets or network access.",
    )
    generate.add_argument(
        "--track",
        required=True,
        choices=TRACKS,
        help="Official CSV schema/parser to use.",
    )
    generate.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to a CSV using the selected track's official columns.",
    )
    generate.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path where the generated ICS file will be written.",
    )
    generate.add_argument(
        "--calendar-name",
        help="Optional calendar display name; defaults to the official track name.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    if args.command == "generate-ics":
        track_parser, default_name = TRACKS[args.track]
        try:
            events = track_parser(args.input)
            generate_calendar(
                events,
                output_path=args.output,
                calendar_name=args.calendar_name or default_name,
            )
        except (OSError, ValueError) as exc:
            parser.error(str(exc))

        print(f"Generated {len(events)} events in {args.output}")
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
