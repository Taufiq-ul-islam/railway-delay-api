from fastapi import APIRouter, HTTPException

from app.parser.parser import ParseError, parse_notice
from app.schemas.delay import BulkParseRequest, DelayNotice, ParseRequest

router = APIRouter(prefix="/v1", tags=["parser"])


@router.post("/parse", response_model=DelayNotice)
async def parse_delay_notice(request: ParseRequest):
    try:
        return parse_notice(request.notice)
    except ParseError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "INVALID_NOTICE",
                "message": str(exc),
            },
        )


@router.post("/parse/bulk", response_model=list[DelayNotice])
async def parse_bulk_delay_notices(request: BulkParseRequest):
    results = []

    for notice in request.notices:
        try:
            results.append(parse_notice(notice))
        except ParseError as exc:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "INVALID_NOTICE",
                    "message": str(exc),
                },
            )

    return results
