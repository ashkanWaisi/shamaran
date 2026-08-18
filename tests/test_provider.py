import httpx
import pytest

from shamaran.exceptions import ProviderError
from shamaran.providers.base import ChatMessage
from shamaran.providers.ollama import OllamaProvider


def provider(handler) -> OllamaProvider:
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    return OllamaProvider("http://ollama.test", "test-model", client=client)


def test_ollama_response_parsing() -> None:
    item = provider(lambda request: httpx.Response(
        200, json={"model": "test-model", "message": {"content": '{"final":"done"}'}}, request=request
    ))
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
