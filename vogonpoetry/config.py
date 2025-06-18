"""Vogon Poetry Configuration"""

from typing import Annotated, Optional

from pydantic import BaseModel, Field

from vogonpoetry.embedders import Embedder
from vogonpoetry.mcp.client import MCPClient
from vogonpoetry.pipeline.pipeline import Pipeline


class Configuration(BaseModel):
    """Base configuration for the Vogon Poetry project."""

    name: Annotated[str, Field(description="Name of the configuration.")]
    description: Annotated[
        Optional[str],
        Field(None, description="Description of the configuration."),
    ]
    version: Annotated[
        Optional[str], Field(default=None, description="Version of the configuration.")
    ]
    pipeline: Annotated[
        Pipeline, Field(description="List of pipelines in the configuration.")
    ]
    embedders: Annotated[
        list[Embedder], Field([], description="List of embedders in the configuration.")
    ]
    mcp_servers: Annotated[
        list[MCPClient], Field([], description="List of MCP clients in the configuration.")
    ]
