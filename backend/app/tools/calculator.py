"""
Calculator Tool - Performs mathematical calculations.
"""

import logging
import math
import re

logger = logging.getLogger(__name__)


async def calculate(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Args:
        expression: Math expression (e.g., "2 + 2 * 3")

    Returns:
        String result of the calculation
    """
    try:
        # Validate expression (only allow numbers, operators, and function names)
        if not re.match(r'^[0-9+\-*/(). \t\n,sqrt,sin,cos,tan,log,exp,pi,e]*$', expression):
            return "Error: Invalid characters in expression"

        # Create safe namespace with only math functions
        safe_dict = {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
            "__builtins__": {},
        }

        # Evaluate the expression
        result = eval(expression, safe_dict)

        # Format result
        if isinstance(result, float):
            # Round to 10 decimal places to avoid floating point errors
            result = round(result, 10)

        logger.info(f"Calculated: {expression} = {result}")
        return str(result)

    except ZeroDivisionError:
        logger.warning(f"Division by zero in: {expression}")
        return "Error: Division by zero"
    except ValueError as e:
        logger.warning(f"Math error in {expression}: {str(e)}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return f"Error: {str(e)}"


# Tool definition for LLM
CALCULATOR_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Perform mathematical calculations (supports +, -, *, /, (), sqrt, sin, cos, tan, log, exp, pi, e)",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression (e.g., '2 + 2 * 3' or 'sqrt(16) + pi')"
                }
            },
            "required": ["expression"]
        }
    }
}
