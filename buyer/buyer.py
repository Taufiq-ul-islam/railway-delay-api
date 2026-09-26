import asyncio
import os

import httpx
from dotenv import load_dotenv
from eth_account import Account

from x402 import x402Client
from x402.http import x402HTTPClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact import register_exact_evm_client


load_dotenv()


API_URL = os.getenv("API_URL", "http://localhost:8000")

SINGLE_NOTICE = (
    "Train 12123 is delayed at PUNE. "
    "Expected arrival 14:30 due to signal failure."
)

BULK_NOTICES = [
    (
        "Train 12123 is delayed at PUNE. "
        "Expected arrival 14:30 due to signal failure."
    ),
    (
        "Train 12951 is delayed at NDLS. "
        "Expected arrival 16:45 due to technical issue."
    ),
]


def create_x402_client() -> x402HTTPClient:
    private_key = os.environ["BUYER_PRIVATE_KEY"]
    account = Account.from_key(private_key)

    print(f"Buyer: {account.address}")

    client = x402Client()

    register_exact_evm_client(
        client,
        EthAccountSigner(account),
    )

    return x402HTTPClient(client)


async def paid_post(
    http: httpx.AsyncClient,
    x402_http: x402HTTPClient,
    url: str,
    payload: dict,
) -> httpx.Response:
    # First request: expect 402.
    response = await http.post(url, json=payload)

    print(f"Initial response: HTTP {response.status_code}")

    if response.status_code != 402:
        return response

    # Decode the server's payment requirements.
    payment_required = x402_http.get_payment_required_response(
        response.headers.get,
        response.json(),
    )

    # Create and sign the payment payload.
    payment_payload = await x402_http._client.create_payment_payload(
        payment_required,
    )

    # Turn the signed payload into the x402 HTTP header.
    payment_headers = x402_http.encode_payment_signature_header(
        payment_payload,
    )

    # Retry with payment.
    return await http.post(
        url,
        json=payload,
        headers=payment_headers,
    )


async def main() -> None:
    x402_http = create_x402_client()

    async with httpx.AsyncClient() as http:
        print("\n--- Single parse ---")

        response = await paid_post(
            http,
            x402_http,
            f"{API_URL}/v1/parse",
            {"notice": SINGLE_NOTICE},
        )

        print(f"Paid response: HTTP {response.status_code}")
        print(response.text)

        print("\n--- Bulk parse ---")

        response = await paid_post(
            http,
            x402_http,
            f"{API_URL}/v1/parse/bulk",
            {"notices": BULK_NOTICES},
        )

        print(f"Paid response: HTTP {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
