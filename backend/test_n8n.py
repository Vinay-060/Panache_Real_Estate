import requests

data = {
    "name": "Vinay",
    "country": "India",
    "budget": 50000000,
    "funding": "Cash",
    "timeline": 2,
    "purpose": "Investment",
    "grade": "A"
}

url = "https://vinay-060.app.n8n.cloud/webhook-test/panache-lead"

r = requests.post(
    url,
    json=data
)

print(r.status_code)
print(r.text)