from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.communication.whatsapp.api import router


app = FastAPI()
app.include_router(router)

client = TestClient(app)


verification = client.get(
    "/webhooks/whatsapp",
    params={
        "hub.mode": "subscribe",
        "hub.verify_token": "ai-employee-os-hafiz-dev",
        "hub.challenge": "123456789",
    },
)

print("Verification status:", verification.status_code)
print("Challenge:", verification.text)


payload = {
    "entry": [
        {
            "changes": [
                {
                    "value": {
                        "messages": [
                            {
                                "from": "923001234567",
                                "type": "text",
                                "text": {
                                    "body": "I need my invoice"
                                },
                            }
                        ]
                    }
                }
            ]
        }
    ]
}

response = client.post(
    "/webhooks/whatsapp",
    json=payload,
)

print("Message status:", response.status_code)
print("Response:", response.json())