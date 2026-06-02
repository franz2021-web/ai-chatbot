"""
Web Search Tool - Search the web using DuckDuckGo.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


async def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search the web using DuckDuckGo.

    Args:
        query: Search query
        max_results: Maximum number of results to return

    Returns:
        List of search results with title, link, and snippet
    """
    # Implementation in Phase 3
    logger.info(f"Searching web for: {query}")
    return []


# Tool definition for LLM
WEB_SEARCH_TOOL_DEFINITION = {
    "name": "web_search",
    "description": "Search the web for information using DuckDuckGo",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results (default: 5)",
                "default": 5
            }
        },
        "required": ["query"]
    }
}
