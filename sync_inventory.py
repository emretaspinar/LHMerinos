import json
import os
import requests

MERINOS_URL = "https://api.merinos-eu.de:5050/api/v2"
CERT = "server.crt"
EMAIL = os.environ.get("MERINOS_EMAIL")
PASSWORD = os.environ.get("MERINOS_PASSWORD")
FILE_PATH = "inventory.json"

print("Logging into Merinos API...")
auth_response = requests.post(
    f"{MERINOS_URL}/auth/login",
    json={"email": EMAIL, "password": PASSWORD},
    verify=CERT,
    timeout=30,
)
if auth_response.status_code != 200:
    raise SystemExit(f"Login failed: {auth_response.text}")

token = auth_response.json().get("accessToken")

print("Fetching inventory...")
inv_response = requests.get(
    f"{MERINOS_URL}/local-data/inventory",
    headers={"Authorization": f"Bearer {token}"},
    verify=CERT,
    timeout=30,
)
if inv_response.status_code != 200:
    raise SystemExit(f"Failed to fetch inventory: {inv_response.text}")

raw_data = inv_response.json()
items = raw_data.get("data", raw_data) if isinstance(raw_data, dict) else raw_data

# Slanker filstørrelsen markant ved kun at gemme de felter SyncX skal bruge
clean_items = []
for item in items:
    clean_items.append({
        "item": str(item.get("item", "")).strip(),
        "available": int(item.get("available", 0))
    })

# Gemmer i det strukturerede format SyncX forventer
with open(FILE_PATH, "w", encoding="utf-8") as f:
    json.dump({"data": clean_items}, f, indent=2)

print("Inventory optimized and saved successfully!")
