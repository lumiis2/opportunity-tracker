"""Print a concise Markdown summary of the publishing workflow."""

import json
import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def build_summary(root: Path, statuses: dict[str, str]) -> str:
    calendars_path = root / "output" / "calendars.json"
    calendars = (
        json.loads(calendars_path.read_text(encoding="utf-8"))
        if statuses["build"] == "success" and calendars_path.exists()
        else []
    )
    all_calendar = next(
        (calendar for calendar in calendars if calendar["id"] == "all"), {}
    )
    csv_count = (
        len(list((root / "data").glob("*.csv")))
        if statuses["sync"] == "success"
        else "—"
    )
    published_count = len(calendars) if statuses["deploy"] == "success" else "—"
    validation_errors = [
        f"{step}: {statuses[step]}"
        for step in ("tests", "build")
        if statuses[step] != "success"
    ]

    return "\n".join(
        [
            "## Calendar publishing report",
            "",
            "| Check | Result |",
            "| --- | ---: |",
            f"| CSVs synchronized | {csv_count} |",
            f"| Opportunities processed | {all_calendar.get('opportunity_count', '—')} |",
            f"| Events generated | {all_calendar.get('event_count', '—')} |",
            f"| Calendars published | {published_count} |",
            f"| Validation errors | {', '.join(validation_errors) or 'None'} |",
            "",
            "### Steps",
            "",
            *[f"- {name.title()}: **{status}**" for name, status in statuses.items()],
        ]
    )


def main() -> None:
    statuses = {
        "sync": os.getenv("SYNC_STATUS", "unknown"),
        "tests": os.getenv("TEST_STATUS", "unknown"),
        "build": os.getenv("BUILD_STATUS", "unknown"),
        "deploy": os.getenv("DEPLOY_STATUS", "unknown"),
    }
    print(build_summary(ROOT_DIR, statuses))


if __name__ == "__main__":
    main()
