from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_personal_calendar_is_visible_on_public_index_and_readmes():
    calendar_url = "https://lumiis2.github.io/opportunity-tracker/personal.ics"
    index = (ROOT / "public" / "index.html").read_text(encoding="utf-8")
    assert index.count(f'href="{calendar_url}"') == 2
    assert 'href="data/personal.csv"' in index

    for name in ("README.md", "README-pt.md"):
        contents = (ROOT / name).read_text(encoding="utf-8")
        assert calendar_url in contents
        assert "data/personal.csv" in contents
