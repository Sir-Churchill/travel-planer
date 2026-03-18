import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

BASE_URL = "http://test"


@pytest.mark.asyncio
async def test_create_and_complete_project():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        # 1. Create a project with two real IDs
        payload = {
            "name": "Art Masterpieces Tour",
            "description": "A quick trip to Chicago's best art",
            "start_date": "2026-05-20",
            "places": [
                {"external_id": 27992, "notes": "Grand Jatte - Must see"},
                {"external_id": 28067, "notes": "Nighthawks - Iconic"},
            ],
        }
        response = await ac.post("/projects", json=payload)
        assert response.status_code == 201
        project = response.json()
        project_id = project["id"]
        place_ids = [p["id"] for p in project["places"]]

        assert project["is_completed"] is False
        assert len(project["places"]) == 2

        # 2. Visit the first place
        resp_p1 = await ac.patch(
            f"/projects/{project_id}/places/{place_ids[0]}", json={"is_visited": True}
        )
        assert resp_p1.status_code == 200

        # 3. Check if project is still not completed
        resp_proj_mid = await ac.get(f"/projects/{project_id}")
        assert resp_proj_mid.json()["is_completed"] is False

        # 4. Visit the second place
        resp_p2 = await ac.patch(
            f"/projects/{project_id}/places/{place_ids[1]}", json={"is_visited": True}
        )
        assert resp_p2.status_code == 200

        # 5. Check if project is now COMPLETED
        resp_proj_final = await ac.get(f"/projects/{project_id}")
        assert resp_proj_final.json()["is_completed"] is True
        print("\n[SUCCESS] Project automatically completed after visiting all places!")


@pytest.mark.asyncio
async def test_invalid_artwork_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        payload = {
            "name": "Failure Test",
            "description": "Testing non-existent ID",
            "start_date": "2026-05-20",
            "places": [{"external_id": 999999, "notes": "Fake ID"}],
        }
        response = await ac.post("/projects", json=payload)
        assert response.status_code == 404
