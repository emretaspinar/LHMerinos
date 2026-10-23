import csv
import os
import requests

MERINOS_URL = "https://api.merinos-eu.de:5050/api/v2"
CERT = "server.crt"
EMAIL = os.environ.get("MERINOS_EMAIL")
PASSWORD = os.environ.get("MERINOS_PASSWORD")
FILE_PATH = "inventory.csv"

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

# Gem direkte som CSV-fil med overskrifterne 'item' og 'available'
with open(FILE_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["item", "available"])
    for item in items:
        writer.writerow([str(item.get("item", "")).strip(), int(item.get("available", 0))])

print("Inventory saved to inventory.csv successfully!")
