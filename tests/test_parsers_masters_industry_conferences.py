from pathlib import Path

from src.parsers.conferences import parse as parse_conferences
from src.parsers.industry import parse as parse_industry
from src.parsers.masters import parse as parse_masters


ROOT = Path(__file__).resolve().parents[1]


def _assert_basic_event_shape(events):
    assert events, "expected at least one CalendarEvent"
    event = events[0]
    assert event.title
    assert event.description
    assert event.start_date is not None


def test_masters_parser_reads_sample_csv():
    events = parse_masters(ROOT / "data" / "masters.csv")
    _assert_basic_event_shape(events)


def test_industry_parser_reads_sample_csv():
    events = parse_industry(ROOT / "data" / "industry.csv")
    _assert_basic_event_shape(events)


def test_conferences_parser_reads_sample_csv():
    events = parse_conferences(ROOT / "data" / "conferences.csv")
    _assert_basic_event_shape(events)
    assert any(event.end_date is not None for event in events)
