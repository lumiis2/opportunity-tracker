from pathlib import Path

import pytest

from src import cli


@pytest.mark.parametrize(
    ("track", "calendar_name"),
    [
        ("graduation", "Graduation Opportunities"),
        ("masters", "Masters Programs"),
        ("industry", "Industry Opportunities"),
        ("conferences", "Conferences"),
        ("ai_ml_research_fellowships", "AI/ML Research & Fellowships"),
    ],
)
def test_generate_ics_uses_official_track_parser(tmp_path, track, calendar_name):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / f"{track}.ics"

    result = cli.main(
        [
            "generate-ics",
            "--track",
            track,
            "--input",
            str(root / "data" / f"{track}.csv"),
            "--output",
            str(output),
        ]
    )

    assert result == 0
    contents = output.read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in contents
    assert "BEGIN:VEVENT" in contents
    assert f"X-WR-CALNAME:{calendar_name}" in contents


def test_generate_ics_reports_invalid_csv(tmp_path):
    csv_path = tmp_path / "invalid.csv"
    csv_path.write_text("unexpected\nvalue\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        cli.main(
            [
                "generate-ics",
                "--track",
                "graduation",
                "--input",
                str(csv_path),
                "--output",
                str(tmp_path / "calendar.ics"),
            ]
        )

    assert exc_info.value.code == 2
