# tools/web_search_tool.py

"""
REAL Web Search Tool using Wikipedia API.
Falls back to a mini local DB if network fails.
"""

from typing import List, Dict
import requests
import html


class WebSearchTool:
    def __init__(self):
        self._fallback_db = {
            "nitrate pollution": {
                "title": "Understanding Nitrate Pollution",
                "snippet": "Nitrate pollution harms water by causing algal blooms and reducing oxygen levels.",
                "url": "https://example.com/nitrate"
            },
            "water quality": {
                "title": "Water Quality Basics",
                "snippet": "Water quality includes pH, turbidity, dissolved oxygen, and contaminants.",
                "url": "https://example.com/water-quality"
            }
        }

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """
        Main function:
        1. Try REAL Wikipedia search
        2. If it fails → fallback to mini DB
        """
        try:
            real_results = self._wikipedia_search(query, max_results)
            if real_results:
                return real_results
        except Exception:
            pass

        return self._fallback_search(query)

    # ---------------------------------------
    # REAL WEB SEARCH (WIKIPEDIA)
    # ---------------------------------------
    def _wikipedia_search(self, query: str, limit: int = 3) -> List[Dict[str, str]]:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": limit
        }

        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        results = []
        for item in data.get("query", {}).get("search", []):
            title = item.get("title", "")
            snippet_raw = item.get("snippet", "")
            snippet = html.unescape(snippet_raw.replace("<span class=\"searchmatch\">", "").replace("</span>", ""))
            page_id = item.get("pageid")

            if page_id is None:
                url_out = "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")
            else:
                url_out = f"https://en.wikipedia.org/?curid={page_id}"

            results.append({
                "title": title,
                "snippet": snippet,
                "url": url_out
            })

        return results

    # ---------------------------------------
    # FALLBACK SEARCH
    # ---------------------------------------
    def _fallback_search(self, query: str) -> List[Dict[str, str]]:
        q = query.lower()
        for key, entry in self._fallback_db.items():
            if key in q:
                return [entry]

        return [{
            "title": "General Water Pollution Info",
            "snippet": "Water pollution affects ecosystems and human health.",
            "url": "https://example.com/water"
        }]

# tools/web_search_tool.py

"""
REAL Web Search Tool using Wikipedia API.
Falls back to a mini local DB if network fails.
"""

from typing import List, Dict
import requests
import html


class WebSearchTool:
    def __init__(self):
        self._fallback_db = {
            "nitrate pollution": {
                "title": "Understanding Nitrate Pollution",
                "snippet": "Nitrate pollution harms water by causing algal blooms and reducing oxygen levels.",
                "url": "https://example.com/nitrate"
            },
            "water quality": {
                "title": "Water Quality Basics",
                "snippet": "Water quality includes pH, turbidity, dissolved oxygen, and contaminants.",
                "url": "https://example.com/water-quality"
            }
        }

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """
        Main function:
        1. Try REAL Wikipedia search
        2. If it fails → fallback to mini DB
        """
        try:
            real_results = self._wikipedia_search(query, max_results)
            if real_results:
                return real_results
        except Exception:
            pass

        return self._fallback_search(query)

    # ---------------------------------------
    # REAL WEB SEARCH (WIKIPEDIA)
    # ---------------------------------------
    def _wikipedia_search(self, query: str, limit: int = 3) -> List[Dict[str, str]]:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": limit
        }

        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        results = []
        for item in data["query"]["search"]:
            title = item["title"]
            snippet_raw = item["snippet"]
            snippet = html.unescape(snippet_raw.replace("<span class=\"searchmatch\">", "").replace("</span>", ""))
            page_id = item["pageid"]

            results.append({
                "title": title,
                "snippet": snippet,
                "url": f"https://en.wikipedia.org/?curid={page_id}"
            })

        return results

    # ---------------------------------------
    # FALLBACK SEARCH
    # ---------------------------------------
    def _fallback_search(self, query: str):
        q = query.lower()
        for key, entry in self._fallback_db.items():
            if key in q:
                return [entry]

        return [{
            "title": "General Water Pollution Info",
            "snippet": "Water pollution affects ecosystems and human health.",
            "url": "https://example.com/water"
        }]
