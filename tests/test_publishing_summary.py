import json

from scripts.publishing_summary import build_summary


def test_publishing_summary_reports_counts(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "one.csv").touch()
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "calendars.json").write_text(
        json.dumps(
            [
                {"id": "graduation", "opportunity_count": 2, "event_count": 3},
                {"id": "all", "opportunity_count": 2, "event_count": 3},
            ]
        ),
        encoding="utf-8",
    )

    summary = build_summary(
        tmp_path,
        {"sync": "success", "tests": "success", "build": "success", "deploy": "success"},
    )

    assert "| CSVs synchronized | 1 |" in summary
    assert "| Opportunities processed | 2 |" in summary
    assert "| Events generated | 3 |" in summary
    assert "| Calendars published | 2 |" in summary
    assert "| Validation errors | None |" in summary


def test_publishing_summary_does_not_report_stale_counts(tmp_path):
    summary = build_summary(
        tmp_path,
        {"sync": "failure", "tests": "skipped", "build": "skipped", "deploy": "skipped"},
    )

    assert "| CSVs synchronized | — |" in summary
    assert "| Opportunities processed | — |" in summary
    assert "| Calendars published | — |" in summary
    assert "| Validation errors | tests: skipped, build: skipped |" in summary
