from src.utils.date_helpers import clean_text
import pytest

def test_clean_text_removes_surrounding_whitespace():
    value = "  Opportunity Tracker  "

    result = clean_text(value)

    assert result == "Opportunity Tracker"

@pytest.mark.parametrize("value", [None, "", "   ", "nan", "None"])
def test_clean_text_normalizes_null_like_values(value):
    result = clean_text(value)

    assert result == ""

def test_clean_text_preserves_numeric_zero():
    value = 0

    result = clean_text(value)

    assert result == "0"