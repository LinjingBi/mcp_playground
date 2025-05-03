from typing import Any
import logging
from contextlib import AsyncExitStack

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import ListToolsResult, Tool

from bot1d.config import ServerConfig

logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
)

class Server:
    """Interface to interact with MCP servers"""
    name: str
    _config: ServerConfig
    stdio_context: Any | None = None
    session: ClientSession | None = None
    _clean_lock: asyncio.Lock
    exit_stack: AsyncExitStack

    def __init__(self, config: ServerConfig) -> None:
        self.name = config.name
        self._config = config
        # for context manager clean up 
        self.stdio_context = None
        self.session = None

        self._clean_lock = asyncio.Lock()
        self.exit_stack = AsyncExitStack()
    
    async def initialize(self) -> str:
        """
        1. spawn server process
        2. hand out server's read and write as a context manager
        3. init clientsession context manager
        4. let clientsession initialize connection with server
        """
        server_params = StdioServerParameters(
            command=self._config.command,
            args=self._config.args,
            env = self._config.env
        )
        try:
            stdio_context = await self.exit_stack.enter_async_context(
                stdio_client(server_params) # spawn server process and return a context manager
            )
            read, write = stdio_context
            self.stdio_context = stdio_context
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write) # a context manager to manager the communication between server
            )
            await session.initialize()
            self.session = session
        except Exception as err:
            logging.error(f"Server {self.name} initialization failed, error {str(err)}")
            await self.cleanup()
            raise
    
    async def list_tools(self) -> list[Tool | None]:
        if self.session is None:
            raise RuntimeError(f'Server {self.name} not initialized')
        tools_resp: ListToolsResult = await self.session.list_tools()
        tools = []

        for item in tools_resp:
            if isinstance(item, tuple) and item[0] == 'tools':
                for tl in item[1]:
                    tools.append(tl) # tl: mcp.types.Tool
        return tools

    async def call_tool(self, name: str, params: dict[str, Any]) -> Any:
        if self.session is None:
            raise RuntimeError(f'Server {self.name} not initialized')
        retry = 3
        for i in range(retry):
            try:
                logging.info(f'Executing tool {name}')
                response = await self.session.call_tool(name, params)
                return response
            except Exception as err:
                logging.error(f'{i+1} time failed to execute tool {name}, err: {str(err)}')
                asyncio.sleep(1)
        logging.error(f'Failed to execute tool {name} after {retry} retries')

    async def cleanup(self):
        async with self._clean_lock:
            try:
                await self.exit_stack.aclose()
                self.session = None
                self.stdio_context = None
            except Exception as err:
                logging.error(f"Failed to cleanup for server {self.name}, err msg: {str(err)}")
        