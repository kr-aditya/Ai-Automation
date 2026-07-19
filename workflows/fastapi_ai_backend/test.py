import requests

url = "http://localhost:5678/webhook-test/ai-chat"

data = {
    "message": "explain FASTAPI",
    "user": "Aditya"
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.json())