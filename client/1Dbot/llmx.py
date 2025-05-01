import logging
import asyncio
from typing import List

import httpx


logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
)

class LLMx:
    """groqcloud API doc: https://console.groq.com/docs/api-reference#chat"""
    CHAT_URL = 'https://api.groq.com/openai/v1/chat/completions'
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._request_header = {
            'Content-Type': 'application/json',
            "Authorization": f"Bearer {self._api_key}",
        }
        self.client = httpx.AsyncClient(
            headers=self._request_header,
            timeout=30.0
        )
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logging.error(f"An error occurred in llmx exit: {exc_val}")  
        await self.client.aclose()

    async def chat(self, messages: List[dict]) -> str:

        payload = {
            "model": "qwen-qwq-32b",
            "messages": messages,
            # What sampling temperature to use, between 0 and 2. 
            # Higher values like 0.8 will make the output more random, 
            # while lower values like 0.2 will make it more focused and deterministic.
            "temperature": 0.7,
            "max_completion_tokens": 4096,
            "stream": False,
            "stop": None,
        }
        retry = 3
        try:
            for i in range(retry):
                response = await self.client.post(self.CHAT_URL, json=payload)
                response.raise_for_status()
                data = response.json()
                return data['choice'][0]['message']['content']
        except httpx.HTTPError as err:
            logging.error(f'{i+1} time request to LLM chat failed, error {str(err)}')
            if isinstance(err, httpx.HTTPStatusError):
                status_code = err.response.status_code
                logging.debug(f"Status code: {status_code}")
                logging.debug(f"Response details: {err.response.text}")
            
            asyncio.sleep(1)
        
        return (f"I encountered an error, please check system log for more details. "
                "Please try again or rephrase your request.")
