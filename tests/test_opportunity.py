from datetime import date

from src.core import Milestone, Opportunity, create_calendar_events


def test_opportunity_holds_normalized_data():
    deadline = Milestone(
        kind="application-deadline",
        title="Application Deadline — Example",
        start_date=date(2027, 1, 15),
        estimated=True,
    )
    opportunity = Opportunity(
        id="example-university-example-program",
        track="masters",
        title="Example Program",
        description="Example description",
        url="https://example.org",
        category="Masters",
        tags=["AI"],
        milestones=[deadline],
    )

    assert opportunity.milestones == [deadline]
    assert opportunity.milestones[0].estimated is True

    event = create_calendar_events([opportunity])[0]
    assert event.id == "example-university-example-program.application-deadline"
    assert event.start_date == date(2027, 1, 15)
