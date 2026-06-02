"""
Web Search Tool - Search the web using DuckDuckGo.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


async def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo.

    Args:
        query: Search query
        max_results: Maximum number of results to return

    Returns:
        List of search results with title, link, and snippet
    """
    try:
        from duckduckgo_search import DDGS

        logger.info(f"Searching web for: {query}")

        # Create search client
        ddgs = DDGS()

        # Perform search
        results = []
        for i, result in enumerate(ddgs.text(query, max_results=max_results)):
            if i >= max_results:
                break

            results.append({
                "title": result.get("title", ""),
                "link": result.get("href", ""),
                "snippet": result.get("body", "")
            })

        logger.info(f"Found {len(results)} results for: {query}")
        return results

    except ImportError:
        logger.error("duckduckgo-search not installed")
        return [{"title": "Error", "link": "", "snippet": "duckduckgo-search library not installed"}]
    except Exception as e:
        logger.error(f"Web search error: {str(e)}")
        return [{"title": "Error", "link": "", "snippet": f"Search failed: {str(e)}"}]


# Tool definition for LLM
WEB_SEARCH_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for information using DuckDuckGo",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}
