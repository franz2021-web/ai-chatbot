"""
LLM Service - Model agnostic abstraction for language models.
Supports NVIDIA, Anthropic Claude, OpenAI GPT, and Ollama models.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Optional, Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def stream_message(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system: str = "You are a helpful assistant.",
        model: str = "meta/llama-3.1-8b-instruct",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a message completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions
            system: System prompt
            model: Model name to use
            temperature: Temperature for generation
            max_tokens: Max tokens to generate

        Yields:
            Events with 'type' and related data
        """
        pass


class NVIDIAProvider(LLMProvider):
    """NVIDIA API provider using OpenAI-compatible interface."""

    def __init__(self, api_key: str, api_base: str, model: str):
        """Initialize with NVIDIA API credentials."""
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        logger.info(f"Initialized NVIDIA provider with model: {model}")

    async def stream_message(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system: str = "You are a helpful assistant.",
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream message from NVIDIA API using OpenAI-compatible interface."""
        try:
            from openai import OpenAI

            # Use provided model or fall back to default
            model_to_use = model or self.model

            # Initialize OpenAI client pointing to NVIDIA API
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )

            # Build messages list with system prompt
            messages_to_send = []
            if system:
                messages_to_send.append({"role": "system", "content": system})
            messages_to_send.extend(messages)

            logger.info(f"Streaming from NVIDIA ({model_to_use}) with {len(messages)} messages")

            # Call NVIDIA API with streaming
            stream = client.chat.completions.create(
                model=model_to_use,
                messages=messages_to_send,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                tools=tools if tools else None,
            )

            # Process streaming response
            for chunk in stream:
                # Skip if no choices (can happen at stream end)
                if not chunk.choices:
                    continue

                choice = chunk.choices[0]

                # Handle text content
                if choice.delta.content:
                    yield {
                        "type": "content_block_delta",
                        "delta": {
                            "type": "text_delta",
                            "text": choice.delta.content
                        }
                    }

                # Handle tool calls if present
                if hasattr(choice.delta, "tool_calls") and choice.delta.tool_calls:
                    for tool_call in choice.delta.tool_calls:
                        yield {
                            "type": "content_block_delta",
                            "delta": {
                                "type": "tool_use",
                                "id": tool_call.id,
                                "name": tool_call.function.name,
                                "input": tool_call.function.arguments
                            }
                        }

            # Signal completion
            yield {"type": "message_stop"}
            logger.info("NVIDIA stream completed successfully")

        except Exception as e:
            logger.error(f"NVIDIA API error: {str(e)}", exc_info=True)
            yield {
                "type": "error",
                "error": {
                    "type": "api_error",
                    "message": f"NVIDIA API error: {str(e)}"
                }
            }
            yield {"type": "message_stop"}


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str, model: str):
        """Initialize with API key."""
        self.api_key = api_key
        self.model = model
        logger.info(f"Initialized Anthropic provider with model: {model}")

    async def stream_message(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system: str = "You are a helpful assistant.",
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream message from Anthropic Claude."""
        # Implementation will be added in Phase 2
        logger.info("Streaming message from Anthropic Claude")

        # Placeholder
        yield {
            "type": "content_block_delta",
            "delta": {
                "type": "text_delta",
                "text": "[Anthropic API implementation pending]"
            }
        }
        yield {"type": "message_stop"}


class OpenAIProvider(LLMProvider):
    """OpenAI GPT API provider."""

    def __init__(self, api_key: str, model: str):
        """Initialize with API key."""
        self.api_key = api_key
        self.model = model
        logger.info(f"Initialized OpenAI provider with model: {model}")

    async def stream_message(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system: str = "You are a helpful assistant.",
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream message from OpenAI GPT."""
        # Implementation will be added in Phase 2
        logger.info("Streaming message from OpenAI")

        # Placeholder
        yield {
            "type": "content_block_delta",
            "delta": {
                "type": "text_delta",
                "text": "[OpenAI API implementation pending]"
            }
        }
        yield {"type": "message_stop"}


class OllamaProvider(LLMProvider):
    """Local Ollama model provider."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """Initialize with Ollama base URL."""
        self.base_url = base_url
        self.model = model
        logger.info(f"Initialized Ollama provider with model: {model}")

    async def stream_message(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system: str = "You are a helpful assistant.",
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream message from Ollama."""
        # Implementation will be added in Phase 2
        logger.info(f"Streaming message from Ollama ({self.model})")

        # Placeholder
        yield {
            "type": "content_block_delta",
            "delta": {
                "type": "text_delta",
                "text": "[Ollama API implementation pending]"
            }
        }
        yield {"type": "message_stop"}


def get_llm_provider() -> LLMProvider:
    """
    Get LLM provider based on configuration.

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider is unknown or API key is missing
    """
    provider_name = settings.llm_provider.lower()

    if provider_name == "nvidia":
        if not settings.nvidia_api_key:
            raise ValueError("NVIDIA_API_KEY not set in environment")
        return NVIDIAProvider(
            api_key=settings.nvidia_api_key,
            api_base=settings.nvidia_api_base,
            model=settings.nvidia_model
        )

    elif provider_name == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model
        )

    elif provider_name == "openai":
        raise NotImplementedError("OpenAI provider not yet fully configured")

    elif provider_name == "ollama":
        return OllamaProvider(model="llama2")

    else:
        raise ValueError(
            f"Unknown LLM provider: {provider_name}. "
            f"Must be one of: nvidia, anthropic, openai, ollama"
        )
