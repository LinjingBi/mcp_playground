import os
import json
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from pydantic import BaseModel


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
)

_SERVER_CONFIG = 'server_config.json'

class ServerConfig(BaseModel):
    command: str
    args: Optional[List[str]] = None
    env: Optional[Dict] = None


def load_config() -> ServerConfig:
    if not os.path.isfile(_SERVER_CONFIG):
        logging.warning(f"No server config file found under {_SERVER_CONFIG}.")
        return None
    with open(_SERVER_CONFIG) as f:
        return ServerConfig(**json.load(f))


# class ServerConfig():
#     def __init__(self):
#         self.load_env()
#         self.llm_api_key = os.getenv('LLM_API_KEY')

#     def load_env(self):
#         load_dotenv()

#     def load_server_config(self) -> Optional[Dict]:
#         if not os.path.isfile(_SERVER_CONFIG):
#             logging.warning(f"No server config file found under {_SERVER_CONFIG}.")
#             return None
#         with open(_SERVER_CONFIG) as f:
#             return json.load(f)