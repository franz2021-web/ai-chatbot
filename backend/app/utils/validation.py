"""
Enhanced Validation Utilities

Additional validation beyond Pydantic for security and data quality.
"""

import re
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""
    pass


def sanitize_string(value: str, max_length: int = 10000, field_name: str = "input") -> str:
    """
    Sanitize user input string.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        field_name: Field name for error messages

    Returns:
        Sanitized string

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")

    # Remove null bytes and control characters
    value = re.sub(r'[\x00-\x1F\x7F]', '', value)

    # Trim whitespace
    value = value.strip()

    # Check length
    if len(value) == 0:
        raise ValidationError(f"{field_name} cannot be empty")

    if len(value) > max_length:
        raise ValidationError(f"{field_name} exceeds maximum length of {max_length}")

    return value


def validate_message(message: str) -> str:
    """
    Validate user message.

    Args:
        message: User message

    Returns:
        Validated message

    Raises:
        ValidationError: If validation fails
    """
    return sanitize_string(message, max_length=4000, field_name="message")


def validate_expression(expression: str) -> str:
    """
    Validate calculator expression.

    Args:
        expression: Math expression

    Returns:
        Validated expression

    Raises:
        ValidationError: If validation fails
    """
    value = sanitize_string(expression, max_length=200, field_name="expression")

    # Only allow safe characters
    if not re.match(r'^[0-9+\-*/(). \t\n,sqrt,sin,cos,tan,log,exp,pi,e]*$', value):
        raise ValidationError("Expression contains invalid characters")

    return value


def validate_coordinates(latitude: float, longitude: float) -> tuple:
    """
    Validate geographic coordinates.

    Args:
        latitude: Latitude (-90 to 90)
        longitude: Longitude (-180 to 180)

    Returns:
        (latitude, longitude) tuple

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(latitude, (int, float)):
        raise ValidationError("Latitude must be a number")

    if not isinstance(longitude, (int, float)):
        raise ValidationError("Longitude must be a number")

    if not -90 <= latitude <= 90:
        raise ValidationError(f"Latitude must be between -90 and 90, got {latitude}")

    if not -180 <= longitude <= 180:
        raise ValidationError(f"Longitude must be between -180 and 180, got {longitude}")

    return float(latitude), float(longitude)


def validate_search_query(query: str) -> str:
    """
    Validate search query.

    Args:
        query: Search query

    Returns:
        Validated query

    Raises:
        ValidationError: If validation fails
    """
    return sanitize_string(query, max_length=500, field_name="search query")


def is_safe_tool_name(tool_name: str, allowed_tools: List[str]) -> bool:
    """
    Check if tool name is in whitelist.

    Args:
        tool_name: Tool name to check
        allowed_tools: List of allowed tool names

    Returns:
        True if tool is allowed, False otherwise
    """
    return tool_name in allowed_tools


def validate_api_key_format(api_key: str) -> bool:
    """
    Validate API key format (basic check).

    Args:
        api_key: API key to validate

    Returns:
        True if format is valid
    """
    if not isinstance(api_key, str):
        return False

    if len(api_key) < 10:
        return False

    # Check for common patterns (not exhaustive, just sanity check)
    if api_key.startswith("sk-") or api_key.startswith("nvapi-"):
        return True

    return False


def get_error_message(error: Exception, is_debug: bool = False) -> str:
    """
    Get user-friendly error message.

    Args:
        error: Exception to convert
        is_debug: Include debug info if True

    Returns:
        User-friendly error message
    """
    if isinstance(error, ValidationError):
        return str(error)

    if is_debug:
        return f"Error: {str(error)}"

    # Generic message for security
    return "An error occurred processing your request"
