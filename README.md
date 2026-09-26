# Railway Delay API

An HTTP API that parses railway delay notices into structured JSON.

The API uses [x402](https://www.x402.org/) to charge for paid endpoints using testnet USDC on Base Sepolia.

## Features

- Parse a single railway delay notice.
- Parse multiple delay notices in one request.
- Extract:
  - train number
  - station
  - expected arrival time
  - delay reason
- Free health endpoint.
- Two paid API routes with different prices.
- x402 payment flow using testnet USDC.
- Buyer script demonstrating automatic payment.
- Sample valid and deliberately broken notices.
- Automated tests for the parser and API.

## API

### Free endpoint

```http
GET /health
```

Returns:

```json
{
  "status": "ok"
}
```

### Paid endpoint: single notice

`POST /v1/parse`

**Price:** 0.001 USDC

Example request:

```json
{
  "notice": "Train 12123 is delayed at PUNE. Expected arrival 14:30 due to signal failure."
}
```

Example response:
```json
{
  "train": "12123",
  "station": "PUNE",
  "expected_time": "14:30",
  "reason": "signal failure"
}
```

Without a valid x402 payment, the endpoint returns:

```text
HTTP/1.1 402 Payment Required
```

The response contains the x402 payment requirements needed by a compatible buyer.

## Paid endpoint: bulk notices

`POST /v1/parse/bulk`

**Price:** 0.003 USDC

### Example request

```json
{
  "notices": [
    "Train 12123 is delayed at PUNE. Expected arrival 14:30 due to signal failure.",
    "Train 12951 is delayed at NDLS. Expected arrival 16:45 due to technical issue."
  ]
}
```

Example response: 
```json
[
  {
    "train": "12123",
    "station": "PUNE",
    "expected_time": "14:30",
    "reason": "signal failure"
  },
  {
    "train": "12951",
    "station": "NDLS",
    "expected_time": "16:45",
    "reason": "technical issue"
  }
]
```

## Payment configuration

The paid endpoints use:

| Property | Value |
|---|---|
| Scheme | `exact` |
| Network | Base Sepolia |
| Asset | Testnet USDC |
| Single parse | 0.001 USDC |
| Bulk parse | 0.003 USDC |

The server uses an x402 facilitator to verify and settle payments.

The payment recipient and prices are configured on the server and are not controlled by the buyer.

## Requirements

- Python 3.14+
- `uv`
- An EVM wallet for signing testnet payments
- Testnet USDC on Base Sepolia
- Access to the configured x402 facilitator

## Installation

Clone the repository and enter the project directory:

```powershell
cd railway-delay-api
```

Install dependencies:
```powershell
uv sync
```

## Environment variables

Create a `.env` file in the project root.

The buyer requires:

```env
BUYER_PRIVATE_KEY=0xYOUR_TESTNET_PRIVATE_KEY
API_URL=http://localhost:8000
```

The server payment configuration is loaded separately through the project's payment configuration.

Never commit .env or a real private key.

Use a dedicated testnet wallet. Never use a wallet containing production funds.

The repository includes .env.example containing placeholders only.

## Start the API

Run:

```powershell
uv run uvicorn app.main:app --reload
```

The API will be available at:
```text
http://loclahost:8000
```

## Check the free endpoint

Run:

```powershell
curl.exe http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok"
}
```

## Test a paid endpoint manually

Calling the paid endpoint without payment:
```powershell
curl.exe -i -X POST http://localhost:8000/v1/parse `
  -H "Content-Type: application/json" `
  -d '{"notice":"Train 12123 is delayed at PUNE. Expected arrival 14:30 due to signal failure."}'
```

The server should respond with:
```text
HTTP/1.1 402 Payment Required
```

The response contains the x402 payment requirements needed by a compatible buyer.

## Run the buyer

With the API running in another terminal:

```powershell
uv run python buyer\buyer.py
```

The buyer performs the complete x402 flow:

1. Sends the initial API request.
2. Receives 402 Payment Required.
3. Reads the payment requirements.
4. Creates an x402 payment payload.
5. Signs the EVM payment with the buyer wallet.
6. Adds the payment signature to the request.
7. Retries the API request.
8. Receives the paid response.

Example output:
```text
Buyer: 0x...

--- Single parse ---
Initial response: HTTP 402
Paid response: HTTP 200
{"train":"12123","station":"PUNE","expected_time":"14:30","reason":"signal failure"}

--- Bulk parse ---
Initial response: HTTP 402
Paid response: HTTP 200
[{"train":"12123","station":"PUNE","expected_time":"14:30","reason":"signal failure"},{"train":"12951","station":"NDLS","expected_time":"16:45","reason":"technical issue"}]
```

## Tests

Run the test suite:

```powershell
uv run pytest
```

The automated tests cover parser behavior and API behavior without making real blockchain payments.

The buyer script provides the end-to-end x402 payment test against the running API.

## Sample notices

Sample input files are provided under:

```text
samples/
├── valid/
└── broken/
```

### Valid notices

The `valid` directory contains notices that should parse successfully.

### Broken notices

The `broken` directory contains deliberately malformed notices, including:

- Missing train number
- Missing station
- Missing expected time
- Unrelated text
- Empty input

These examples demonstrate how the parser handles malformed input.

## Project structure

```text
railway-delay-api/
│
├── app/
│   ├── api/
│   │   ├── health.py
│   │   └── parse.py
│   │
│   ├── parser/
│   │   ├── normalizer.py
│   │   ├── parser.py
│   │   └── patterns.py
│   │
│   ├── payments/
│   │   ├── config.py
│   │   └── x402.py
│   │
│   ├── schemas/
│   │   └── delay.py
│   │
│   └── main.py
│
├── buyer/
│   └── buyer.py
│
├── samples/
│   ├── valid/
│   └── broken/
│
├── tests/
│   ├── test_api.py
│   └── test_parser.py
│
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## x402 architecture

The server registers the exact EVM payment scheme for Base Sepolia and applies x402 payment middleware to the paid routes.

```text
                  Client
                    |
                    | POST /v1/parse
                    v
              FastAPI application
                    |
                    v
              x402 middleware
                    |
              No payment?
                    |
                    v
             402 Payment Required
                    |
                    | payment requirements
                    v
              Buyer / x402 client
                    |
                    | signed payment
                    v
              x402 middleware
                    |
              verify + settle
                    |
                    v
              Parse endpoint
                    |
                    v
              Structured JSON
```

The free `/health` endpoint is not included in the x402 payment routes.

## Security

Private keys are loaded from environment variables.

Real secrets must never be committed to Git.

`.env` is ignored by Git.

`.env.example` contains placeholders only.

The buyer wallet should contain testnet assets only.

Payment prices and the recipient are configured by the server.

Client-supplied fields cannot override the server's payment configuration.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
