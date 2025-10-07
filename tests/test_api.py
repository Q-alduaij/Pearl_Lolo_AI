from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_invoke_chat_path_exists() -> None:
    payload = {
        "intent": "chat",
        "messages": [{"role": "user", "content": "Hello"}],
        "params": {},
        "attachments": [],
        "locale": "en-GB",
        "tz": "Asia/Kuwait",
        "user_tags": [],
    }
    response = client.post("/invoke", json=payload)
    assert response.status_code == 200
