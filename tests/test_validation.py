from datetime import date

import pytest

from src.core import Milestone, Opportunity, validate_opportunities


def opportunity(item_id: str = "example") -> Opportunity:
    return Opportunity(item_id, "graduation", "Example", "Description")


def test_valid_opportunity_passes():
    item = opportunity()
    item.milestones.append(Milestone("application-deadline", "Deadline", date(2027, 1, 1)))

    validate_opportunities([item])


def test_duplicate_opportunity_ids_are_rejected():
    with pytest.raises(ValueError, match="Duplicate opportunity IDs: example"):
        validate_opportunities([opportunity(), opportunity()])


def test_duplicate_milestones_are_rejected():
    item = opportunity()
    item.milestones = [
        Milestone("application-open", "Open", date(2027, 1, 1)),
        Milestone("application-open", "Open again", date(2027, 2, 1)),
    ]

    with pytest.raises(ValueError, match="duplicate milestones: application-open"):
        validate_opportunities([item])


def test_invalid_date_range_is_rejected():
    item = opportunity()
    item.milestones = [
        Milestone("program-period", "Program", date(2027, 2, 1), date(2027, 1, 1))
    ]

    with pytest.raises(ValueError, match="invalid date range"):
        validate_opportunities([item])


def test_confirmed_deadline_before_opening_is_rejected():
    item = opportunity()
    item.milestones = [
        Milestone("application-open", "Open", date(2027, 2, 1)),
        Milestone("application-deadline", "Deadline", date(2027, 1, 1)),
    ]

    with pytest.raises(ValueError, match="deadline before applications open"):
        validate_opportunities([item])
