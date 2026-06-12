from __future__ import annotations

from pathlib import Path
from typing import List

import logging
import pandas as pd

from .models import Opportunity
from .datasets import get_column_mapping


logger = logging.getLogger("opportunity-calendar.parser")


def parse_opportunities(csv_path: Path, column_mapping: dict | None = None) -> List[Opportunity]:
    """Parse opportunity rows from a CSV file.

    Args:
        csv_path: Path to the CSV file.
        column_mapping: Optional dict mapping actual CSV columns to Opportunity model fields.
                       If provided, renames columns in the dataframe before parsing.

    Rows that fail validation are skipped with a warning. This keeps the
    parser resilient against single malformed rows instead of failing the
    entire import.
    """

    frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    
    # Apply column mapping if provided (or auto-detect from dataset registry)
    if column_mapping is None:
        column_mapping = get_column_mapping(csv_path)
    
    if column_mapping:
        # Rename columns according to mapping (only rename columns that exist)
        rename_dict = {k: v for k, v in column_mapping.items() if k in frame.columns}
        if rename_dict:
            frame = frame.rename(columns=rename_dict)
            logger.debug("Remapped columns: %s", rename_dict)
    
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
