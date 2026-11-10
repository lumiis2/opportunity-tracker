"""Build every configured calendar and the combined calendar."""

from __future__ import annotations

from pathlib import Path
import re
import sys

import yaml


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.cli import TRACKS
from src.core import (
    CalendarEvent,
    Opportunity,
    create_calendar_events,
    generate_calendar,
    validate_opportunities,
)


def load_datasets() -> dict[str, dict]:
    path = ROOT_DIR / "config.yaml"
    with path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)
    datasets = config.get("datasets") if isinstance(config, dict) else None
    if not isinstance(datasets, dict) or not datasets:
        raise ValueError("Invalid config: missing datasets")
    return datasets


def update_public_stats(event_counts: dict[str, int]) -> None:
    """Update event counters marked with data-track in the static page."""

    path = ROOT_DIR / "public" / "index.html"
    if not path.exists():
        return
    contents = path.read_text(encoding="utf-8")
    for track, count in event_counts.items():
        pattern = rf'(<div class="stats-number" data-track="{re.escape(track)}">)\d+(</div>)'
        contents, replacements = re.subn(pattern, rf"\g<1>{count}\g<2>", contents)
        if replacements != 1:
            raise ValueError(f"Missing or duplicate public statistic for track: {track}")
    path.write_text(contents, encoding="utf-8")


def main() -> int:
    datasets = load_datasets()
    all_events: list[CalendarEvent] = []
    counts: dict[str, int] = {}
    parsed: dict[str, list[Opportunity]] = {}

    unknown = sorted(set(datasets) - set(TRACKS))
    if unknown:
        raise ValueError(f"No parser registered for: {', '.join(unknown)}")

    for track, meta in datasets.items():
        parser, default_name = TRACKS[track]
        csv_name = meta.get("csv")
        output_name = meta.get("output")
        if not csv_name or not output_name:
            raise ValueError(f"Dataset {track} must define csv and output")

        parsed[track] = parser(ROOT_DIR / "data" / csv_name)

    validate_opportunities(
        [opportunity for opportunities in parsed.values() for opportunity in opportunities]
    )

    for track, meta in datasets.items():
        _, default_name = TRACKS[track]
        output_name = meta["output"]
        opportunities = parsed[track]
        events = create_calendar_events(opportunities)
        generate_calendar(
            events,
            output_path=ROOT_DIR / "output" / output_name,
            calendar_name=meta.get("calendar_name") or default_name,
        )
        counts[track] = len(events)
        all_events.extend(events)
        print(f"{track}: {len(events)} events -> output/{output_name}")

    generate_calendar(
        all_events,
        output_path=ROOT_DIR / "output" / "all.ics",
        calendar_name="All Opportunities",
    )
    counts["all"] = len(all_events)
    update_public_stats(counts)
    print(f"all: {len(all_events)} events -> output/all.ics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
