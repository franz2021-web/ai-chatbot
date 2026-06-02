# NVIDIA API Setup Guide

## NVIDIA API Overview

NVIDIA provides free access to their AI models via their inference service. This is perfect for learning because:

✅ **Genuinely free** (no credit card required)
✅ **Multiple models** (LLaMA, Mistral, etc.)
✅ **Supports function calling** (tool use)
✅ **Streaming support** (real-time tokens)
✅ **Great for learning** (good documentation)

---

## Step 1: Get Your API Key

### Method 1: NVIDIA API Catalog (Recommended)

1. Visit: https://build.nvidia.com/
2. Sign up (free account)
3. Navigate to "Playground" or "API Keys"
4. Create a new API key
5. Copy the key (you'll need it in `.env`)

### Method 2: NVIDIA Cloud Services

If Method 1 doesn't work:
1. Visit: https://www.nvidia.com/en-us/ai-data-science/generative-ai/api/
2. Sign up for their API service
3. Generate API key from dashboard

---

## Step 2: Choose Your Model

NVIDIA offers several free models. Best options for our use case:

### Recommended: Meta Llama 3.1 8B Instruct
```
Model ID: meta/llama-3.1-8b-instruct
Capabilities: ✅ Streaming, ✅ Function calling, ✅ Good quality
Latency: ~2-5 seconds per response
Use case: Perfect for learning
```

### Alternative: Mistral 7B Instruct
```
Model ID: mistralai/mistral-7b-instruct-v0.2
Capabilities: ✅ Streaming, ✅ Function calling, ✅ Fast
Latency: ~1-3 seconds per response
Use case: Faster, still good quality
```

### Alternative: Mixtral 8x7B
```
Model ID: mistralai/mixtral-8x7b-instruct-v0.1
Capabilities: ✅ Streaming, ✅ Function calling, ✅ Best quality
Latency: ~3-5 seconds per response
Use case: Highest quality
```

**Recommendation:** Start with **Meta Llama 3.1 8B** (great balance)

---

## Step 3: Update Backend Configuration

### Update `backend/.env`

Replace the Anthropic configuration with NVIDIA:

```bash
# NVIDIA Configuration
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=your_api_key_here
NVIDIA_MODEL=meta/llama-3.1-8b-instruct

# Keep other settings
HOST=127.0.0.1
PORT=8000
DEBUG=True
FRONTEND_URL=http://localhost:5173
RATE_LIMIT_PER_MINUTE=60
REQUEST_TIMEOUT_SECONDS=30
TOOL_TIMEOUT_SECONDS=15
DUCKDUCKGO_MAX_RESULTS=5
WEATHER_API_BASE=https://api.open-meteo.com/v1
```

### Update `backend/app/config.py`

Add NVIDIA settings:

```python
# Add these fields to Settings class:

# NVIDIA Configuration
nvidia_api_key: str = Field(default="", env="NVIDIA_API_KEY")
nvidia_model: str = Field(default="meta/llama-3.1-8b-instruct", env="NVIDIA_MODEL")
nvidia_api_base: str = Field(
    default="https://integrate.api.nvidia.com/v1",
    env="NVIDIA_API_BASE"
)
```

---

## Step 4: Implementation Details

### API Endpoint Structure

NVIDIA uses OpenAI-compatible API format:

```python
# Request format (OpenAI compatible)
POST https://integrate.api.nvidia.com/v1/chat/completions

Headers:
- Authorization: Bearer YOUR_API_KEY
- Content-Type: application/json

Body:
{
    "model": "meta/llama-3.1-8b-instruct",
    "messages": [
        {"role": "user", "content": "What is 2+2?"}
    ],
    "temperature": 0.7,
    "max_tokens": 2048,
    "stream": true  # For streaming
}

Response (streaming):
data: {"choices": [{"delta": {"content": "The"}}]}
data: {"choices": [{"delta": {"content": " answer"}}]}
...
```

### Tool/Function Calling Format

NVIDIA supports OpenAI-compatible function calling:

```python
# Define tools
"tools": [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression"
                    }
                }
            }
        }
    }
]

# Model response with tool call
{
    "choices": [{
        "message": {
            "tool_calls": [{
                "id": "call_123",
                "function": {
                    "name": "calculator",
                    "arguments": "{\"expression\": \"2+2\"}"
                }
            }]
        }
    }]
}
```

---

## Step 5: Python SDK Options

### Option 1: OpenAI SDK (Recommended)
```bash
pip install openai
```

Since NVIDIA is OpenAI-compatible, you can use the OpenAI SDK:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=settings.nvidia_api_key,
    base_url=settings.nvidia_api_base
)

stream = await client.chat.completions.create(
    model=settings.nvidia_model,
    messages=messages,
    stream=True,
    tools=tools
)

async for chunk in stream:
    # Process streaming chunks
    pass
```

### Option 2: Direct HTTP (If you want to see details)
```bash
pip install httpx  # Already have this
```

```python
async with httpx.AsyncClient() as client:
    async with client.stream(
        "POST",
        f"{settings.nvidia_api_base}/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.nvidia_api_key}",
        },
        json={...}
    ) as response:
        async for line in response.aiter_lines():
            # Process SSE line
            pass
```

**Recommendation:** Use OpenAI SDK for simplicity

---

## Step 6: Update requirements.txt

Add NVIDIA/OpenAI SDK:

```txt
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
httpx==0.25.1
openai==1.3.0  # ← Add this (OpenAI SDK, works with NVIDIA)
pydantic==2.5.0
pydantic-settings==2.1.0  # ← Make sure this is included
pytest==7.4.3
pytest-asyncio==0.21.1
aiohttp==3.9.1
```

---

## Known Limitations & Solutions

### Limitation 1: Rate Limiting
**Issue:** NVIDIA free tier has rate limits
**Solution:** Built into Phase 7 (we'll add rate limiting middleware)

### Limitation 2: Model Quality vs Speed
**Issue:** Llama 3.1 8B is less powerful than Claude
**Solution:** Perfect for learning, will work fine for demo

### Limitation 3: Streaming Latency
**Issue:** First token takes 2-3 seconds
**Solution:** Normal for free tier, acceptable for learning

### Limitation 4: Tool Calling Edge Cases
**Issue:** Different models handle tools differently
**Solution:** We'll add validation in Phase 3

---

## Verification Checklist

Before starting Phase 2, verify:

```bash
# 1. API Key Works
curl -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta/llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 100
  }'

# Should return: {"choices": [{"message": {"content": "Hello..."}}]}

# 2. Streaming Works
curl -N -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta/llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "Count: 1"}],
    "stream": true,
    "max_tokens": 100
  }'

# Should return: data: {"choices": [{"delta": {"content": "..."}}]}
```

---

## Implementation Plan for Phase 2

With NVIDIA API, Phase 2 will:

1. **Add NVIDIAProvider class** to `services/llm_service.py`
2. **Use OpenAI SDK** for API calls
3. **Handle streaming responses** via SSE events
4. **Support function calling** for tools
5. **Add error handling** for rate limits

**Key difference from Anthropic:**
- Use `openai.AsyncOpenAI` instead of `anthropic.Anthropic`
- Format tools as OpenAI-style "functions"
- Handle `tool_calls` instead of `tool_use`

---

## Cost Analysis

**Your cost for the full project:**

```
Phase 1-7 with NVIDIA API:
├─ NVIDIA API: FREE ✅
├─ No paid APIs needed
├─ DuckDuckGo: FREE ✅
├─ Open-Meteo: FREE ✅
└─ Total cost: $0

Total time: 20-25 hours
Learning depth: 9/10
```

---

## Gotchas to Watch

1. **API Key Scope:** Make sure key has access to inference
2. **Rate Limits:** Free tier is limited (but fine for learning)
3. **Model Availability:** Llama 3.1 8B is stable, but stay updated
4. **Streaming Format:** SSE format is slightly different from Anthropic
5. **Tool Calling:** Format matches OpenAI, not Anthropic

---

## Next Steps

1. ✅ Get NVIDIA API key (5 minutes)
2. ✅ Test API with curl (5 minutes)
3. ✅ Update `.env` with your key
4. ⏳ Phase 2: Implement NVIDIAProvider class

Then you'll see:
- Real API calls to NVIDIA
- Actual streaming responses
- Tokens arriving in real-time
- Full request/response cycle working

---

## Resources

- **NVIDIA AI Playground:** https://build.nvidia.com/
- **NVIDIA API Docs:** https://docs.api.nvidia.com/
- **OpenAI SDK Docs:** https://platform.openai.com/docs/
- **Function Calling Guide:** https://docs.api.nvidia.com/nim/openai-api/#function-calling

---

## Questions?

If anything is unclear:
- ✅ Check the docs above
- ✅ Test the curl commands
- ✅ Come back with specific errors
- ✅ We'll debug together in Phase 2

You're ready to proceed once you have your API key! 🚀

