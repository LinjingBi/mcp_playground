import httpx
import feedparser
from typing import List, Dict, Any


class ArxivX:
    BASE_URL = "http://export.arxiv.org/api/query"
    async def search(self, query: str, max_results: int=3) -> List[Dict[str, Any]]:
        """"Only return the most likely 3 papers by default"""
        async with httpx.AsyncClient() as client:
            params = {
                "search_query": query,
                "max_results": max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }

            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return feedparser.parse(response.content)['entries']
