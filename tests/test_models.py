from __future__ import annotations

import unittest
from datetime import date

from src.models import Opportunity


class OpportunityModelTests(unittest.TestCase):
    def test_csv_round_trip(self) -> None:
        row = {
            "category": "Scholarship",
            "subcategory": "Masters",
            "program": "Global Scholars",
            "organization": "Example Org",
            "host_institution": "Example University",
            "country": "Brazil",
            "career_stage": "Graduate",
            "funding_type": "Full funding",
            "duration": "2 years",
            "application_open": "2026-06-01",
            "application_deadline": "2026-07-15",
            "expected_open_month": "6",
            "expected_deadline_month": "7",
            "date_status": "confirmed",
            "deadline_confidence": "high",
            "official_website": "https://example.com",
            "notes": "  Apply early  ",
        }

        opportunity = Opportunity.from_csv_row(row)

        self.assertEqual(opportunity.application_open, date(2026, 6, 1))
        self.assertEqual(opportunity.application_deadline, date(2026, 7, 15))
        self.assertEqual(opportunity.expected_open_month, 6)
        self.assertEqual(opportunity.expected_deadline_month, 7)
        self.assertEqual(opportunity.notes, "Apply early")

        serialized = opportunity.to_csv_row()
        self.assertEqual(serialized["application_open"], "2026-06-01")
        self.assertEqual(serialized["application_deadline"], "2026-07-15")
        self.assertEqual(serialized["expected_open_month"], "6")
        self.assertEqual(serialized["expected_deadline_month"], "7")
        self.assertEqual(serialized["notes"], "Apply early")

    def test_invalid_month_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Opportunity(
                category="Scholarship",
                subcategory="Masters",
                program="Program",
                organization="Org",
                host_institution="Institution",
                country="Country",
                career_stage="Graduate",
                funding_type="Full",
                duration="1 year",
                expected_deadline_month=13,
                date_status="estimated",
                deadline_confidence="medium",
            )

    def test_deadline_cannot_precede_open(self) -> None:
        with self.assertRaises(ValueError):
            Opportunity(
                category="Scholarship",
                subcategory="Masters",
                program="Program",
                organization="Org",
                host_institution="Institution",
                country="Country",
                career_stage="Graduate",
                funding_type="Full",
                duration="1 year",
                application_open=date(2026, 7, 1),
                application_deadline=date(2026, 6, 1),
                date_status="confirmed",
                deadline_confidence="high",
            )


if __name__ == "__main__":
    unittest.main()
