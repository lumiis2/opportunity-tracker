"""Dataset-specific CSV parsers for normalized opportunities."""

from src.parsers.conferences import parse as parse_conferences
from src.parsers.ai_ml_research_fellowships import (
    parse as parse_ai_ml_research_fellowships,
)
from src.parsers.graduation import parse as parse_graduation
from src.parsers.industry import parse as parse_industry
from src.parsers.masters import parse as parse_masters
from src.parsers.personal import parse as parse_personal

__all__ = [
    "parse_ai_ml_research_fellowships",
    "parse_conferences",
    "parse_graduation",
    "parse_industry",
    "parse_masters",
    "parse_personal",
]
