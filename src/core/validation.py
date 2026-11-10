"""Validation rules for normalized opportunities."""

from collections import Counter

from src.core.opportunity import Opportunity


def validate_opportunities(opportunities: list[Opportunity]) -> None:
    """Raise a single error containing every invalid opportunity found."""

    errors: list[str] = []
    duplicate_ids = sorted(
        item_id
        for item_id, count in Counter(item.id for item in opportunities).items()
        if count > 1
    )
    if duplicate_ids:
        errors.append(f"Duplicate opportunity IDs: {', '.join(duplicate_ids)}")

    for opportunity in opportunities:
        if not opportunity.id or not opportunity.track or not opportunity.title:
            errors.append(f"Opportunity has missing required fields: {opportunity.id or '<unknown>'}")

        duplicate_kinds = sorted(
            kind
            for kind, count in Counter(item.kind for item in opportunity.milestones).items()
            if count > 1
        )
        if duplicate_kinds:
            errors.append(
                f"{opportunity.id} has duplicate milestones: {', '.join(duplicate_kinds)}"
            )

        for milestone in opportunity.milestones:
            if not milestone.kind or not milestone.title:
                errors.append(f"{opportunity.id} has a milestone with missing required fields")
            if milestone.end_date and milestone.end_date <= milestone.start_date:
                errors.append(f"{opportunity.id}.{milestone.kind} has an invalid date range")

        milestones = {item.kind: item for item in opportunity.milestones}
        opening = milestones.get("application-open")
        deadline = milestones.get("application-deadline")
        if (
            opening
            and deadline
            and not opening.estimated
            and not deadline.estimated
            and deadline.start_date < opening.start_date
        ):
            errors.append(f"{opportunity.id} has a deadline before applications open")

    if errors:
        raise ValueError("Invalid opportunities:\n- " + "\n- ".join(errors))
