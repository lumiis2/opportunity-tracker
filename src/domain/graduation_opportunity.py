from __future__ import annotations

from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .calendar_event import CalendarEvent


class GraduationOpportunity(BaseModel):
    """Dataset-specific domain model for graduation/research opportunities."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    category: str
    subcategory: str
    program: str
    organization: str
    host_institution: str
    country: str
    career_stage: str
    funding_type: str
    funding_details: Optional[str] = None
    duration: Optional[str] = None
    application_open: Optional[date] = None
    application_deadline: Optional[date] = None
    expected_open_month: Optional[int] = None
    expected_deadline_month: Optional[int] = None
    date_status: str = "unknown"
    deadline_confidence: str = "low"
    application_effort: Optional[str] = None
    prestige_score: Optional[int] = None
    funding_score: Optional[int] = None
    fit_score: Optional[int] = None
    official_website: Optional[str] = None
    notes: Optional[str] = None
    raw: dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "category",
        "subcategory",
        "program",
        "organization",
        "host_institution",
        "country",
        "career_stage",
        "funding_type",
        mode="before",
    )
    @classmethod
    def require_text(cls, value: object) -> str:
        text = str(value).strip() if value is not None else ""
        if not text:
            raise ValueError("field cannot be empty")
        return text

    @field_validator(
        "funding_details",
        "duration",
        "application_effort",
        "official_website",
        "notes",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @field_validator("expected_open_month", "expected_deadline_month")
    @classmethod
    def validate_month(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return None
        if not 1 <= value <= 12:
            raise ValueError("month must be between 1 and 12")
        return value

    def to_calendar_events(self, reference_date: Optional[date] = None, lead_months: int = 1) -> list[CalendarEvent]:
        events: list[CalendarEvent] = []

        if self.application_deadline is not None:
            events.append(
                CalendarEvent(
                    title=f"🚨 {self.program} Deadline",
                    start_date=self.application_deadline,
                    description="\n".join(
                        [
                            self.organization,
                            self.country,
                            self.official_website or "",
                            self.notes or "",
                        ]
                    ).strip(),
                    url=self.official_website,
                )
            )
            return events

        if self.expected_deadline_month is not None:
            from .utils import reminder_date_for_month

            start_date = reminder_date_for_month(
                self.expected_deadline_month,
                reference_date=reference_date,
                lead_months=lead_months,
            )
            events.append(
                CalendarEvent(
                    title=f"🔍 Check {self.program}",
                    start_date=start_date,
                    description="\n".join(
                        [
                            self.organization,
                            f"Expected deadline month: {self.expected_deadline_month}",
                            "Verify official dates.",
                            self.notes or "",
                        ]
                    ).strip(),
                    url=self.official_website,
                )
            )

        return events
