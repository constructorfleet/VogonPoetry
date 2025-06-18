import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from .test_local_embedder import DummySentenceTransformer, Tensor
from vogonpoetry.embedders import EmbedderTypeAdapter
from vogonpoetry.embedders.local import LocalEmbedder
from vogonpoetry.embedders.remote import RemoteEmbedder


@patch("vogonpoetry.embedders.local.SentenceTransformer", new=DummySentenceTransformer)
def test_embedder_typeadapter_local():
    data = {"name": "My Test Embedder", "type": "local", "model_name": "my_model"}
    embedder = EmbedderTypeAdapter.validate_python(data)
    assert isinstance(embedder, LocalEmbedder)
    assert embedder.model_name == "my_model"


def test_embedder_typeadapter_remote():
    data = {
        "name": "My Remote Embedder",
        "type": "remote",
        "url": "http://localhost:8000/embed",
        "model": "text-embedding-3-small",
    }
    embedder = EmbedderTypeAdapter.validate_python(data)
    assert isinstance(embedder, RemoteEmbedder)
    assert embedder.url == "http://localhost:8000/embed"


def test_embedder_typeadapter_invalid_type():
    data = {"type": "unknown", "foo": "bar"}
    with pytest.raises(ValidationError):
        EmbedderTypeAdapter.validate_python(data)
