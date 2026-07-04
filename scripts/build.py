"""Build the graduation ICS calendar from the synced CSV."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core import generate_calendar
from src.parsers.graduation import parse


def main() -> int:
    csv_path = ROOT_DIR / "data" / "graduation.csv"
    output_path = ROOT_DIR / "output" / "graduation.ics"

    events = parse(csv_path)
    generate_calendar(events, output_path=output_path, calendar_name="Graduation Opportunities")

    print("Downloaded CSV:")
    print(csv_path.name)
    print()
    print("Events generated:")
    print(len(events))
    print()
    print("ICS written to:")
    print(f"output/{output_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

