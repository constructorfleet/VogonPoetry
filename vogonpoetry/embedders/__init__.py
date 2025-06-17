from typing import Annotated, Union

from pydantic import Field, TypeAdapter

from vogonpoetry.embedders.local import LocalEmbedder
from vogonpoetry.embedders.remote import RemoteEmbedder


Embedder = Annotated[
    Union[
        LocalEmbedder,
        RemoteEmbedder
    ],
    Field(
        description="Configuration for the embedder in the Vogon Poetry project.",
        discriminator="type"
    )
]

EmbedderTypeAdapter = TypeAdapter(Embedder)