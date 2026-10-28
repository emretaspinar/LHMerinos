import os
import requests
import json

# Hent ordre-data fra GitHub repository_dispatch payload
event_path = os.getenv('GITHUB_EVENT_PATH')
order_payload = {}
if event_path and os.path.exists(event_path):
    with open(event_path, 'r') as f:
        event_data = json.load(f)
    order_payload = event_data.get('client_payload', {})

# 1. Login og hent frisk access token fra Medipa
login_url = "https://api.merinos-eu.de:5050/api/v2/auth/login"
credentials = {
    "email": os.getenv("MERINOS_EMAIL"),
    "password": os.getenv("MERINOS_PASSWORD")
}

print("Logger ind på Medipa API...")
auth_res = requests.post(login_url, json=credentials, verify="server.crt")

if auth_res.status_code != 200:
    print(f"Login fejlede: {auth_res.text}")
    exit(1)

token = auth_res.json().get("accessToken")

# 2. Send ordren til saveOrder endpointet
order_url = "https://api.merinos-eu.de:5050/api/v2/saveOrder"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("Sender ordre til Medipa...")
order_res = requests.post(order_url, json=order_payload, headers=headers, verify="server.crt")

print(f"Svar fra Medipa (Status {order_res.status_code}): {order_res.text}")

if order_res.status_code != 200 or order_res.json().get("result") != 1:
    exit(1)
