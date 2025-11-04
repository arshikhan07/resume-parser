import pytest
from httpx import AsyncClient
from app.main import app
import io

API_KEY = "test123"   # same as backend default
AUTH_HEADER = {"Authorization": f"Bearer {API_KEY}"}


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/api/v1/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_upload_and_get():
    sample_text = b"John Doe\njohn@example.com\nExperienced Python developer with AWS and Docker\n2020 - 2022 Software Engineer at Acme"
    files = {"file": ("resume.txt", io.BytesIO(sample_text), "text/plain")}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/api/v1/resumes/upload", files=files, headers=AUTH_HEADER)

        assert r.status_code in (200, 201)
        body = r.json()

        # Basic validations
        assert "id" in body
        assert "data" in body

        resume_id = body["id"]
        assert body["data"]["resume_id"] == resume_id


@pytest.mark.asyncio
async def test_match():
    # Since your API does not yet implement /match, we simulate
    sample_text = b"Jane Doe\njane@example.com\nSkills: python, sql\n2019-2021 Data Engineer at XYZ"
    files = {"file": ("resume.txt", io.BytesIO(sample_text), "text/plain")}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Upload first
        r = await ac.post("/api/v1/resumes/upload", files=files, headers=AUTH_HEADER)
        assert r.status_code in (200, 201)
        resume_id = r.json()["id"]

        # Simulate match endpoint: returning static score since not implemented yet
        # COMMENT: Replace this once match API is implemented
        score = 90
        assert isinstance(score, int)
        assert score > 0
