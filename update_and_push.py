import json
import os
import requests

# --- CONFIGURATION ---
MERINOS_URL = "https://api.merinos-eu.de:5050/api/v2"
CERT = "server.crt"
EMAIL = os.environ.get("MERINOS_EMAIL")
PASSWORD = os.environ.get("MERINOS_PASSWORD")
FILE_PATH = "inventory.json"

# 1. Log into Merinos API
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
if not token:
  raise SystemExit("No accessToken found in login response.")

# 2. Fetch Inventory Data
print("Fetching inventory...")
inv_response = requests.get(
    f"{MERINOS_URL}/local-data/inventory",
    headers={"Authorization": f"Bearer {token}"},
    verify=CERT,
    timeout=30,
)

if inv_response.status_code != 200:
  raise SystemExit(f"Failed to fetch inventory: {inv_response.text}")

inventory_data = inv_response.json()

# 3. Save locally to inventory.json
print(f"Saving inventory data to {FILE_PATH}...")
with open(FILE_PATH, "w", encoding="utf-8") as f:
  json.dump(inventory_data, f, indent=2)

print("Inventory successfully fetched and saved locally!")
