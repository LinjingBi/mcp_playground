import logging
from typing import List
import re

import httpx
import asyncio


logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
)

def extract_json_from_think(text: str) -> str:
    """
    Extract JSON content from text that may contain <think> tags.
    """
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    return text

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
    
    async def cleanup(self):
        if not self.client.is_closed:
            await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logging.error(f"An error occurred in llmx exit: {exc_val}")  
        await self.cleanup()

    async def chat(self, messages: List[dict]) -> str:

        payload = {
            "model": "qwen-qwq-32b",
            # "model": 'llama-3.1-8b-instant',
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
        for i in range(retry):
            try:
                response = await self.client.post(self.CHAT_URL, json=payload)
                response.raise_for_status()
                data = response.json()
                logging.info(f"LLM response usage: prompt_tokens/total_tokens {data['usage']['prompt_tokens']}/{data['usage']['total_tokens']}")
                content = data['choices'][0]['message']['content']
                return extract_json_from_think(content)
            except httpx.HTTPError as err:
                logging.error(f'{i+1} time request to LLM chat failed, error {str(err)}')
                if isinstance(err, httpx.HTTPStatusError):
                    status_code = err.response.status_code
                    logging.debug(f"Status code: {status_code}")
                    logging.debug(f"Response details: {err.response.text}")
                
                await asyncio.sleep(1)
            except Exception as err:
                logging.error(f'Exception occured when chatting with LLM {str(err)}')
                break
        
        return (f"I encountered an error, please check system log for more details. "
                "Please try again or rephrase your request.")
