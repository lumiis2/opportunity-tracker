from datetime import date

import pytest

from src.core import Milestone, Opportunity, validate_opportunities


def test_validation_accepts_empty_collection():
    validate_opportunities([])


def test_validation_accepts_opportunity_without_milestones():
    item = Opportunity("masters-example", "masters", "Example", "Description")

    validate_opportunities([item])


@pytest.mark.parametrize(
    ("item_id", "track", "title"),
    [
        ("", "masters", "Example"),
        ("masters-example", "", "Example"),
        ("masters-example", "masters", ""),
    ],
)
def test_validation_rejects_missing_opportunity_fields(item_id, track, title):
    item = Opportunity(item_id, track, title, "Description")

    with pytest.raises(ValueError, match="Opportunity has missing required fields"):
        validate_opportunities([item])


@pytest.mark.parametrize(
    ("kind", "title"),
    [
        ("", "Deadline"),
        ("application-deadline", ""),
    ],
)
def test_validation_rejects_missing_milestone_fields(kind, title):
    item = Opportunity(
        "masters-example",
        "masters",
        "Example",
        "Description",
        milestones=[Milestone(kind, title, date(2027, 1, 15))],
    )

    with pytest.raises(ValueError, match="milestone with missing required fields"):
        validate_opportunities([item])


def test_validation_rejects_end_date_equal_to_start_date():
    item = Opportunity(
        "masters-example",
        "masters",
        "Example",
        "Description",
        milestones=[
            Milestone(
                "program-period",
                "Program",
                date(2027, 2, 1),
                date(2027, 2, 1),
            ),
        ],
    )

    with pytest.raises(ValueError, match="invalid date range"):
        validate_opportunities([item])


def test_validation_accepts_deadline_on_opening_date():
    item = Opportunity(
        "masters-example",
        "masters",
        "Example",
        "Description",
        milestones=[
            Milestone("application-open", "Open", date(2027, 2, 1)),
            Milestone("application-deadline", "Deadline", date(2027, 2, 1)),
        ],
    )

    validate_opportunities([item])


@pytest.mark.parametrize(
    ("opening_estimated", "deadline_estimated"),
    [(True, False), (False, True)],
)
def test_validation_accepts_earlier_deadline_when_a_date_is_estimated(
    opening_estimated, deadline_estimated
):
    item = Opportunity(
        "masters-example",
        "masters",
        "Example",
        "Description",
        milestones=[
            Milestone(
                "application-open",
                "Open",
                date(2027, 2, 1),
                estimated=opening_estimated,
            ),
            Milestone(
                "application-deadline",
                "Deadline",
                date(2027, 1, 1),
                estimated=deadline_estimated,
            ),
        ],
    )

    validate_opportunities([item])


def test_validation_allows_same_milestone_kind_in_different_opportunities():
    first = Opportunity(
        "masters-first",
        "masters",
        "First",
        "First program",
        milestones=[
            Milestone("application-deadline", "Deadline", date(2027, 2, 1)),
        ],
    )
    second = Opportunity(
        "masters-second",
        "masters",
        "Second",
        "Second program",
        milestones=[
            Milestone("application-deadline", "Deadline", date(2027, 2, 1)),
        ],
    )

    validate_opportunities([first, second])


def test_validation_reports_errors_from_multiple_opportunities():
    first = Opportunity("masters-first", "masters", "", "Description")
    second = Opportunity(
        "masters-second",
        "masters",
        "Second",
        "Description",
        milestones=[
            Milestone("application-deadline", "", date(2027, 2, 1)),
        ],
    )

    with pytest.raises(ValueError) as error:
        validate_opportunities([first, second])

    message = str(error.value)
    assert "Opportunity has missing required fields: masters-first" in message
    assert "masters-second has a milestone with missing required fields" in message


def test_validation_reports_multiple_errors_from_one_opportunity():
    item = Opportunity(
        "masters-example",
        "masters",
        "Example",
        "Description",
        milestones=[
            Milestone(
                "program-period",
                "First period",
                date(2027, 2, 1),
                date(2027, 1, 1),
            ),
            Milestone(
                "program-period",
                "Second period",
                date(2027, 3, 1),
                date(2027, 4, 1),
            ),
        ],
    )

    with pytest.raises(ValueError) as error:
        validate_opportunities([item])

    message = str(error.value)
    assert "masters-example has duplicate milestones: program-period" in message
    assert "masters-example.program-period has an invalid date range" in message