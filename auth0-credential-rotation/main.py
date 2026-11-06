import os
import requests
from dotenv import load_dotenv
import time
from datetime import datetime, timezone

load_dotenv()

auth0_domain = os.getenv("AUTH0_DOMAIN")
client_id = os.getenv("AUTH0_CLIENT_ID")
client_secret = os.getenv("AUTH0_CLIENT_SECRET")
audience = os.getenv("AUTH0_AUDIENCE")

def get_token():
    url = f"https://{auth0_domain}/oauth/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": audience,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, json=payload)

    # print("Status Code:", response.status_code)
    # print("Auth0 Response:", response.text)

    response.raise_for_status()

    # delete this line after debugging
    # data = response.json()
    # print("Token lifetime:", data.get("expires_in"), "seconds")

    return response.json()["access_token"]

def call_chat_endpoint(token):
    url = "http://127.0.0.1:8000/chat"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, headers=headers)

    print_timestamp("Calling chat endpoint...")
    print("Chat API Status:", response.status_code)
    print("Chat API Response:", response.text)

def print_timestamp(message):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{timestamp}] {message}")


if __name__ == "__main__":
    token = get_token()
    call_chat_endpoint(token)

    time.sleep(60)

    call_chat_endpoint(token)