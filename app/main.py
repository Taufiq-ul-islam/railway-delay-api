from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.parse import router as parse_router
from app.payments.x402 import add_x402_middleware


def create_app(enable_payments: bool = True) -> FastAPI:
    app = FastAPI(
        title="Railway Delay API",
        description="x402-powered railway delay notice parser",
        version="0.1.0",
    )

    app.include_router(health_router)
    app.include_router(parse_router)

    if enable_payments:
        add_x402_middleware(app)

    return app


app = create_app()
