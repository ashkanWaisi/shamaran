from fastapi.testclient import TestClient

from shamaran.webapp import create_app


def test_web_ui_and_status(monkeypatch) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"models": [{"name": "qwen3.5:9b"}]}

    monkeypatch.setattr("shamaran.webapp.httpx.get", lambda *args, **kwargs: FakeResponse())
    client = TestClient(create_app())

    page = client.get("/")
    assert page.status_code == 200
    assert "Shamaran Web" in page.text

    status = client.get("/api/status")
    assert status.status_code == 200
    assert status.json()["models"] == ["qwen3.5:9b"]
    assert status.json()["tools"]
