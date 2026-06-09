from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from .models import Opportunity


def parse_opportunities(csv_path: Path) -> List[Opportunity]:
    """Parse opportunity rows from a CSV file.

    Empty cells are preserved as blank strings so the model can normalize them.
    """

    frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    rows = frame.to_dict(orient="records")
    return [Opportunity.from_csv_row(row) for row in rows]
