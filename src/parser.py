from __future__ import annotations

from pathlib import Path
from typing import List

import logging
import pandas as pd

from .models import Opportunity


logger = logging.getLogger("opportunity-calendar.parser")


def parse_opportunities(csv_path: Path) -> List[Opportunity]:
    """Parse opportunity rows from a CSV file.

    Rows that fail validation are skipped with a warning. This keeps the
    parser resilient against single malformed rows instead of failing the
    entire import.
    """

    frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    rows = frame.to_dict(orient="records")

    opportunities: List[Opportunity] = []
    for idx, row in enumerate(rows, start=1):
        try:
            opp = Opportunity.from_csv_row(row)
        except Exception as exc:  # validation/parsing error for this row
            logger.warning("Skipping row %s in %s due to parse error: %s", idx, csv_path, exc)
            continue
        opportunities.append(opp)

    return opportunities
