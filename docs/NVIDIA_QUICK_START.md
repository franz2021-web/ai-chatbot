# NVIDIA API Quick Start (5 Minutes)

## What Changed

Your project is now configured for **NVIDIA API (free)** instead of Anthropic.

```
Before: LLM_PROVIDER=anthropic
After:  LLM_PROVIDER=nvidia
```

All the code still works the same way - just using a different API under the hood.

---

## Step 1: Get Your API Key (2 minutes)

1. Go to: https://build.nvidia.com/
2. Sign up (free, no credit card)
3. Click "API Keys" or go to your dashboard
4. Create a new key for "Inference" or "NIM"
5. Copy the key (you'll need it in the next step)

**Your key should look like:** `nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Step 2: Add to Your .env File (1 minute)

Open `backend/.env` and find this line:

```bash
NVIDIA_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual key:

```bash
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**That's it!** You're configured.

---

## Step 3: Verify It Works (2 minutes)

### Test 1: Backend Can Start

```bash
cd backend
python -c "from app.config import settings; print(f'Provider: {settings.llm_provider}'); print(f'Model: {settings.nvidia_model}')"
```

Should output:
```
Provider: nvidia
Model: meta/llama-3.1-8b-instruct
```

### Test 2: API Key Works

```bash
curl -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta/llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 100
  }'
```

Replace `YOUR_API_KEY_HERE` with your actual key.

Should return something like:
```json
{
  "choices": [
    {
      "message": {
        "content": "Hello! How can I help you today?"
      }
    }
  ]
}
```

If you get an error like `401 Unauthorized`, check:
- ✅ Key is correct (copy-paste carefully)
- ✅ Key is for NVIDIA (not something else)
- ✅ No extra spaces or quotes

---

## What's Updated in the Project

### Changed Files:
```
✅ backend/.env                    - Added NVIDIA config, kept Anthropic as backup
✅ backend/app/config.py           - Added NVIDIA_API_KEY, NVIDIA_MODEL, NVIDIA_API_BASE
✅ backend/requirements.txt         - Added "openai==1.3.0" (for OpenAI-compatible API)
✅ backend/app/services/llm_service.py - Added NVIDIAProvider class
```

### What Stays the Same:
```
✅ Frontend code - No changes needed
✅ Tool definitions - No changes needed
✅ Request/response format - No changes needed
✅ FastAPI routes - No changes needed
```

**The beauty of abstraction:** Change the provider, rest of the code stays the same.

---

## Next: Phase 2 Implementation

When ready for Phase 2, we'll:

1. ✅ Implement `NVIDIAProvider.stream_message()`
2. ✅ Use OpenAI SDK to call NVIDIA
3. ✅ Handle streaming SSE responses
4. ✅ Support function calling (tools)
5. ✅ Add error handling

But the architecture stays clean and model-agnostic.

---

## Switching Providers Later

Want to try Anthropic Claude instead?

```bash
# In .env, change:
LLM_PROVIDER=nvidia
# to:
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

That's it. Code doesn't change. This is why abstraction matters!

---

## Troubleshooting

### Problem: "401 Unauthorized"
**Solution:**
- Check your API key is correct
- Make sure you copied the entire key (including `nvapi-` prefix)
- No extra spaces before/after
- Generate a new key if unsure

### Problem: "Model not found"
**Solution:**
- Check model name is correct: `meta/llama-3.1-8b-instruct`
- Visit https://build.nvidia.com/ to see available models
- Some models might not be available in your region

### Problem: "Rate limit exceeded"
**Solution:**
- NVIDIA free tier has limits (fine for learning)
- Phase 7 will add rate limiting middleware
- For now, just wait a minute and retry

### Problem: Python can't import openai
**Solution:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## Cost Analysis

```
Project Cost Breakdown:
├─ NVIDIA API: FREE ✅
├─ DuckDuckGo search: FREE ✅
├─ Open-Meteo weather: FREE ✅
└─ Total: $0

vs Original Plan with Anthropic:
├─ Anthropic: ~$5 initial credit ❌
├─ DuckDuckGo: FREE ✅
├─ Open-Meteo: FREE ✅
└─ Total: ~$5
```

You're saving $5 by using NVIDIA! 🎉

---

## You're All Set!

Next steps:

1. ✅ Get NVIDIA API key (done in 2 min)
2. ✅ Add to `.env` (done in 1 min)
3. ✅ Verify with curl (optional, 2 min)
4. ⏳ Proceed to Phase 2 when ready

When you're ready to start Phase 2:
- We'll implement the actual API calls
- You'll see your first working request cycle
- Tokens will stream in real-time
- It's going to be exciting! 🚀

---

## Remember

**Your learning goal:** Understand the request cycle deeply.

**Why NVIDIA is perfect for this:**
- ✅ Free (no financial barrier to learning)
- ✅ Works great for demos (perfect for learning)
- ✅ OpenAI-compatible (industry-standard format)
- ✅ Clear documentation
- ✅ You'll understand the FULL stack

Let's build something amazing! 

**Next phase starts when you have your API key configured.** You ready? 🚀

