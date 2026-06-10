from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from src.calendar_generator import build_calendar_report
from src.models import Opportunity
from src.parser import parse_opportunities


class CalendarLeadTimeTests(unittest.TestCase):
    def make_op(self, month: int) -> Opportunity:
        return Opportunity(
            category="X",
            subcategory="Y",
            program="P",
            organization="O",
            host_institution="H",
            country="Z",
            career_stage="Any",
            funding_type="None",
            duration="1",
            expected_deadline_month=month,
            date_status="estimated",
            deadline_confidence="medium",
        )

    def test_lead_months_shifts_reminder_backwards(self) -> None:
        opp = self.make_op(5)  # expected deadline May
        report = build_calendar_report([opp], reference_date=date(2025, 2, 15), lead_months=1)
        self.assertEqual(len(report.calendar.events), 1)
        ev = list(report.calendar.events)[0]
        self.assertEqual(ev.begin.date(), date(2025, 4, 1))

        report2 = build_calendar_report([opp], reference_date=date(2025, 2, 15), lead_months=3)
        ev2 = list(report2.calendar.events)[0]
        self.assertEqual(ev2.begin.date(), date(2025, 2, 1))

    def test_lead_months_crosses_year_boundary(self) -> None:
        opp = self.make_op(2)  # expected deadline Feb
        # reference in November => expected deadline is next year Feb
        report = build_calendar_report([opp], reference_date=date(2025, 11, 10), lead_months=1)
        ev = list(report.calendar.events)[0]
        self.assertEqual(ev.begin.date(), date(2026, 1, 1))

        report2 = build_calendar_report([opp], reference_date=date(2025, 11, 10), lead_months=3)
        ev2 = list(report2.calendar.events)[0]
        self.assertEqual(ev2.begin.date(), date(2025, 11, 1))


class ParserInvalidRowTests(unittest.TestCase):
    def test_parser_skips_invalid_rows(self) -> None:
        headers = Opportunity.csv_headers()
        valid = {
            "category": "A",
            "subcategory": "B",
            "program": "Good",
            "organization": "Org",
            "host_institution": "Inst",
            "country": "C",
            "career_stage": "All",
            "funding_type": "Full funding",
            "duration": "0",
            "expected_deadline_month": "May",
            "date_status": "estimated",
            "deadline_confidence": "medium",
        }
        invalid = dict(valid)
        invalid["program"] = "Bad"
        invalid["application_deadline"] = "not-a-date"

        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "test.csv"
            with path.open("w", encoding="utf-8") as fh:
                fh.write(",".join(headers) + "\n")
                fh.write(",".join(valid.get(h, "") for h in headers) + "\n")
                fh.write(",".join(invalid.get(h, "") for h in headers) + "\n")

            parsed = parse_opportunities(path)
            self.assertEqual(len(parsed), 1)
            self.assertEqual(parsed[0].program, "Good")


if __name__ == "__main__":
    unittest.main()
