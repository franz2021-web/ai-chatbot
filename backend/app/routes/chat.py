"""
Chat endpoint route.
Handles streaming chat completion requests.
"""

import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest
from app.services.llm_service import get_llm_provider
from app.services.tool_executor import get_executor

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/tools")
async def get_tools():
    """
    Get available tools for the chat API.

    Returns:
        List of tool definitions in OpenAI format
    """
    executor = get_executor()
    return {
        "tools": executor.get_tool_definitions()
    }


@router.post("/chat/completions")
async def chat_completions(request: ChatRequest):
    """
    Stream chat completions.

    Args:
        request: ChatRequest with messages, tools, system prompt, etc.

    Returns:
        StreamingResponse with SSE-formatted events
    """
    try:
        # Get the LLM provider (will be implemented in Phase 2)
        llm_provider = get_llm_provider()

        async def event_generator():
            """Generate SSE events from LLM stream."""
            try:
                # Call LLM provider and stream results
                async for event in llm_provider.stream_message(
                    messages=request.messages,
                    tools=request.tools,
                    system=request.system,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                ):
                    # Send event to frontend
                    yield f"data: {json.dumps(event)}\n\n"

            except Exception as e:
                logger.error(f"Error in chat stream: {str(e)}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'message': 'An error occurred'})}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
