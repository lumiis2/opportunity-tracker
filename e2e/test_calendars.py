import csv

from playwright.sync_api import expect


def test_homepage_loads_all_calendars(app_page):
    expect(app_page).to_have_title("Opportunity Tracker")
    expect(app_page.locator("#calendar-list article")).to_have_count(7)
    expect(
        app_page.get_by_role("heading", name="Graduation Opportunities", exact=True)
    ).to_be_visible()
    expect(
        app_page.get_by_role("heading", name="All Opportunities", exact=True)
    ).to_be_visible()


def test_overview_shows_built_opportunity_and_event_counts(app_page):
    expect(app_page.locator("#total-opportunities")).to_have_text("4")
    expect(app_page.locator("#total-events")).to_have_text("4")
    expect(app_page.locator("#category-counts")).to_contain_text(
        "4 Graduation Opportunities"
    )


def test_upcoming_dates_are_sorted_and_past_dates_are_hidden(app_page):
    card = app_page.get_by_role("article").filter(
        has=app_page.get_by_role(
            "heading", name="Graduation Opportunities", exact=True
        )
    )

    expect(card.locator(".highlights strong")).to_have_text(
        ["Early Program", "Estimated Program", "Late Program"]
    )
    expect(card.locator(".highlights span")).to_have_text(
        [
            "Jan 20, 2027 · application deadline",
            "Feb 1, 2027 · application deadline · estimated",
            "Mar 10, 2027 · application deadline",
        ]
    )
    expect(card).not_to_contain_text("Past Program")


def test_download_calendar_delivers_built_ics(app_page, tmp_path):
    link = app_page.get_by_role(
        "link", name="Download Graduation Opportunities", exact=True
    )
    expect(link).to_have_attribute(
        "href", "https://lumiis2.github.io/opportunity-tracker/graduation.ics"
    )

    with app_page.expect_download() as download_info:
        link.click()

    download = download_info.value
    destination = tmp_path / "graduation.ics"
    download.save_as(destination)
    contents = destination.read_text(encoding="utf-8")

    assert download.suggested_filename == "graduation.ics"
    assert "BEGIN:VCALENDAR" in contents
    assert "SUMMARY:Application Deadline — Early Program" in contents
    assert contents.count("BEGIN:VEVENT") == 4


def test_view_dataset_delivers_category_csv(app_page, tmp_path):
    with app_page.expect_download() as download_info:
        app_page.get_by_role(
            "link", name="View Graduation Opportunities dataset", exact=True
        ).click()

    destination = tmp_path / "graduation.csv"
    download_info.value.save_as(destination)
    with destination.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert [row["Program"] for row in rows] == [
        "Past Program",
        "Late Program",
        "Early Program",
        "Estimated Program",
    ]
