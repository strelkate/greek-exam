async def test_session_creates_new_user(client, init_data):
    response = await client.post(
        "/api/v1/auth/session",
        headers={"X-Telegram-Init-Data": init_data},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == 123456789
    assert data["is_new_user"] is True
    assert data["placement_status"] == "pending"
    assert data["streak_days"] == 0
    assert data["total_xp"] == 0
    assert data["show_instruction_translation"] is True
    assert isinstance(data["user_id"], int) and data["user_id"] > 0
    assert data["a1_skipped"] is False


async def test_session_returns_existing_user(client, init_data):
    await client.post("/api/v1/auth/session", headers={"X-Telegram-Init-Data": init_data})
    response = await client.post("/api/v1/auth/session", headers={"X-Telegram-Init-Data": init_data})
    assert response.status_code == 200
    assert response.json()["is_new_user"] is False


async def test_session_invalid_init_data(client):
    import time
    from urllib.parse import urlencode
    # Current auth_date but deliberately wrong hash
    bad_init_data = urlencode({
        "auth_date": str(int(time.time())),
        "user": '{"id":999}',
        "hash": "a" * 64,  # wrong hash, correct length
    })
    response = await client.post(
        "/api/v1/auth/session",
        headers={"X-Telegram-Init-Data": bad_init_data},
    )
    assert response.status_code == 401


async def test_session_missing_header(client):
    response = await client.post("/api/v1/auth/session")
    assert response.status_code == 422
