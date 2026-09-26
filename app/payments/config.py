import os

from dotenv import load_dotenv

load_dotenv()


PAY_TO = os.environ["PAY_TO"]
FACILITATOR_URL = os.getenv("FACILITATOR_URL", "https://x402.org/facilitator")

NETWORK = os.getenv("X402_NETWORK", "eip155:84532")

PARSE_PRICE = os.getenv("PARSE_PRICE", "$0.001")

BULK_PRICE = os.getenv("BULK_PRICE", "$0.003")
