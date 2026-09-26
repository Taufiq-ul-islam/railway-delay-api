from app.parser.normalizer import normalize
from app.parser.patterns import (
    REASON_PATTERN,
    STATION_PATTERN,
    TIME_PATTERN,
    TRAIN_PATTERN,
)
from app.schemas.delay import DelayNotice


class ParseError(Exception):
    """Raised when a railway notice cannot be parsed."""


def parse_notice(text: str) -> DelayNotice:
    text = normalize(text)

    train_match = TRAIN_PATTERN.search(text)
    station_match = STATION_PATTERN.search(text)
    time_match = TIME_PATTERN.search(text)
    reason_match = REASON_PATTERN.search(text)

    if not train_match:
        raise ParseError("Could not identify train number")

    if not station_match:
        raise ParseError("Could not identify station")

    if not time_match:
        raise ParseError("Could not identify expected arrival time")

    return DelayNotice(
        train=train_match.group(1),
        station=station_match.group(1).upper(),
        expected_time=time_match.group(0),
        reason=reason_match.group(1).strip() if reason_match else None,
    )
