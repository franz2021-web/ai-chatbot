"""
Weather Tool - Get weather information for a location.
Uses the free Open-Meteo API.
"""

import logging
from typing import Dict, Any
import httpx

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
    try:
        # Use Open-Meteo free API (no API key required)
        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "temperature_unit": "fahrenheit"
        }

        logger.info(f"Getting weather for: {latitude}, {longitude}")

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()

        data = response.json()

        # Extract current weather
        if "current" not in data:
            return {"error": "No weather data available"}

        current = data["current"]

        # Map weather codes to descriptions
        weather_descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail",
        }

        weather_code = current.get("weather_code", 0)
        weather_description = weather_descriptions.get(weather_code, "Unknown")

        result = {
            "temperature": f"{current.get('temperature_2m')}°F",
            "apparent_temperature": f"{current.get('apparent_temperature')}°F",
            "humidity": f"{current.get('relative_humidity_2m')}%",
            "weather": weather_description,
            "wind_speed": f"{current.get('wind_speed_10m')} mph",
            "latitude": latitude,
            "longitude": longitude
        }

        logger.info(f"Weather retrieved: {result['weather']} - {result['temperature']}")
        return result

    except httpx.HTTPError as e:
        logger.error(f"Weather API error: {str(e)}")
        return {"error": f"Weather API error: {str(e)}"}
    except Exception as e:
        logger.error(f"Weather error: {str(e)}")
        return {"error": f"Weather error: {str(e)}"}


# Tool definition for LLM
WEATHER_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "weather",
        "description": "Get current weather information for a location using latitude and longitude",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Location latitude (-90 to 90)"
                },
                "longitude": {
                    "type": "number",
                    "description": "Location longitude (-180 to 180)"
                }
            },
            "required": ["latitude", "longitude"]
        }
    }
}
