"""
Pydantic models for request/response validation.
"""

from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field, field_validator


class MessageDict(BaseModel):
    """A message in the conversation."""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate that role is one of the allowed values."""
        if v not in ['user', 'assistant', 'system']:
            raise ValueError(f"Invalid role: {v}. Must be 'user', 'assistant', or 'system'")
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not empty and not too long."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        if len(v) > 50000:
            raise ValueError("Message content too long (max 50000 characters)")
        return v


class ToolSchema(BaseModel):
    """Tool schema definition."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    input_schema: Dict[str, Any] = Field(..., description="Tool input JSON schema")


class ChatRequest(BaseModel):
    """Chat completion request."""
    messages: List[MessageDict] = Field(..., min_items=1, max_items=100)
    tools: Optional[List[ToolSchema]] = Field(default=None, description="Available tools")
    system: str = Field(default="You are a helpful assistant.", max_length=10000)
    model: str = Field(default="claude-3-5-sonnet-20241022")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=2048, ge=100, le=4096)

    @field_validator('system')
    @classmethod
    def validate_system(cls, v: str) -> str:
        """Validate system prompt."""
        if not v.strip():
            raise ValueError("System prompt cannot be empty")
        return v.strip()

    @field_validator('messages')
    @classmethod
    def validate_messages(cls, v: List[MessageDict]) -> List[MessageDict]:
        """Validate messages list."""
        if len(v) == 0:
            raise ValueError("Must provide at least one message")
        return v


class StreamEvent(BaseModel):
    """A streaming event from the LLM."""
    type: str = Field(..., description="Event type: content_block_start, content_block_delta, content_block_stop, message_stop, error")
    delta: Optional[Dict[str, Any]] = Field(None, description="Delta data for text or tool input")
    content_block: Optional[Dict[str, Any]] = Field(None, description="Content block data")


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
