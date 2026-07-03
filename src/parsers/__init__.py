"""Dataset-specific CSV parsers for turning rows into calendar events."""

from src.parsers.graduation import GraduationParser, parse

__all__ = ["GraduationParser", "parse"]

