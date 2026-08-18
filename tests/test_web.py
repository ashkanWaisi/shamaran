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
    assert {item["id"] for item in status.json()["providers"]} >= {"ollama", "lm-studio", "vllm", "custom"}


def test_model_discovery_for_compatible_server(monkeypatch) -> None:
    monkeypatch.setattr(
        "shamaran.webapp.OpenAICompatibleProvider.models",
        lambda _provider: ["local-a", "local-b"],
    )
    client = TestClient(create_app())
    response = client.post(
        "/api/models/discover",
        json={"provider": "openai-compatible", "endpoint": "http://localhost:1234/v1"},
    )
    assert response.status_code == 200
    assert response.json()["models"] == ["local-a", "local-b"]


def test_model_discovery_rejects_invalid_endpoint() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/models/discover", json={"provider": "ollama", "endpoint": "file:///tmp/models"}
    )
    assert response.status_code == 400
