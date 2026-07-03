"""Preview parsed graduation opportunities.

For now, this script reads `data/graduation.csv`, parses it into
`CalendarEvent` objects, and prints a small summary.
"""

from __future__ import annotations

from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.parsers.graduation import parse


def main() -> int:
    csv_path = ROOT_DIR / "data" / "graduation.csv"
    events = parse(csv_path)
    print(f"number of events generated: {len(events)}")
    print("first few CalendarEvent objects:")
    for event in events[:5]:
        print(event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

