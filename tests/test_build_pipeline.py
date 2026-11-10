from pathlib import Path
import json
import shutil

import scripts.build as build


def test_build_pipeline_generates_ics(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]

    # Copy the current CSV inputs into a temporary workspace.
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "public").mkdir(parents=True, exist_ok=True)
    shutil.copy(root / "config.yaml", tmp_path / "config.yaml")
    shutil.copy(root / "public" / "index.html", tmp_path / "public" / "index.html")
    for name in [
        "graduation.csv",
        "masters.csv",
        "industry.csv",
        "conferences.csv",
        "ai_ml_research_fellowships.csv",
        "personal.csv",
    ]:
        shutil.copy(root / "data" / name, tmp_path / "data" / name)

    monkeypatch.setattr(build, "ROOT_DIR", tmp_path)

    code = build.main()
    assert code == 0

    for name in [
        "graduation.ics",
        "masters.ics",
        "industry.ics",
        "conferences.ics",
        "ai_ml_research_fellowships.ics",
        "personal.ics",
        "all.ics",
    ]:
        out = tmp_path / "output" / name
        assert out.exists()
        text = out.read_text(encoding="utf-8")
        assert "BEGIN:VCALENDAR" in text
        assert "BEGIN:VEVENT" in text

    combined = (tmp_path / "output" / "all.ics").read_text(encoding="utf-8")
    individual_count = sum(
        (tmp_path / "output" / name).read_text(encoding="utf-8").count("BEGIN:VEVENT")
        for name in [
            "graduation.ics", "masters.ics", "industry.ics", "conferences.ics",
            "ai_ml_research_fellowships.ics", "personal.ics",
        ]
    )
    assert combined.count("BEGIN:VEVENT") == individual_count
    assert 'data-track="all"' in (tmp_path / "public" / "index.html").read_text(encoding="utf-8")

    opportunities = json.loads(
        (tmp_path / "output" / "opportunities.json").read_text(encoding="utf-8")
    )
    assert opportunities
    assert set(opportunities[0]) == {
        "id",
        "track",
        "title",
        "description",
        "url",
        "category",
        "tags",
        "milestones",
    }
    assert opportunities[0]["milestones"][0]["start_date"]

    calendars = json.loads(
        (tmp_path / "output" / "calendars.json").read_text(encoding="utf-8")
    )
    assert [calendar["id"] for calendar in calendars] == [
        "graduation",
        "masters",
        "industry",
        "conferences",
        "ai_ml_research_fellowships",
        "personal",
        "all",
    ]
    assert {
        key: calendars[0][key]
        for key in ("id", "name", "ics_url", "csv_url")
    } == {
        "id": "graduation",
        "name": "Graduation Opportunities",
        "ics_url": "graduation.ics",
        "csv_url": "data/graduation.csv",
    }
    assert calendars[0]["opportunity_count"] == sum(
        opportunity["track"] == "graduation" for opportunity in opportunities
    )
    assert calendars[0]["event_count"] > 0
    assert calendars[-1]["ics_url"] == "all.ics"
    assert calendars[-1]["csv_url"] is None
