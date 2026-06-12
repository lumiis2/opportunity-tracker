from __future__ import annotations

from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .calendar_event import CalendarEvent


class Conference(BaseModel):
    """Dataset-specific domain model for conferences."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    title: str
    organizer: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    deadline: Optional[date] = None
    expected_deadline_month: Optional[int] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    raw: dict[str, Any] = Field(default_factory=dict)

    @field_validator("title", mode="before")
    @classmethod
    def require_title(cls, value: object) -> str:
        text = str(value).strip() if value is not None else ""
        if not text:
            raise ValueError("field cannot be empty")
        return text

    @field_validator("organizer", "country", "city", "website", "notes", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @field_validator("expected_deadline_month")
    @classmethod
    def validate_month(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return None
        if not 1 <= value <= 12:
            raise ValueError("month must be between 1 and 12")
        return value

    def to_calendar_events(self, reference_date: Optional[date] = None, lead_months: int = 1) -> list[CalendarEvent]:
        if self.deadline is not None:
            return [
                CalendarEvent(
                    title=f"🚨 {self.title} Deadline",
                    start_date=self.deadline,
                    description="\n".join(
                        [
                            self.organizer or "",
                            self.country or "",
                            self.notes or "",
                        ]
                    ).strip(),
                    url=self.website,
                )
            ]

        if self.expected_deadline_month is not None:
            from .utils import reminder_date_for_month

            return [
                CalendarEvent(
                    title=f"🔍 Check {self.title}",
                    start_date=reminder_date_for_month(
                        self.expected_deadline_month,
                        reference_date=reference_date,
                        lead_months=lead_months,
                    ),
                    description=self.notes or "Verify official dates.",
                    url=self.website,
                )
            ]

        return []
