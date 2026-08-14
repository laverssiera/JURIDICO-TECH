import requests
import os

LICEU_URL = os.getenv("LICEU_MAE_URL", "http://localhost:9000")

def send_to_mae(endpoint, payload):
    response = requests.post(
        f"{LICEU_URL}{endpoint}",
        json=payload,
        timeout=5
    )
    return response.json()
