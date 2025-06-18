"""MCP client model."""
from typing import Annotated, Any, Literal, MutableSequence, Optional, Union
import mcp
from pydantic import BaseModel, Field
from mcp.client.session import ClientSession
from mcp.shared.context import RequestContext, LifespanContextT
from mcp.shared.session import RequestResponder
from mcp.types import ServerRequest,ClientResult, ServerNotification, LoggingMessageNotificationParams, SamplingMessage, CreateMessageRequestParams, Prompt
from fastmcp import Client
from fastmcp.client import ClientTransport, StdioTransport, WSTransport, SSETransport, StreamableHttpTransport

from vogonpoetry.logging import logger
from vogonpoetry.utils.filter_config import FilterConfig, FilterUtility

Transport = Union[Literal['stdio'], Literal['websocket'], Literal['sse'], Literal['streamable']]

class StdioConfig(BaseModel):
    """STDIO transport configuration."""
    type: Literal['stdio'] = 'stdio'
    command: Annotated[str, Field(description="Command to start the STDIO transport process.")]
    args: Annotated[list[str], Field(default_factory=list, description="Arguments for the command.")]
    env: Annotated[dict[str, str], Field(default_factory=dict, description="Environment variables for the process.")]
    cwd: Annotated[Optional[str], Field(None, description="Working directory for the process.")]
    keep_alive: Annotated[Optional[bool], Field(None, description="Whether to keep the process alive.")]

class WebsocketConfig(BaseModel):
    """WebSocket transport configuration."""
    type: Literal['websocket'] = 'websocket'
    url: Annotated[str, Field(description="WebSocket URL for the MCP client.")]

class SSEConfig(BaseModel):
    """SSE transport configuration."""
    type: Literal['sse'] = 'sse'
    url: Annotated[str, Field(description="SSE URL for the MCP client.")]
    headers: Annotated[dict[str, str], Field(default_factory=dict, description="Headers for the SSE connection.")]
    timeout: Annotated[Optional[float], Field(None, description="Timeout for the SSE connection in seconds.")]

class StreamableConfig(BaseModel):
    """Streamable transport configuration."""
    type: Literal['streamable'] = 'streamable'
    url: Annotated[str, Field(description="SSE URL for the MCP client.")]
    headers: Annotated[dict[str, str], Field(default_factory=dict, description="Headers for the SSE connection.")]
    timeout: Annotated[Optional[float], Field(None, description="Timeout for the SSE connection in seconds.")]

TransportConfig = Annotated[
    Union[
        StdioConfig,
        WebsocketConfig,
        SSEConfig,
        StreamableConfig,
    ],
    Field(discriminator="type", description="Transport configuration for the MCP client.")
]

class MCPClientConfig(BaseModel):
    """MCP client configuration."""
    transport: Annotated[TransportConfig, Field(description="Transport configuration for the MCP client.")]
     


SamplingResponse = str | mcp.CreateMessageResult

class MCPClient(BaseModel):
    """MCP client model."""
    id: Annotated[str, Field(description="Unique identifier for the MCP client.")]
    transport: Annotated[TransportConfig, Field(description="Transport configuration for the MCP client.")]
    resource_template: Annotated[list[FilterConfig], Field([], description="Resource template filter configuration.")]
    tools: Annotated[list[FilterConfig], Field([], description="Tools filter configuration.")]
    prompts: Annotated[list[FilterConfig], Field([], description="Prompts filter configuration.")]  

    def model_post_init(self, context: Any) -> None:
        """Initialize the MCP client."""
        self._logger = logger(f"MCPClient-{self.id}")
        self._transport: ClientTransport
        if self.transport.type == 'stdio':
            transport = StdioTransport(self.transport.command, self.transport.args, self.transport.env, self.transport.cwd, self.transport.keep_alive)
        elif self.transport.type == 'websocket':
            transport = WSTransport(self.transport.url)
        elif self.transport.type == 'sse':
            transport = SSETransport(url=self.transport.url, headers=self.transport.headers, sse_read_timeout=self.transport.timeout)
        elif self.transport.type == 'streamable':
            transport = StreamableHttpTransport(url=self.transport.url, headers=self.transport.headers, sse_read_timeout=self.transport.timeout)
        else:
            raise ValueError(f"Unsupported transport type: {self.transport.type}")
        self._client = Client(
            transport,
            message_handler=self.handle_message,
            progress_handler=self.handle_progress,
            log_handler=self.handle_logging_message,
            sampling_handler=self.handle_sampling,
        )

    async def handle_message(self, message: RequestResponder[ServerRequest, ClientResult] | ServerNotification | Exception) -> None:
        """Handle incoming messages from the MCP client."""
        self._logger.info("Received message", message=message)

    async def handle_progress(self, progress: float, total: float | None, message: str | None) -> None:
        """Handle progress updates from the MCP client."""
        self._logger.info("Progress update", progress=progress, total=total, message=message)

    async def handle_logging_message(self, params: LoggingMessageNotificationParams) -> None:
        """Handle logging messages from the MCP client."""
        level = params.level.lower()
        log_method = getattr(self._logger, level, self._logger.info)
        log_method("MCP Log", **params.data)

    async def handle_sampling(self, sampling: list[SamplingMessage], params: CreateMessageRequestParams, context: RequestContext[ClientSession, LifespanContextT]) -> SamplingResponse:
        """Handle sampling requests from the MCP client."""
        self._logger.info("Received sampling request", sampling=sampling)
        raise NotImplementedError("Sampling handler not implemented")

    async def list_tools(self) -> MutableSequence[mcp.Tool]:
        """List available tools from the MCP client."""
        async with self._client:
            return FilterUtility[mcp.Tool].filter_items(self.tools, await self._client.list_tools(), lambda tool: tool.name)
        
    async def list_prompts(self) -> MutableSequence[Prompt]:
        """List available tools from the MCP client."""
        async with self._client:
            return FilterUtility[Prompt].filter_items(self.prompts, await self._client.list_prompts(), lambda prompt: prompt.name)