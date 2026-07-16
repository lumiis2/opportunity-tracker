from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CALENDAR_URL = (
    "https://lumiis2.github.io/opportunity-tracker/"
    "ai_ml_research_fellowships.ics"
)
CSV_URL = (
    "https://lumiis2.github.io/opportunity-tracker/data/"
    "ai_ml_research_fellowships.csv"
)


def test_ai_ml_calendar_is_visible_on_public_index():
    contents = (ROOT / "public" / "index.html").read_text(encoding="utf-8")

    assert "AI/ML Research &amp; Fellowships" in contents
    assert contents.count(f'href="{CALENDAR_URL}"') == 2
    assert 'href="data/ai_ml_research_fellowships.csv"' in contents


def test_ai_ml_calendar_is_listed_in_readmes():
    english = (ROOT / "README.md").read_text(encoding="utf-8")
    portuguese = (ROOT / "README-pt.md").read_text(encoding="utf-8")

    for contents in (english, portuguese):
        assert CALENDAR_URL in contents
        assert CSV_URL in contents
