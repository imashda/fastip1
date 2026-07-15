import pytest


@pytest.mark.asyncio
async def test_register(client):
    res = await client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "qwerty123"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@test.com"
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    await client.post("/auth/register", json={
        "username": "testuser", "email": "test@test.com", "password": "qwerty123"
    })
    res = await client.post("/auth/register", json={
        "username": "testuser", "email": "other@test.com", "password": "qwerty123"
    })
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_login(client):
    await client.post("/auth/register", json={
        "username": "testuser", "email": "test@test.com", "password": "qwerty123"
    })
    res = await client.post("/auth/login", data={
        "username": "testuser", "password": "qwerty123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "username": "testuser", "email": "test@test.com", "password": "qwerty123"
    })
    res = await client.post("/auth/login", data={
        "username": "testuser", "password": "wrongpass"
    })
    assert res.status_code == 401