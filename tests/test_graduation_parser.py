from pathlib import Path
from datetime import date

from src.core import create_calendar_events
from src.parsers.graduation import parse


def test_graduation_parser_sample():
    sample = Path(__file__).resolve().parent / "data" / "graduation_sample.csv"
    opportunities = parse(sample)

    assert len(opportunities) == 3
    assert [milestone.kind for milestone in opportunities[0].milestones] == [
        "application-open",
        "application-deadline",
    ]


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

    events = create_calendar_events(parse(path))
    assert [(event.title, event.start_date) for event in events] == [
        ("Application Opens — Example", date(2027, 8, 10)),
        ("Expected Application Deadline — Example", date(2027, 9, 1)),
    ]
