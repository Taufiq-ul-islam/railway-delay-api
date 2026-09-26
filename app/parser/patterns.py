import re

TRAIN_PATTERN = re.compile(r"\b(?:train\s*)?(\d{4,6})\b", re.IGNORECASE)

TIME_PATTERN = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")

STATION_PATTERN = re.compile(r"\bat\s+([A-Z][A-Z0-9]{2,5})\b", re.IGNORECASE)

REASON_PATTERN = re.compile(r"\bdue to\s+(.+?)(?:[.!?]|$)", re.IGNORECASE)
