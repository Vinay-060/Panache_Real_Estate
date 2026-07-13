import requests


def send_to_n8n(data):

    response = requests.post(

        "https://vinay-060.app.n8n.cloud/webhook-test/panache-lead",

        json=data,
        timeout=10
    )
    print(response.status_code)
    print(response.text)