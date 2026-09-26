from x402.http import (
    FacilitatorConfig,
    HTTPFacilitatorClient,
    PaymentOption,
)
from x402.http.middleware.fastapi import PaymentMiddlewareASGI
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.server import x402ResourceServer

from app.payments.config import (
    BULK_PRICE, FACILITATOR_URL, NETWORK, PARSE_PRICE, PAY_TO,
)


def create_x402_server():
    facilitator = HTTPFacilitatorClient(FacilitatorConfig(url=FACILITATOR_URL))

    server = x402ResourceServer(facilitator)

    server.register(NETWORK, ExactEvmServerScheme())

    return server


def create_x402_routes():
    return {
        "POST /v1/parse": RouteConfig(
            accepts=[
                PaymentOption(
                    scheme="exact",
                    pay_to=PAY_TO,
                    price=PARSE_PRICE,
                    network=NETWORK,
                )
            ],
            mime_type="application/json",
            description="Parse a single railway delay notice",
        ),
        "POST /v1/parse/bulk": RouteConfig(
            accepts=[
                PaymentOption(
                    scheme="exact",
                    pay_to=PAY_TO,
                    price=BULK_PRICE,
                    network=NETWORK,
                )
            ],
            mime_type="application/json",
            description="Parse multiple railway delay notices",
        ),
    }


def add_x402_middleware(app):
    server = create_x402_server()
    routes = create_x402_routes()

    app.add_middleware(
        PaymentMiddlewareASGI,
        routes=routes,
        server=server,
    )
