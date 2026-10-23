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

# Udtræk listen under 'data' nøglen (eller gem hele responset hvis det allerede var en liste)
data = inv_response.json()
inventory_list = data.get("data", data) if isinstance(data, dict) else data

with open(FILE_PATH, "w", encoding="utf-8") as f:
    json.dump(inventory_list, f, indent=2)

print("Inventory saved locally as a direct array successfully!")
