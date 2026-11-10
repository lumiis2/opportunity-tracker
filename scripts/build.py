"""Build every configured calendar and the combined calendar."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
import json
from pathlib import Path
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


def write_json(data: object, output_path: Path) -> None:
    """Write frontend data as readable JSON."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            data,
            default=date.isoformat,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


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

    all_opportunities = [
        opportunity for opportunities in parsed.values() for opportunity in opportunities
    ]
    validate_opportunities(all_opportunities)
    write_json(
        [asdict(opportunity) for opportunity in all_opportunities],
        ROOT_DIR / "output" / "opportunities.json",
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
    calendars = [
        {
            "id": track,
            "name": meta.get("calendar_name") or TRACKS[track][1],
            "ics_url": meta["output"],
            "csv_url": f"data/{meta['csv']}",
            "opportunity_count": len(parsed[track]),
            "event_count": counts[track],
        }
        for track, meta in datasets.items()
    ]
    calendars.append(
        {
            "id": "all",
            "name": "All Opportunities",
            "ics_url": "all.ics",
            "csv_url": None,
            "opportunity_count": len(all_opportunities),
            "event_count": len(all_events),
        }
    )
    write_json(calendars, ROOT_DIR / "output" / "calendars.json")
    print(f"all: {len(all_events)} events -> output/all.ics")
    print(f"opportunities: {len(all_opportunities)} -> output/opportunities.json")
    print(f"calendars: {len(calendars)} -> output/calendars.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
