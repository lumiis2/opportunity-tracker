"""Dataset-specific CSV parsers for turning rows into calendar events."""

from src.parsers.conferences import ConferenceParser, parse as parse_conferences
from src.parsers.ai_ml_research_fellowships import (
	AiMlResearchFellowshipsParser,
	parse as parse_ai_ml_research_fellowships,
)
from src.parsers.graduation import GraduationParser, parse as parse_graduation
from src.parsers.industry import IndustryParser, parse as parse_industry
from src.parsers.masters import MastersParser, parse as parse_masters

__all__ = [
	"ConferenceParser",
	"AiMlResearchFellowshipsParser",
	"GraduationParser",
	"IndustryParser",
	"MastersParser",
	"parse_conferences",
	"parse_ai_ml_research_fellowships",
	"parse_graduation",
	"parse_industry",
	"parse_masters",
]
