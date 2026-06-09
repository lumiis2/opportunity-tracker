from __future__ import annotations

import re
from calendar import month_name
from datetime import date
from typing import Any, Literal, Mapping, Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

CSV_HEADERS: tuple[str, ...] = (
    "category",
    "subcategory",
    "program",
    "organization",
    "host_institution",
    "country",
    "career_stage",
    "funding_type",
    "duration",
    "application_open",
    "application_deadline",
    "expected_open_month",
    "expected_deadline_month",
    "date_status",
    "deadline_confidence",
    "official_website",
    "notes",
)

_FIELD_ALIASES = {
    "category": "category",
    "subcategory": "subcategory",
    "program": "program",
    "organization": "organization",
    "host_institution": "host_institution",
    "host institution": "host_institution",
    "country": "country",
    "career_stage": "career_stage",
    "career stage": "career_stage",
    "funding_type": "funding_type",
    "funding type": "funding_type",
    "duration": "duration",
    "application_open": "application_open",
    "application open": "application_open",
    "application_deadline": "application_deadline",
    "application deadline": "application_deadline",
    "expected_open_month": "expected_open_month",
    "expected open month": "expected_open_month",
    "expected_deadline_month": "expected_deadline_month",
    "expected deadline month": "expected_deadline_month",
    "date_status": "date_status",
    "date status": "date_status",
    "deadline_confidence": "deadline_confidence",
    "deadline confidence": "deadline_confidence",
    "official_website": "official_website",
    "official website": "official_website",
    "notes": "notes",
}

_EMPTY_MARKERS = {"", "na", "n/a", "none", "null", "varies", "rolling", "continuous"}
_DATE_STATUS_ALIASES = {
    "confirmed": "confirmed",
    "estimated": "estimated",
    "historical": "historical",
    "unknown": "unknown",
}
_DEADLINE_CONFIDENCE_ALIASES = {
    "very high": "high",
    "high": "high",
    "medium": "medium",
    "low": "low",
}
_MONTH_LOOKUP = {
    month_name[index].lower(): index for index in range(1, 13)
}


class Opportunity(BaseModel):
    """Structured representation of an academic opportunity."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    category: str
    subcategory: str
    program: str
    organization: str
    host_institution: str
    country: str
    career_stage: str
    funding_type: str
    duration: str

    application_open: Optional[date] = None
    application_deadline: Optional[date] = None

    expected_open_month: Optional[int] = None
    expected_deadline_month: Optional[int] = None

    date_status: Literal["confirmed", "estimated", "historical", "unknown"]
    deadline_confidence: Literal["high", "medium", "low"]

    official_website: Optional[str] = None
    notes: Optional[str] = None

    @field_validator(
        "category",
        "subcategory",
        "program",
        "organization",
        "host_institution",
        "country",
        "career_stage",
        "funding_type",
        "duration",
        mode="before",
    )
    @classmethod
    def validate_required_text(cls, value: Any) -> str:
        if value is None:
            raise ValueError("field cannot be empty")
        text = str(value).strip()
        if not text:
            raise ValueError("field cannot be empty")
        return text

    @field_validator("official_website", "notes", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> Optional[str]:
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

    @model_validator(mode="after")
    def validate_dates(self) -> Opportunity:
        if self.application_open and self.application_deadline:
            if self.application_open > self.application_deadline:
                raise ValueError("application_open cannot be after application_deadline")
        return self

    @classmethod
    def from_csv_row(cls, row: Mapping[str, Any]) -> Opportunity:
        """Build an opportunity from a CSV row mapping."""

        def normalize_key(key: Any) -> Optional[str]:
            raw_key = str(key).strip().lower()
            raw_key = re.sub(r"[^a-z0-9]+", " ", raw_key).strip()
            return _FIELD_ALIASES.get(raw_key)

        def coerce_value(field: str, value: Any) -> Any:
            if value is None:
                return None
            if isinstance(value, str):
                stripped = value.strip()
                if not stripped or stripped.lower() in _EMPTY_MARKERS:
                    return None

                if field in {"application_open", "application_deadline"}:
                    return date.fromisoformat(stripped)

                if field in {"expected_open_month", "expected_deadline_month"}:
                    month_value = stripped.lower()
                    if month_value.isdigit():
                        return int(month_value)
                    if month_value in _MONTH_LOOKUP:
                        return _MONTH_LOOKUP[month_value]
                    return stripped

                if field == "date_status":
                    return _DATE_STATUS_ALIASES.get(stripped.lower(), stripped.lower())

                if field == "deadline_confidence":
                    return _DEADLINE_CONFIDENCE_ALIASES.get(stripped.lower(), stripped.lower())

                return stripped

            return value

        normalized = {}
        for key, value in row.items():
            field_name = normalize_key(key)
            if field_name is None:
                continue
            normalized[field_name] = coerce_value(field_name, value)

        return cls.model_validate(normalized)

    def to_csv_row(self) -> dict[str, str]:
        """Convert the model into a CSV-friendly row dictionary."""

        def serialize(value: Any) -> str:
            if value is None:
                return ""
            if isinstance(value, date):
                return value.isoformat()
            return str(value)

        data = self.model_dump()
        return {field: serialize(data.get(field)) for field in CSV_HEADERS}

    @classmethod
    def csv_headers(cls) -> tuple[str, ...]:
        """Return the expected CSV column order."""

        return CSV_HEADERS


AcademicOpportunity = Opportunity
