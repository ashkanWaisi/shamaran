import httpx
import pytest

from shamaran.exceptions import ProviderError
from shamaran.providers.base import ChatMessage
from shamaran.providers.ollama import OllamaProvider
from shamaran.providers.openai_compatible import OpenAICompatibleProvider


def provider(handler) -> OllamaProvider:
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    return OllamaProvider("http://ollama.test", "test-model", client=client)


def test_ollama_response_parsing() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = __import__("json").loads(request.content)
        assert payload["format"]["type"] == "object"
        assert "action" in payload["format"]["properties"]
        assert payload["options"]["temperature"] == 0
        return httpx.Response(
            200,
            json={"model": "test-model", "message": {"content": '{"final":"done"}'}},
            request=request,
        )

    item = provider(handler)
    response = item.complete([ChatMessage(role="user", content="hello")], [])
    assert response.content == '{"final":"done"}'


def test_malformed_response() -> None:
    item = provider(lambda request: httpx.Response(200, json={"unexpected": True}, request=request))
    with pytest.raises(ProviderError, match="malformed"):
        item.complete([ChatMessage(role="user", content="hello")], [])


def test_connection_error() -> None:
    def fail(request):
        raise httpx.ConnectError("refused", request=request)

    with pytest.raises(ProviderError, match="could not connect"):
        provider(fail).complete([ChatMessage(role="user", content="hello")], [])


def test_timeout() -> None:
    def fail(request):
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(ProviderError, match="timed out"):
        provider(fail).complete([ChatMessage(role="user", content="hello")], [])


def test_health_reports_unavailable_model() -> None:
    item = provider(lambda request: httpx.Response(
        200, json={"models": [{"name": "another-model"}]}, request=request
    ))
    ok, detail = item.health()
    assert not ok
    assert "unavailable" in detail


def compatible_provider(handler) -> OpenAICompatibleProvider:
    transport = httpx.MockTransport(handler)
    return OpenAICompatibleProvider(
        "http://models.test/v1", "local-model", client=httpx.Client(transport=transport)
    )


def test_openai_compatible_discovers_models() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/models"
        return httpx.Response(200, json={"data": [{"id": "model-a"}, {"id": "model-b"}]}, request=request)

    assert compatible_provider(handler).models() == ["model-a", "model-b"]


def test_openai_compatible_chat_and_tool_observation() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = __import__("json").loads(request.content)
        assert request.url.path == "/v1/chat/completions"
        assert payload["model"] == "local-model"
        assert payload["messages"][1] == {"role": "user", "content": "Tool observation:\nresult"}
        return httpx.Response(
            200,
            json={"model": "local-model", "choices": [{"message": {"content": '{"final":"done"}'}}]},
            request=request,
        )

    response = compatible_provider(handler).complete(
        [ChatMessage(role="user", content="hello"), ChatMessage(role="tool", content="result")], []
    )
    assert response.content == '{"final":"done"}'
