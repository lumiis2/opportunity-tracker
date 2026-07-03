"""Reusable calendar event model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class CalendarEvent:
    """Normalized event data shared by all dataset parsers."""

    title: str
    description: str
    start_date: date
    end_date: date | None = None
    url: str | None = None
    category: str | None = None
    tags: list[str] = field(default_factory=list)
