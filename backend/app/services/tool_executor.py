"""
Tool Executor - Executes tools called by the LLM.
Coordinates between LLM tool calls and actual tool implementations.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tools called by the LLM."""

    def __init__(self):
        """Initialize tool executor with available tools."""
        # Tools will be registered in Phase 3
        self.tools: Dict[str, Any] = {}

    async def execute_tool(
        self, tool_name: str, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool result as a dict

        Raises:
            ValueError: If tool name is unknown
        """
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

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

    def get_tool_definitions(self) -> Dict[str, Any]:
        """
        Get tool definitions for sending to LLM.

        Returns:
            Dictionary of tool name -> tool definition
        """
        # Will be populated in Phase 3
        return {}


# Global instance
_executor = None


def get_executor() -> ToolExecutor:
    """Get or create the global tool executor instance."""
    global _executor
    if _executor is None:
        _executor = ToolExecutor()
    return _executor
