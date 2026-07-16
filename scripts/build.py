"""Build the graduation ICS calendar from the synced CSV."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core import generate_calendar
from src.parsers.graduation import parse as parse_graduation
from src.parsers.masters import parse as parse_masters
from src.parsers.industry import parse as parse_industry
from src.parsers.conferences import parse as parse_conferences
from src.parsers.ai_ml_research_fellowships import parse as parse_ai_ml_research_fellowships


def main() -> int:
    # Graduation calendar
    csv_path = ROOT_DIR / "data" / "graduation.csv"
    output_path = ROOT_DIR / "output" / "graduation.ics"

    events = parse_graduation(csv_path)
    generate_calendar(events, output_path=output_path, calendar_name="Graduation Opportunities")

    print("Downloaded CSV:")
    print(csv_path.name)
    print()
    print("Events generated:")
    print(len(events))
    print()
    print("ICS written to:")
    print(f"output/{output_path.name}")

    # Masters calendar (temporary build target for testing)
    masters_csv = ROOT_DIR / "data" / "masters.csv"
    masters_out = ROOT_DIR / "output" / "masters.ics"
    masters_events = parse_masters(masters_csv)
    generate_calendar(masters_events, output_path=masters_out, calendar_name="Masters Programs")
    print()
    print("Masters events generated:")
    print(len(masters_events))
    print("Masters ICS written to:")
    print(f"output/{masters_out.name}")
    
    # Industry calendar (temporary build target for testing)
    industry_csv = ROOT_DIR / "data" / "industry.csv"
    industry_out = ROOT_DIR / "output" / "industry.ics"
    industry_events = parse_industry(industry_csv)
    generate_calendar(industry_events, output_path=industry_out, calendar_name="Industry Opportunities")
    print()
    print("Industry events generated:")
    print(len(industry_events))
    print("Industry ICS written to:")
    print(f"output/{industry_out.name}")
    
    # Conferences calendar (temporary build target for testing)
    conferences_csv = ROOT_DIR / "data" / "conferences.csv"
    conferences_out = ROOT_DIR / "output" / "conferences.ics"
    conferences_events = parse_conferences(conferences_csv)
    generate_calendar(conferences_events, output_path=conferences_out, calendar_name="Conferences")
    print()
    print("Conferences events generated:")
    print(len(conferences_events))
    print("Conferences ICS written to:")
    print(f"output/{conferences_out.name}")

    ai_ml_csv = ROOT_DIR / "data" / "ai_ml_research_fellowships.csv"
    ai_ml_out = ROOT_DIR / "output" / "ai_ml_research_fellowships.ics"
    ai_ml_events = parse_ai_ml_research_fellowships(ai_ml_csv)
    generate_calendar(
        ai_ml_events,
        output_path=ai_ml_out,
        calendar_name="AI/ML Research & Fellowships",
    )
    print()
    print("AI/ML Research & Fellowships events generated:")
    print(len(ai_ml_events))
    print("AI/ML Research & Fellowships ICS written to:")
    print(f"output/{ai_ml_out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
