from pydantic import BaseModel, Field


class ParseRequest(BaseModel):
    notice: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Raw railway delay notice",
    )


class DelayNotice(BaseModel):
    train: str
    station: str
    expected_time: str
    reason: str | None = None

class BulkParseRequest(BaseModel):
    notices: list[str] = Field(
        ...,
        min_length=1,
        max_length=20,
    )
