import json
from urllib.parse import parse_qsl


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_fake_init_data_structure():
    from tests.conftest import make_fake_init_data

    init_data = make_fake_init_data(user_id=42, first_name="Test")
    params = dict(parse_qsl(init_data))
    assert "hash" in params
    assert "user" in params
    assert "auth_date" in params
    user = json.loads(params["user"])
    assert user["id"] == 42
