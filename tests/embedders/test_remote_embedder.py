import pytest
import httpx
import asyncio
from vogonpoetry.embedders.remote import RemoteEmbedder

class MockResponse:
    def __init__(self, data):
        self._data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self._data

class MockAsyncClient:
    def __init__(self, response):
        self._response = response
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    async def post(self, url, json, headers):
        return self._response

@pytest.mark.asyncio
async def test_embed(monkeypatch):
    embedder = RemoteEmbedder(
        name="test",
        type="remote",
        model="mock",
        url="http://mock",
        headers={},
        timeout=10
    )

    response_data = {"data": [[0.1, 0.2, 0.3]]}
    monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: MockAsyncClient(MockResponse(response_data)))

    result = await embedder.embed(["foo"])
    assert result == [[0.1, 0.2, 0.3]]