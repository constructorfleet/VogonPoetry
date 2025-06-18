import pytest
from unittest.mock import patch, MagicMock
from vogonpoetry.embedders.local import LocalEmbedder


class Tensor:
    def __init__(self, data):
        self.data = data

    def tolist(self):
        return self.data


class DummySentenceTransformer:
    def __init__(self, model_name=""):
        self.model_name = model_name
        self.encode_called_with = None

    def encode(self, texts, convert_to_tensor=False):
        self.encode_called_with = (texts, convert_to_tensor)
        # Return a list of lists of floats, one per text
        return [Tensor([0.1 * i for i in range(3)]) for i in range(len(texts))]


@patch("vogonpoetry.embedders.local.SentenceTransformer", new=DummySentenceTransformer)
@patch("vogonpoetry.embedders.local.logger")
@pytest.mark.asyncio
async def test_local_embedder_embed(mock_logger):
    embedder = LocalEmbedder(name="test", model_name="test-model")
    embedder.model_post_init(None)
    texts = ["hello", "world"]
    result = await embedder.embed(texts)
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(vec, list) for vec in result)
    assert all(len(vec) == 3 for vec in result)
    mock_logger().debug.assert_called_with(
        "Classifying using local embeddings with model %s", "test-model"
    )


@patch("vogonpoetry.embedders.local.SentenceTransformer", new=DummySentenceTransformer)
@patch("vogonpoetry.embedders.local.logger")
@pytest.mark.asyncio
async def test_local_embedder_embed_single_encoding(mock_logger):
    class SingleEncodingDummy(DummySentenceTransformer):
        def encode(self, texts, convert_to_tensor=False):  # type: ignore
            # Simulate returning a single list for one text
            return Tensor([0.5, 0.6, 0.7])

    with patch(
        "vogonpoetry.embedders.local.SentenceTransformer", new=SingleEncodingDummy
    ):
        embedder = LocalEmbedder(name="test", model_name="test-model")
        embedder.model_post_init(None)
        texts = ["only one"]
        result = await embedder.embed(texts)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == [0.5, 0.6, 0.7]
