import pytest
import requests

from research_agent.llm import LLMClient, LLMError


class FakeResponse:
    status_code = 200
    headers = {"content-type": "text/html; charset=utf-8"}
    text = "<!doctype html><title>Gateway</title>"

    def raise_for_status(self):
        return None

    def json(self):
        raise ValueError("not json")


def test_llm_client_reports_non_json_response(monkeypatch):
    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("research_agent.llm.requests.post", fake_post)
    client = LLMClient("https://example.com", "key", max_retries=1)

    with pytest.raises(LLMError) as exc:
        client.chat("model", [{"role": "user", "content": "hi"}])

    message = str(exc.value)
    assert "non-JSON response" in message
    assert "https://example.com/chat/completions" in message
    assert "text/html" in message
    assert "usually ends with /v1" in message


def test_llm_client_uses_longer_backoff_for_rate_limit_and_server_errors(monkeypatch):
    response = requests.Response()
    response.status_code = 503
    response.url = "https://example.com/v1/chat/completions"
    response._content = b"Service Unavailable"
    error = requests.HTTPError("503 Server Error", response=response)

    def fake_post(*args, **kwargs):
        raise error

    sleeps: list[float] = []
    monkeypatch.setattr("research_agent.llm.requests.post", fake_post)
    monkeypatch.setattr("research_agent.llm.time.sleep", sleeps.append)

    client = LLMClient("https://example.com/v1", "key", max_retries=3)

    with pytest.raises(LLMError):
        client.chat("model", [{"role": "user", "content": "hi"}])

    assert sleeps == [8, 16]
