import requests

# Your GCC High (powerbigov.us) API base URL
BASE = "https://api.powerbigov.us/v1.0/myorg"

# Replace these with values from your report URL:
GROUP_ID = "57ba19a1-f62c-40d5-a043-67dbd430e612"
REPORT_ID = "87fc2fbd-cd9c-4b79-8641-0faf650413bd"

endpoint = f"{BASE}/groups/{GROUP_ID}/reports/{REPORT_ID}"

print("Testing:", endpoint)

response = requests.get(endpoint)

print("Status:", response.status_code)
print("Body:", response.text[:500])