import pytest

from app.parser.parser import ParseError, parse_notice


def test_parse_valid_notice():
    notice = (
        "Train 12123 is delayed at PUNE. "
        "Expected arrival 14:30 due to signal failure."
    )

    result = parse_notice(notice)

    assert result.train == "12123"
    assert result.station == "PUNE"
    assert result.expected_time == "14:30"
    assert result.reason == "signal failure"


def test_parse_without_reason():
    notice = (
        "Train 12123 is delayed at PUNE. "
        "Expected arrival 14:30."
    )

    result = parse_notice(notice)

    assert result.train == "12123"
    assert result.station == "PUNE"
    assert result.expected_time == "14:30"
    assert result.reason is None


def test_rejects_garbage():
    with pytest.raises(ParseError):
        parse_notice("asdf banana railway lol")


def test_rejects_missing_train():
    notice = (
        "Train is delayed at PUNE. "
        "Expected arrival 14:30 due to signal failure."
    )

    with pytest.raises(ParseError):
        parse_notice(notice)


def test_rejects_missing_station():
    notice = (
        "Train 12123 is delayed. "
        "Expected arrival 14:30 due to signal failure."
    )

    with pytest.raises(ParseError):
        parse_notice(notice)


def test_rejects_missing_time():
    notice = (
        "Train 12123 is delayed at PUNE "
        "due to signal failure."
    )

    with pytest.raises(ParseError):
        parse_notice(notice)
