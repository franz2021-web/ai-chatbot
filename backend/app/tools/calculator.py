"""
Calculator Tool - Performs mathematical calculations.
"""

import logging

logger = logging.getLogger(__name__)


async def calculate(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Args:
        expression: Math expression (e.g., "2 + 2 * 3")

    Returns:
        String result of the calculation
    """
    # Implementation in Phase 3
    logger.info(f"Calculating: {expression}")
    return "Not yet implemented"


# Tool definition for LLM
CALCULATOR_TOOL_DEFINITION = {
    "name": "calculator",
    "description": "Perform mathematical calculations",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression (e.g., '2 + 2 * 3')"
            }
        },
        "required": ["expression"]
    }
}
