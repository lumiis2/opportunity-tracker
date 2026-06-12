from __future__ import annotations

from datetime import date
from typing import Any, Iterable

import pandas as pd


def read_rows(csv_path) -> list[dict[str, Any]]:
    frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    return frame.to_dict(orient="records")


def text_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def parse_iso_date(value: Any) -> date | None:
    text = text_or_none(value)
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def first_month_from_text(values: Iterable[Any]) -> int | None:
    from ..domain.utils import parse_month_value

    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if not text:
            continue
        for token in text.replace("/", " ").replace(",", " ").split():
            month = parse_month_value(token)
            if month is not None:
                return month
        month = parse_month_value(text)
        if month is not None:
            return month
    return None
