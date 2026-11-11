"""Normalized opportunity models shared by every data source."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class Milestone:
    """A dated step in an opportunity, such as an application deadline."""

    kind: str
    title: str
    start_date: date
    end_date: date | None = None
    estimated: bool = False


@dataclass(slots=True)
class Opportunity:
    """An opportunity normalized from one source row."""

    id: str
    track: str
    title: str
    description: str
    url: str | None = None
    category: str | None = None
    tags: list[str] = field(default_factory=list)
    milestones: list[Milestone] = field(default_factory=list)
