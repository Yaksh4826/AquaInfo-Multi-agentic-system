
"""
REAL Web Search Tool using SerpAPI (Google Search API).

This tool performs real Google web searches using SERPAPI_API_KEY
from the .env file. It returns live results (title, snippet, url).
No fake database, no fallback, no example.com.
"""

from typing import List, Dict
import os
from dotenv import load_dotenv

try:
    from serpapi import GoogleSearch
except ImportError as exc:  # pragma: no cover - dependency hint
    GoogleSearch = None
    _serpapi_import_error = exc


class WebSearchTool:
    def __init__(self) -> None:
        load_dotenv()
        api_key = os.getenv("SERPAPI_API_KEY")

        if not api_key:
            raise ValueError("ERROR: SERPAPI_API_KEY not found in .env file")

        if GoogleSearch is None:
            raise ImportError(
                "serpapi package is required. Install with `pip install serpapi`. "
                f"Original error: {_serpapi_import_error}"
            )

        self.api_key = api_key

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """
        Perform a real Google search using SerpAPI.
        Returns list of results with title, snippet, url.
        """
        print("DEBUG: Using SerpAPI for REAL web search")

        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": max_results,
            "hl": "en",
            "gl": "ca"
        }

        search = GoogleSearch(params)
        response = search.get_dict()
        organic = response.get("organic_results", [])

        results: List[Dict[str, str]] = []

        for item in organic[:max_results]:
            results.append({
                "title": item.get("title", "No title"),
                "snippet": item.get("snippet", "") or "",
                "url": item.get("link", "") or "",
            })

        return results
