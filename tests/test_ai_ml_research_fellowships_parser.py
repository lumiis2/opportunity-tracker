from datetime import date

import pytest

from src import cli
from src.core import create_calendar_events
from src.parsers.ai_ml_research_fellowships import parse


def _sample_lines():
    return open("data/ai_ml_research_fellowships.csv", encoding="utf-8").read().splitlines()


def test_continuously_open_program_becomes_calendar_event():
    events = create_calendar_events(parse("data/ai_ml_research_fellowships.csv"))

    event = next(event for event in events if event.title == "Applications Open Continuously — fast.ai")
    assert event.title == "Applications Open Continuously — fast.ai"
    assert event.start_date == date(date.today().year, 1, 1)
    assert event.url == "https://fast.ai"
    assert event.category == "Education"
    assert event.tags == ["Online Courses"]
    assert "Funding: Free" in event.description
    assert "Notes: Classic deep learning course" in event.description
    assert any(event.url == "https://learnmechinterp.com/topics/" for event in events)


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
