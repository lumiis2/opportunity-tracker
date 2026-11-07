from src.utils.date_helpers import clean_text


def test_clean_text_removes_surrounding_whitespace():
    value = "  Opportunity Tracker  "

    result = clean_text(value)

    assert result == "Opportunity Tracker"