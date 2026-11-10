from pathlib import Path
from datetime import date

from src.parsers.graduation import parse


def test_graduation_parser_sample():
    sample = Path(__file__).resolve().parent / "data" / "graduation_sample.csv"
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


def test_expected_deadline_is_generated_without_duplicate_expected_open(tmp_path):
    source = Path(__file__).resolve().parent / "data" / "graduation_sample.csv"
    header = source.read_text(encoding="utf-8").splitlines()[0]
    values = [""] * len(header.split(","))
    columns = header.split(",")
    values[columns.index("Program")] = "Example"
    values[columns.index("Application Open")] = "2027-08-10"
    values[columns.index("Expected Open Month")] = "August 2027"
    values[columns.index("Expected Deadline Month")] = "September 2027"
    path = tmp_path / "graduation.csv"
    path.write_text(header + "\n" + ",".join(values) + "\n", encoding="utf-8")

    events = parse(path)
    assert [(event.title, event.start_date) for event in events] == [
        ("Application Opens — Example", date(2027, 8, 10)),
        ("Expected Application Deadline — Example", date(2027, 9, 1)),
    ]
