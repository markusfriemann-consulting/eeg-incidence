"""Smoke test for netztransparenz.de OAuth credentials."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["NETZTRANSPARENZ_CLIENT_ID"]
CLIENT_SECRET = os.environ["NETZTRANSPARENZ_CLIENT_SECRET"]

TOKEN_URL = "https://identity.netztransparenz.de/users/connect/token"
API_BASE = "https://ds.netztransparenz.de/api/v1"


def get_access_token() -> str:
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def main() -> None:
    token = get_access_token()
    print(f"Token acquired (length: {len(token)} chars, first 20: {token[:20]}...)")

    # Hit the API health endpoint
    health = requests.get(f"{API_BASE}/health", headers={"Authorization": f"Bearer {token}"}, timeout=30)
    print(f"Health check status: {health.status_code}")
    print(f"Response: {health.text[:200]}")


if __name__ == "__main__":
    main()