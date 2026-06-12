from __future__ import annotations

from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .calendar_event import CalendarEvent


class MasterProgram(BaseModel):
    """Dataset-specific domain model for master programs."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    program_id: str
    university: str
    program: str
    degree_type: Optional[str] = None
    country: str
    city: Optional[str] = None
    department: Optional[str] = None
    duration: Optional[str] = None
    program_website: Optional[str] = None
    research_areas: Optional[str] = None
    funding_type: Optional[str] = None
    funding_description: Optional[str] = None
    application_open: Optional[date] = None
    application_deadline: Optional[date] = None
    expected_open_month: Optional[int] = None
    expected_deadline_month: Optional[int] = None
    deadline_status: Optional[str] = None
    notes: Optional[str] = None
    raw: dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "program_id",
        "university",
        "program",
        "country",
        mode="before",
    )
    @classmethod
    def require_text(cls, value: object) -> str:
        text = str(value).strip() if value is not None else ""
        if not text:
            raise ValueError("field cannot be empty")
        return text

    @field_validator(
        "degree_type",
        "city",
        "department",
        "duration",
        "program_website",
        "research_areas",
        "funding_type",
        "funding_description",
        "deadline_status",
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
        """Extract calendar-facing events from the domain model."""

        events: list[CalendarEvent] = []

        if self.application_deadline is not None:
            events.append(
                CalendarEvent(
                    title=f"🚨 {self.program} Deadline",
                    start_date=self.application_deadline,
                    description="\n".join(
                        [
                            self.university,
                            self.country,
                            self.program_website or "",
                            self.notes or "",
                        ]
                    ).strip(),
                    url=self.program_website,
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
                            f"University: {self.university}",
                            f"Expected deadline month: {self.expected_deadline_month}",
                            "Verify official dates.",
                            self.notes or "",
                        ]
                    ).strip(),
                    url=self.program_website,
                )
            )

        return events
