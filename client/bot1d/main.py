import os
import asyncio

from bot1d.config import load_config
from bot1d.server import Server
from bot1d.llmx import LLMx
from bot1d.client import BotClient

async def main():
    server_configs = load_config()
    servers = [Server(config) for config in server_configs]
    llm_apikey = os.environ['LLM_API_KEY']
    llm = LLMx(llm_apikey)
    chatbot = BotClient(llm, servers)
    await chatbot.initialize()
    await chatbot.talk()

if __name__ == '__main__':
    asyncio.run(main())