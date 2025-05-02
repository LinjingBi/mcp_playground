import os
import asyncio

from .config import load_config
from .server import Server
from .llmx import LLMx
from .client import BotClient

def main():
    server_configs = load_config()
    servers = [Server(config) for config in server_configs]
    llm_apikey = os.environ['LLM_API_KEY']
    llm = LLMx(llm_apikey)
    chatbot = BotClient(llm, servers)
    chatbot.initialize()
    chatbot.talk()

if __name__ == '__main__':
    asyncio.run(main())
