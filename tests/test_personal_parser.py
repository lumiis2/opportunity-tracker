import csv
from datetime import date

from src.core import create_calendar_events
from src.parsers.personal import EXPECTED_COLUMNS, parse


def write_csv(tmp_path, rows):
    path = tmp_path / "personal.csv"
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_personal_tracker_generates_deadline_and_estimated_periods(tmp_path):
    path = write_csv(
        tmp_path,
        [
            {
                "Programa": "UARE Winter",
                "Categoria": "Research internship",
                "Nível": "Undergrad",
                "Instituição / organização": "University of Alberta",
                "Deadline": "04/08/2026",
                "Período / data do programa": "Winter 2027",
                "Prioridade": "Alta",
                "Link": "https://www.ualberta.ca/example",
            },
            {
                "Programa": "UARE Summer",
                "Instituição / organização": "University of Alberta",
                "Período / data do programa": "Summer 2027",
            },
        ],
    )
    events = create_calendar_events(parse(path))

    assert [(event.title, event.start_date) for event in events] == [
        ("Application Deadline — UARE Winter", date(2026, 8, 4)),
        ("Expected Program Period — UARE Winter", date(2027, 1, 1)),
        ("Expected Program Period — UARE Summer", date(2027, 6, 1)),
    ]
    assert events[0].category == "Research internship"
    assert events[0].tags == ["Undergrad", "Alta"]
    assert events[0].id == "personal-uare-winter-university-of-alberta.application-deadline"
    assert events[0].url.startswith("https://www.ualberta.ca/")
    assert "Já apliquei?" not in events[0].description


def test_personal_tracker_accepts_markdown_link_and_exact_range(tmp_path):
    path = write_csv(
        tmp_path,
        [
            {
                "Programa": "Example",
                "Categoria": "Course",
                "Nível": "Undergrad",
                "Instituição / organização": "Org",
                "Período / data do programa": "10/09/2027 a 12/09/2027",
                "Link": "[Site](https://example.org)",
            }
        ],
    )

    event = create_calendar_events(parse(path))[0]
    assert event.start_date == date(2027, 9, 10)
    assert event.end_date == date(2027, 9, 13)
    assert event.url == "https://example.org"
