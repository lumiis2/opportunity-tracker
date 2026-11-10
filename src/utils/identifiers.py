"""Composition helpers for stable public identifiers."""

from __future__ import annotations

import re
import unicodedata


def opportunity_id(prefix: str, *parts: object) -> str:
    source = " ".join(str(part or "").strip() for part in parts if str(part or "").strip())
    normalized = unicodedata.normalize("NFKD", source).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    if not slug:
        raise ValueError("Cannot build an opportunity ID without a name")
    return f"{prefix}-{slug}"


def event_id(opportunity_id: str, kind: str) -> str:
    return f"{opportunity_id}.{kind}"
