from src.utils.date_helpers import clean_text, is_blank, split_tags
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

@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, True),
        ("", True),
        ("   ", True),
        ("Opportunity Tracker", False),
        (0, False),
    ],
)
def test_is_blank_classifies_values(value, expected):
    result = is_blank(value)

    assert result is expected

def test_split_tags_accepts_mixed_separators():
    value = "AI,ML;Python/Data Science|Research"

    result = split_tags(value)

    assert result == ["AI", "ML", "Python", "Data Science", "Research"]

def test_split_tags_discards_empty_parts():
    value = ",  AI  ;; |  ML  , / "

    result = split_tags(value)

    assert result == ["AI", "ML"]