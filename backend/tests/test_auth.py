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


async def test_session_returns_existing_user(client, init_data):
    await client.post("/api/v1/auth/session", headers={"X-Telegram-Init-Data": init_data})
    response = await client.post("/api/v1/auth/session", headers={"X-Telegram-Init-Data": init_data})
    assert response.status_code == 200
    assert response.json()["is_new_user"] is False


async def test_session_invalid_init_data(client):
    response = await client.post(
        "/api/v1/auth/session",
        headers={"X-Telegram-Init-Data": "auth_date=123&user=%7B%7D&hash=badhash"},
    )
    assert response.status_code == 401


async def test_session_missing_header(client):
    response = await client.post("/api/v1/auth/session")
    assert response.status_code in (400, 422)
