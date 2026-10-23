import base64
import json
import os
import requests

# --- CONFIGURATION ---
MERINOS_URL = "https://api.merinos-eu.de:5050/api/v2"
CERT = "server.crt"
EMAIL = os.environ.get("MERINOS_EMAIL")
PASSWORD = os.environ.get("MERINOS_PASSWORD")

# GitHub details
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# Henter automatisk "brugernavn/repository" fra GitHub Actions miljøet
REPO_NAME = os.environ.get("GITHUB_REPOSITORY", "emretaspinar/LHMerinos")
FILE_PATH = "inventory.json"
BRANCH = "main"

print(f"Target Repository: {REPO_NAME}")

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
file_content_str = json.dumps(inventory_data, indent=2)

# 3. Push/Update the file on GitHub automatically via API
print("Pushing updated inventory to GitHub...")
api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

# Check if the file already exists to get its SHA (required by GitHub API for updates)
get_res = requests.get(api_url, headers=headers)
sha = None
if get_res.status_code == 200:
  sha = get_res.json().get("sha")

# Prepare payload
encoded_content = base64.b64encode(file_content_str.encode("utf-8")).decode(
    "utf-8"
)
payload = {
    "message": "Daily automated inventory sync from Merinos",
    "content": encoded_content,
    "branch": BRANCH,
}
if sha:
  payload["sha"] = sha

put_res = requests.put(api_url, headers=headers, json=payload)

if put_res.status_code in [200, 201]:
  print("Successfully updated inventory.json on GitHub!")
else:
  raise SystemExit(f"Failed to push to GitHub: {put_res.text}")
