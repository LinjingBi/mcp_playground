import os
import json
import logging
from typing import Optional, Dict, Any, List

from pydantic import BaseModel
from mcp.types import Tool


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
)

_SERVER_CONFIG = 'server_config.json'
SHORT_MEMORY_DIR = os.path.join(os.environ['HOME'], '.bot1d', 'storage', 'short-memory')

class ServerConfig(BaseModel):
    name: str
    command: str
    args: Optional[List[str]] = None
    env: Optional[Dict] = None

# TODO raise error for servers with the same name
def load_config() -> List[ServerConfig | None]:
    if not os.path.isfile(_SERVER_CONFIG):
        logging.warning(f"No server config file found under {_SERVER_CONFIG}.")
        return []
    with open(_SERVER_CONFIG) as f:
        servers = json.load(f)['mcpServers']
        return [ServerConfig(name=key, **value) for key, value in servers.items()]

def format_tool_description(server_name: str, tools: list[Tool | None]) -> str:
    result = ''
    for tool in tools:
        name = tool.name
        descrip = tool.description
        params = ''
        for name, values in tool.inputSchema.get('properties', {}).items():
            params += name + (f':{values["description"]}' if values.get('description') else ".")
            if name in tool.inputSchema.get('required', []):
                params += '. Required.\n'
            else:
                params += '\n'
        
        text = f"""
        Server: {server_name}\n
        Tool: {name}\n
        Description: {descrip}\n
        Params: {params}
        """
        result += text + '\n'
    return result

