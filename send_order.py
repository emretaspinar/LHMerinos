import os
import requests
import json

# Læs GitHub event payload
event_path = os.getenv('GITHUB_EVENT_PATH')
if event_path and os.path.exists(event_path):
    with open(event_path, 'r') as f:
        event_data = json.load(f)
    order_payload = event_data.get('client_payload', {})
else:
    order_payload = {}

# SIKKERHEDSVALIDERING (Nødbremse): Blokér ordren øjeblikkeligt, hvis en vare mangler SKU eller er 0
orders = order_payload.get("data", {}).get("orders", [])
items_list = order_payload.get("items", [])

all_items = []
for order in orders:
    all_items.extend(order.get("lineItems", []))
if items_list:
    all_items.extend(items_list)

for item in all_items:
    item_id = item.get("itemCode") or item.get("item_id")
    if not item_id or item_id == 0 or item_id == "0":
        print(f"KRITISK FEJL: Ugyldig eller manglende SKU/item_id opdaget ({item_id}). Ordren afvises for at undgå fejl.")
        exit(1)

# Hent token (tilpas afhængigt af dit miljø)
token = os.getenv('MEDIPA_TOKEN')

# Send ordren til Medipa API
order_url = "https://api.merinos-eu.de:5050/api/v2/orders"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("Sender ordre til Medipa...")
verify_target = "server.crt" if os.path.exists("server.crt") else True
order_res = requests.post(order_url, json=order_payload, headers=headers, verify=verify_target)

print(f"Svar fra Medipa (Status {order_res.status_code}): {order_res.text}")

try:
    res_json = order_res.json()
except Exception:
    res_json = {}

# Godkend ordren hvis HTTP-status er 200, og Medipa returnerer success=true eller result=1
is_success = order_res.status_code == 200 and (
    res_json.get("success") is True or 
    res_json.get("data", {}).get("result") == 1
)

if not is_success:
    print("Fejl: Ordren blev ikke godkendt af Medipa.")
    exit(1)
else:
    print("Succes! Ordren er oprettet hos Medipa.")
