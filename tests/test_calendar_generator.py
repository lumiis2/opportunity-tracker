from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from src.calendar_generator import build_calendar, generate_calendar
from src.models import Opportunity


class CalendarGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.deadline_opportunity = Opportunity(
            category="Scholarship",
            subcategory="Masters",
            program="Global Scholars",
            organization="Example Org",
            host_institution="Example University",
            country="Brazil",
            career_stage="Graduate",
            funding_type="Full funding",
            duration="2 years",
            application_deadline=date(2026, 7, 15),
            date_status="confirmed",
            deadline_confidence="high",
            official_website="https://example.com",
        )
        self.expected_opportunity = Opportunity(
            category="Fellowship",
            subcategory="Research",
            program="Future Fellows",
            organization="Another Org",
            host_institution="Another University",
            country="Chile",
            career_stage="Postdoc",
            funding_type="Partial funding",
            duration="1 year",
            expected_deadline_month=9,
            date_status="estimated",
            deadline_confidence="medium",
        )
        self.ignored_opportunity = Opportunity(
            category="Award",
            subcategory="Travel",
            program="No Dates",
            organization="Ignore Org",
            host_institution="Ignore University",
            country="Peru",
            career_stage="Student",
            funding_type="Stipend",
            duration="3 months",
            date_status="unknown",
            deadline_confidence="low",
        )

    def test_build_calendar_creates_expected_events(self) -> None:
        calendar = build_calendar(
            [self.deadline_opportunity, self.expected_opportunity, self.ignored_opportunity],
            reference_date=date(2026, 6, 9),
        )

        summaries = [event.name for event in calendar.events]
        self.assertEqual(
            summaries,
            ["🚨 Global Scholars Deadline", "🔍 Check Future Fellows"],
        )

        deadline_event = calendar.events[0]
        self.assertEqual(deadline_event.begin.date(), date(2026, 7, 15))
        self.assertEqual(
            deadline_event.description,
            "Example Org\nBrazil\nhttps://example.com",
        )

        expected_event = calendar.events[1]
        self.assertEqual(expected_event.begin.date(), date(2026, 8, 1))
        self.assertEqual(
            expected_event.description,
            "Expected deadline month:\nSeptember\n\nVerify official dates.",
        )

    def test_generate_calendar_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "graduation.ics"
            result = generate_calendar(
                [self.deadline_opportunity],
                output_path,
                reference_date=date(2026, 6, 9),
            )

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())

            content = output_path.read_text(encoding="utf-8")
            self.assertIn("BEGIN:VCALENDAR", content)
            self.assertIn("SUMMARY:🚨 Global Scholars Deadline", content)
            self.assertIn("DTSTART;VALUE=DATE:20260715", content)


if __name__ == "__main__":
    unittest.main()
