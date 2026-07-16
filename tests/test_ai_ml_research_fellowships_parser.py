from datetime import date

import pytest

from src import cli
from src.parsers.ai_ml_research_fellowships import parse


def _sample_lines():
    return open("data/ai_ml_research_fellowships.csv", encoding="utf-8").read().splitlines()


def test_continuously_open_program_becomes_calendar_event():
    events = parse("data/ai_ml_research_fellowships.csv")

    assert len(events) == 2
    event = events[0]
    assert event.title == "Applications Open Continuously — fast.ai"
    assert event.start_date == date(date.today().year, 1, 1)
    assert event.url == "https://fast.ai"
    assert event.category == "Education"
    assert event.tags == ["Online Courses"]
    assert "Funding: Free" in event.description
    assert "Notes: Classic deep learning course" in event.description
    assert events[1].url == "https://learnmechinterp.com/topics/"


def test_exact_and_expected_dates_create_events(tmp_path):
    header, row = _sample_lines()[:2]
    row = row.replace(",Always Open,Always Open,Continuous,Continuous,", ",2027-02-01,,February 2027,March 2027,")
    csv_path = tmp_path / "dated.csv"
    csv_path.write_text(f"{header}\n{row}\n", encoding="utf-8")

    events = parse(csv_path)

    assert [(event.title, event.start_date) for event in events] == [
        ("Applications Open — fast.ai", date(2027, 2, 1)),
        ("Expected Application Deadline — fast.ai", date(2027, 3, 1)),
    ]


def test_month_only_cross_year_window_uses_following_year(tmp_path):
    header, row = _sample_lines()[:2]
    row = row.replace(
        ",Always Open,Always Open,Continuous,Continuous,",
        ",October,January,October,January,",
    )
    csv_path = tmp_path / "cross_year.csv"
    csv_path.write_text(f"{header}\n{row}\n", encoding="utf-8")

    events = parse(csv_path)

    assert events[0].start_date == date(date.today().year, 10, 1)
    assert events[1].start_date == date(date.today().year + 1, 1, 1)


def test_month_only_window_creates_open_and_deadline_events(tmp_path):
    header, row = _sample_lines()[:2]
    row = row.replace(
        ",Always Open,Always Open,Continuous,Continuous,",
        ",September,October,September,October,",
    )
    csv_path = tmp_path / "month_window.csv"
    csv_path.write_text(f"{header}\n{row}\n", encoding="utf-8")

    events = parse(csv_path)

    assert [(event.title, event.start_date) for event in events] == [
        ("Expected Applications Open — fast.ai", date(date.today().year, 9, 1)),
        ("Expected Application Deadline — fast.ai", date(date.today().year, 10, 1)),
    ]


def test_notes_column_is_required(tmp_path):
    header, row = _sample_lines()[:2]
    csv_path = tmp_path / "missing_notes.csv"
    csv_path.write_text(
        f"{header.rsplit(',', 1)[0]}\n{row.rsplit(',', 1)[0]}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing required columns: Notes"):
        parse(csv_path)


def test_cli_preserves_notes_and_links_in_generated_ics(tmp_path):
    output = tmp_path / "ai_ml.ics"

    result = cli.main(
        [
            "generate-ics",
            "--track",
            "ai_ml_research_fellowships",
            "--input",
            "data/ai_ml_research_fellowships.csv",
            "--output",
            str(output),
        ]
    )

    contents = output.read_text(encoding="utf-8")
    assert result == 0
    assert "X-WR-CALNAME:AI/ML Research & Fellowships" in contents
    assert "SUMMARY:Applications Open Continuously — fast.ai" in contents
    assert "Notes: Classic deep learning course" in contents
    assert "URL:https://fast.ai" in contents
