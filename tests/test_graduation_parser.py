from pathlib import Path

from src.parsers.graduation import parse


def test_graduation_parser_sample(tmp_path):
    sample = Path("tests/data/graduation_sample.csv")
    events = parse(sample)

    # From the sample CSV we expect events for rows with dates:
    # Row A: Application Open + Deadline + Expected Open => 3
    # Row B: no explicit dates => 0
    # Row C: Expected Open Month => 1
    assert len(events) >= 4

    # Verify required fields exist on at least one event
    ev = events[0]
    assert getattr(ev, "title")
    assert getattr(ev, "start_date")
    assert getattr(ev, "description")

