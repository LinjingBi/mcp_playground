import os

from config import load_config
from server import Server
from llmx import LLMx

def main():
    server_configs = load_config()
    servers = [Server(config) for config in server_configs]
    llm_apikey = os.environ['LLM_API_KEY']
    llm = LLMx(llm_apikey)
