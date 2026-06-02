"""
Weather Tool - Get weather information for a location.
Uses the free Open-Meteo API.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def get_weather(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Get weather information for a location.

    Args:
        latitude: Location latitude
        longitude: Location longitude

    Returns:
        Dict with current weather information
    """
    # Implementation in Phase 3
    logger.info(f"Getting weather for: {latitude}, {longitude}")
    return {}


# Tool definition for LLM
WEATHER_TOOL_DEFINITION = {
    "name": "weather",
    "description": "Get current weather information for a location",
    "input_schema": {
        "type": "object",
        "properties": {
            "latitude": {
                "type": "number",
                "description": "Location latitude"
            },
            "longitude": {
                "type": "number",
                "description": "Location longitude"
            }
        },
        "required": ["latitude", "longitude"]
    }
}
