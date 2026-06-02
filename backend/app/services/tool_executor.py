"""
Tool Executor - Executes tools called by the LLM.
Coordinates between LLM tool calls and actual tool implementations.
"""

import logging
from typing import Any, Dict

from app.tools.calculator import calculate, CALCULATOR_TOOL_DEFINITION
from app.tools.web_search import search_web, WEB_SEARCH_TOOL_DEFINITION
from app.tools.weather import get_weather, WEATHER_TOOL_DEFINITION

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tools called by the LLM."""

    def __init__(self):
        """Initialize tool executor with available tools."""
        self.tools: Dict[str, Any] = {
            "calculator": calculate,
            "web_search": search_web,
            "weather": get_weather,
        }
        self.tool_definitions = {
            "calculator": CALCULATOR_TOOL_DEFINITION,
            "web_search": WEB_SEARCH_TOOL_DEFINITION,
            "weather": WEATHER_TOOL_DEFINITION,
        }
        logger.info(f"Initialized ToolExecutor with tools: {list(self.tools.keys())}")

    async def execute_tool(
        self, tool_name: str, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool result as a dict with success/error status
        """
        # Check if tool exists
        if tool_name not in self.tools:
            error_msg = f"Unknown tool: {tool_name}. Available tools: {list(self.tools.keys())}"
            logger.warning(error_msg)
            return {"success": False, "error": error_msg}

        tool_func = self.tools[tool_name]
        logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

        try:
            # Execute tool
            result = await tool_func(**tool_input)
            logger.info(f"Tool {tool_name} completed successfully")
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def register_tool(self, name: str, func: Any) -> None:
        """
        Register a tool.

        Args:
            name: Tool name
            func: Async callable that executes the tool
        """
        self.tools[name] = func
        logger.info(f"Registered tool: {name}")

    def get_tool_definitions(self) -> list:
        """
        Get tool definitions for sending to LLM.

        Returns:
            List of tool definitions for OpenAI-compatible API
        """
        return list(self.tool_definitions.values())


# Global instance
_executor = None


def get_executor() -> ToolExecutor:
    """Get or create the global tool executor instance."""
    global _executor
    if _executor is None:
        _executor = ToolExecutor()
    return _executor
