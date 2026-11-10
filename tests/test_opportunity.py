from datetime import date

from src.core import Milestone, Opportunity


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
