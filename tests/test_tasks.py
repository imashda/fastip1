import pytest


async def register_and_login(client, username="user1", email="user1@test.com", password="qwerty123"):
    await client.post("/auth/register", json={"username": username, "email": email, "password": password})
    res = await client.post("/auth/login", data={"username": username, "password": password})
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_create_task(client):
    token = await register_and_login(client)
    res = await client.post("/tasks", json={
        "title": "Тестовая задача",
        "description": "Описание",
        "priority": "medium"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Тестовая задача"
    assert data["status"] == "backlog"


@pytest.mark.asyncio
async def test_get_my_tasks(client):
    token = await register_and_login(client)
    await client.post("/tasks", json={"title": "Задача 1", "priority": "low"},
                      headers={"Authorization": f"Bearer {token}"})
    await client.post("/tasks", json={"title": "Задача 2", "priority": "high"},
                      headers={"Authorization": f"Bearer {token}"})
    res = await client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(res.json()) == 2


@pytest.mark.asyncio
async def test_change_task_status(client):
    token = await register_and_login(client)
    res = await client.post("/tasks", json={"title": "Задача", "priority": "medium"},
                            headers={"Authorization": f"Bearer {token}"})
    task_id = res.json()["id"]
    res = await client.patch(f"/tasks/{task_id}/status?new_status=in_progress",
                             headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_cannot_access_others_task(client):
    token1 = await register_and_login(client, "user1", "u1@test.com")
    token2 = await register_and_login(client, "user2", "u2@test.com")
    res = await client.post("/tasks", json={"title": "Чужая задача", "priority": "low"},
                            headers={"Authorization": f"Bearer {token1}"})
    task_id = res.json()["id"]
    res = await client.get(f"/tasks/{task_id}",
                           headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_delete_task(client):
    token = await register_and_login(client)
    res = await client.post("/tasks", json={"title": "Удалить меня", "priority": "low"},
                            headers={"Authorization": f"Bearer {token}"})
    task_id = res.json()["id"]
    res = await client.delete(f"/tasks/{task_id}",
                              headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 204