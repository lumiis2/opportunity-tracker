from datetime import date

from src.parsers.personal import parse


def test_personal_tracker_generates_deadline_and_estimated_periods():
    events = parse("data/personal.csv")

    assert [(event.title, event.start_date) for event in events] == [
        ("Application Deadline — UARE Winter", date(2026, 8, 4)),
        ("Expected Program Period — UARE Winter", date(2027, 1, 1)),
        ("Expected Program Period — UARE Summer", date(2027, 6, 1)),
    ]
    assert events[0].category == "Research internship"
    assert events[0].tags == ["Undergrad", "Alta"]
    assert events[0].url.startswith("https://www.ualberta.ca/")
    assert "Já apliquei?" not in events[0].description


def test_personal_tracker_accepts_markdown_link_and_exact_range(tmp_path):
    header = open("data/personal.csv", encoding="utf-8").readline().strip()
    row = (
        "Example,Course,Undergrad,Org,AI,Remote,Online,2 days,N/A,N/A,"
        "10/09/2027 a 12/09/2027,Sim,None,Free,CV,Média,Open,"
        "[Site](https://example.org),Não"
    )
    path = tmp_path / "personal.csv"
    path.write_text(f"{header}\n{row}\n", encoding="utf-8")

    event = parse(path)[0]
    assert event.start_date == date(2027, 9, 10)
    assert event.end_date == date(2027, 9, 13)
    assert event.url == "https://example.org"
