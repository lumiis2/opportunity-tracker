import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lumiis2.github.io/opportunity-tracker/"
CALENDARS = {
    "graduation": ("graduation.ics", "data/graduation.csv"),
    "masters": ("masters.ics", "data/masters.csv"),
    "industry": ("industry.ics", "data/industry.csv"),
    "conferences": ("conferences.ics", "data/conferences.csv"),
    "ai_ml_research_fellowships": (
        "ai_ml_research_fellowships.ics",
        "data/ai_ml_research_fellowships.csv",
    ),
    "personal": ("personal.ics", "data/personal.csv"),
    "all": ("all.ics", None),
}


def test_public_urls_are_preserved():
    readmes = [
        (ROOT / name).read_text(encoding="utf-8")
        for name in ("README.md", "README-pt.md")
    ]
    metadata = {
        calendar["id"]: calendar
        for calendar in json.loads(
            (ROOT / "output" / "calendars.json").read_text(encoding="utf-8")
        )
    }

    assert set(metadata) == set(CALENDARS)
    for track, (ics_path, csv_path) in CALENDARS.items():
        ics_url = BASE_URL + ics_path
        assert all(ics_url in readme for readme in readmes)
        assert metadata[track]["ics_url"] == ics_path
        assert metadata[track]["csv_url"] == csv_path

        if csv_path:
            assert all(BASE_URL + csv_path in readme for readme in readmes)


def test_public_index_loads_calendar_statistics():
    index = (ROOT / "public" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "public" / "app.js").read_text(encoding="utf-8")

    assert 'href="styles.css"' in index
    assert 'src="app.js"' in index
    assert 'src="banner.png"' in index
    assert (ROOT / "public" / "banner.png").exists()
    assert 'id="calendar-list"' in index
    assert 'aria-live="polite"' in index
    assert 'fetchJson("calendars.json")' in script
    assert 'fetchJson("opportunities.json")' in script
    assert "renderCalendars(calendars, opportunities)" in script
    assert "renderSummary(calendars)" in script
    assert "getHighlights(opportunities, track)" in script
    assert "calendar.event_count" in script
    assert "Calendars could not be loaded" in script


def test_calendar_actions_use_canonical_github_pages_urls():
    script = (ROOT / "public" / "app.js").read_text(encoding="utf-8")

    assert f'const CALENDAR_BASE_URL = "{BASE_URL}"' in script
    assert 'calendar.ics_url.replace(/^\\/+/, "")' in script
    assert "new URL(calendarPath, CALENDAR_BASE_URL).href" in script
    assert "window.location" not in script
    assert script.count('href="${calendarUrl}"') == 3


def test_pages_workflow_publishes_generated_files():
    workflow = (ROOT / ".github" / "workflows" / "deploy-pages.yml").read_text(
        encoding="utf-8"
    )

    assert "cp -v output/*.ics public/" in workflow
    assert "cp -v output/*.json public/" in workflow
    assert "cp -v data/*.csv public/data/" in workflow
