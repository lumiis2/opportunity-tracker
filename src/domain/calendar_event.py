from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator
from ics import Event


class CalendarEvent(BaseModel):
    """Schema-agnostic calendar output event."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    title: str
    start_date: date
    description: str = ""
    url: Optional[str] = None

    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, value: object) -> str:
        text = str(value).strip() if value is not None else ""
        if not text:
            raise ValueError("title cannot be empty")
        return text

    def to_ics_event(self) -> Event:
        event = Event(self.title)
        event.begin = self.start_date
        event.description = self.description
        event.make_all_day()
        return event
