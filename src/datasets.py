from __future__ import annotations

from pathlib import Path
from typing import Dict

# Registry mapping input CSV (relative to repo root) -> output ICS (relative path)
# Keep this registry editable so new datasets can be added without code changes.
DATASET_REGISTRY: Dict[Path, Path] = {
    Path("data/graduation_opportunities.csv"): Path("public/graduation.ics"),
    Path("data/master_programs.csv"): Path("public/masters.ics"),
    Path("data/conferences.csv"): Path("public/conferences.ics"),
}


def get_registry() -> Dict[Path, Path]:
    """Return a copy of the default dataset registry.

    Callers may modify or extend the returned mapping at runtime.
    """

    return dict(DATASET_REGISTRY)
