from typing import Union

from pydantic import Field

from vogonpoetry.config.embedders.local import LocalEmbedderConfig
from vogonpoetry.config.embedders.remote import RemoteEmbedderConfig


EmbedderConfig = Union[
    LocalEmbedderConfig,
    RemoteEmbedderConfig,
    Field(
        description="Configuration for the embedder in the Vogon Poetry project.",
        discriminator="type"
    )
]