# Mental Model: Navigating the AI Chatbot Project

## The Core Metaphor

**Think of this application like a restaurant:**

```
CUSTOMER (Frontend)
    ↓
    Places order: "2 eggs, scrambled, toast"
    (sends ChatRequest with messages, tools, system)
    ↓
WAITER (Backend)
    ↓
    Takes order to kitchen
    (routes/chat.py receives request)
    ↓
CHEF (LLM Provider)
    ↓
    Cooks the meal (calls LLM API)
    ↓
    Shouts back: "Eggs!", "Toast!", "Done!"
    (yields SSE events)
    ↓
WAITER (Backend)
    ↓
    Brings each plate to table immediately
    (yields events one at a time)
    ↓
CUSTOMER (Frontend)
    ↓
    Sees food appearing on table
    (displays tokens in real-time)
```

### Why This Metaphor?

- **Frontend = Customer**: Initiates request, waits for response, displays results
- **Backend = Waiter**: Takes request, coordinates with chef, streams results
- **LLM = Chef**: Does the actual work (thinking, generating)
- **Streaming = Serving course by course**: Not waiting for entire meal before eating

---

## The Triangle of Concerns

All decisions in this project involve **three competing goals**:

```
          ╱╲
         ╱  ╲
        ╱ F1 ╲      F1 = Learn about request cycles
       ╱──────╲
      ╱  F2    ╲    F2 = Build something that works
     ╱──────────╲
    ╱    F3      ╲  F3 = Use latest best practices
   ╱──────────────╲
```

**When we make a choice, we optimize for TWO and compromise on ONE:**

```
Phase 1-2: LEARNING + WORKING (sacrifice some practices)
  → Skip rate limiting (learn the basics first)
  → Skip some error handling (focus on happy path)
  → Skip tests initially (build first)

Phase 5-6: LEARNING + PRACTICES (sacrifice some simplicity)
  → Add comprehensive error handling
  → Add tests
  → Refactor code

Phase 7: WORKING + PRACTICES (sacrifice learning time)
  → Polish everything
  → Make it production-ready
  → Document thoroughly
```

**This is intentional.** You can't optimize for all three simultaneously.

---

## The Skill Ladder

Imagine climbing a ladder. Each rung has a prerequisite skill:

```
     RUNG 7: Production-Ready Code
             (rate limiting, security, monitoring)
             Requires: Rung 6 complete
             Skill: Advanced DevOps thinking

     RUNG 6: Testing & Validation
             (pytest, Vitest, error scenarios)
             Requires: Rung 5 complete
             Skill: Testing mindset

     RUNG 5: ⭐ Streaming (THE HARD PART)
             (SSE parsing, async iteration, real-time)
             Requires: Rung 4 complete
             Skill: Advanced JavaScript/async

     RUNG 4: Frontend Basics
             (React hooks, state management, events)
             Requires: Rung 3 complete
             Skill: React intermediate

     RUNG 3: Backend Tools
             (async functions, API integration, error handling)
             Requires: Rung 2 complete
             Skill: Backend basics

     RUNG 2: ⭐ Streaming Backend
             (async generators, SSE format, event streaming)
             Requires: Rung 1 complete
             Skill: Async Python intermediate

     RUNG 1: Project Setup
             (file creation, installation, configuration)
             Requires: Nothing!
             Skill: Beginner CLI
```

**⭐ = Places where you'll learn the most**

---

## The Request/Response Dance

Every interaction follows this pattern:

```
TIME → (increases downward)

T0:   Frontend: User types "What is 2+2?"
      State: inputValue = "What is 2+2?"

T1:   User clicks Send
      Frontend: Builds ChatRequest object
      Frontend: Disables send button (UX feedback)

T2:   Frontend: fetch POST /api/chat/completions
      (Request travels across network ~100ms)

T3:   Backend: routes/chat.py receives request
      Backend: ChatRequest validated by Pydantic
      (If invalid: 422 Unprocessable Entity, done)

T4:   Backend: Calls get_llm_provider()
      Backend: Returns AnthropicProvider instance

T5:   Backend: Calls llm_provider.stream_message()
      Backend: Anthropic SDK makes API call to Claude

T6:   Claude AI: Processes request
      Claude: Generates tokens one by one

T7:   Backend: Receives first token
      Backend: Wraps in SSE format
      Backend: Yields to event_generator()

T8:   Frontend: getReader() receives first chunk
      Frontend: Parses SSE line
      Frontend: Extracts text token
      Frontend: Updates assistantMessage state
      Frontend: React re-renders

T9:   User sees: "T" appears in chat (just one character!)

T10:  Backend: Generates next token
      (Repeat T7-T9 many times)

T20:  Backend: No more tokens, yield message_stop event
      Frontend: Parser sees message_stop
      Frontend: Marks message as complete

T21:  Frontend: Re-enables send button
      Frontend: Ready for next message
      User: Sees complete response "The answer is 4"
```

**Key insight:** The "dance" happens THOUSANDS of times per second.
Each token is wrapped, sent, received, parsed, displayed.

---

## Code Navigation Flowchart

When you're confused about what happens when:

```
START: "User sends message"
│
├─ Where in code? → frontend/src/hooks/useChat.ts
│
├─ What function? → handleSendMessage()
│
├─ What does it do?
│  ├─ Validate input
│  ├─ Build ChatRequest
│  ├─ Call fetch POST /api/chat/completions
│  └─ Handle streaming response
│
├─ Response arrives as stream
│
├─ Where does it go? → frontend/src/hooks/useStreamParser.ts
│
├─ What function? → parseSSEStream()
│
├─ What does it do?
│  ├─ Read bytes from stream
│  ├─ Parse SSE format
│  ├─ Extract JSON events
│  └─ Update React state
│
├─ State updates
│
├─ Where does it display? → frontend/src/components/ChatInterface.tsx
│
├─ What renders?
│  ├─ Messages from state
│  ├─ Text appears token by token
│  └─ Tool calls show as they execute
│
└─ User sees result
```

---

## The Four Types of Code in This Project

### Type 1: Configuration Code
**Purpose:** Set up the environment  
**Examples:** `config.py`, `.env`, `vite.config.ts`  
**Skill Level:** Beginner  
**What it teaches:** How to make code configurable  
**When to modify:** When you need to add settings

```python
# Example: config.py loads from .env
ANTHROPIC_API_KEY=settings.anthropic_api_key
# Now you can use: settings.anthropic_api_key anywhere
```

### Type 2: Schema Code
**Purpose:** Define what data looks like  
**Examples:** `schemas.py`, TypeScript interfaces  
**Skill Level:** Beginner-Intermediate  
**What it teaches:** Type safety across boundaries  
**When to modify:** When adding new data structures

```python
# Example: ChatRequest defines request structure
class ChatRequest(BaseModel):
    messages: List[MessageDict]
    tools: Optional[List[ToolSchema]]
    # FastAPI automatically validates incoming JSON against this
```

### Type 3: Logic Code
**Purpose:** Do actual work  
**Examples:** `llm_service.py`, `useChat.ts`, `tools/calculator.py`  
**Skill Level:** Intermediate-Advanced  
**What it teaches:** How to coordinate systems  
**When to modify:** When implementing features

```python
# Example: llm_service.py calls external APIs
async def stream_message(...):
    async for event in llm.stream(...):  # Async iteration
        yield event  # Stream to frontend
```

### Type 4: Integration Code
**Purpose:** Connect pieces together  
**Examples:** `routes/chat.py`, `useStreamParser.ts`  
**Skill Level:** Advanced  
**What it teaches:** How systems work together  
**When to modify:** When debugging or refactoring

```python
# Example: chat.py connects request → LLM → response
async def event_generator():
    async for event in llm_provider.stream_message(...):
        yield f"data: {json.dumps(event)}\n\n"
```

---

## Common Confusion Points (And Their Answers)

### Confusion 1: "Why is everything async?"

**What you see:**
```python
async def stream_message(...):
async for event in ...
await ...
```

**What it means:**
```
"This function takes a long time (network call).
 Don't block everything waiting for it.
 Let other requests happen meanwhile.
 When it's done, come back and continue."
```

**Why it matters:**
- Without async: 1 user = 1 second wait = 1 request per second max
- With async: 100 users = 1 second wait = 100 requests per second

### Confusion 2: "What's an AsyncGenerator?"

**What you see:**
```python
async def stream_message(...) -> AsyncGenerator[Dict, None]:
    async for event in stream:
        yield event
```

**What it means:**
```
"This function returns multiple values over time.
 Not all at once.
 One value per 'next()' call.
 And it's async (slow) values."
```

**Real-world analogy:**
- Normal function: return [1, 2, 3] (all at once)
- Generator: yield 1, yield 2, yield 3 (one at a time)
- AsyncGenerator: yield 1 (wait), yield 2 (wait), yield 3 (wait)

### Confusion 3: "What's SSE (Server-Sent Events)?"

**What you see:**
```python
return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**What it means:**
```
"Instead of returning a single response,
 Keep the connection open.
 Send events one at a time.
 Frontend reads them as they arrive."
```

**Format:**
```
data: {"type": "...", "delta": {...}}
[blank line]
data: {"type": "...", "delta": {...}}
[blank line]
```

**Why:**
- Normal HTTP: Wait for everything, get it all, close connection
- SSE: Open connection, send events forever, frontend consumes live

### Confusion 4: "Why do we need a Tool Executor?"

**What you see:**
```python
async def execute_tool(tool_name, tool_input):
    if tool_name == "calculator":
        return calculate(tool_input)
    elif tool_name == "web_search":
        return search_web(tool_input)
```

**What it means:**
```
"LLM says 'I need calculator tool'.
 We look up which tool that is.
 We execute it.
 We give results back to LLM."
```

**Why:**
```
LLM ← "Here are your tools:" (tool definitions)
  ↓
LLM thinks about problem
  ↓
LLM → "I choose calculator(2+2)"
  ↓
Executor: "What's 'calculator'? Ah, the calculate function"
  ↓
Executor: Runs calculate("2+2")
  ↓
Executor → LLM: "Result is 4"
  ↓
LLM → Frontend: "The answer is 4"
```

---

## The Learning Path Visualization

```
Your Journey Through This Project:

        RUNG 7
        ┌──┐
        │██│ Polish
        │██│ Security
        │██│ Documentation
        └──┘
          ▲
        RUNG 6
        ┌──┐
        │  │ Testing
        │  │ Error handling
        │  │ Validation
        └──┘
          ▲
        RUNG 5 ⭐⭐⭐ (Hardest!)
        ┌──┐
        │  │ Frontend Streaming
        │  │ SSE parsing
        │  │ Real-time updates
        └──┘
          ▲
        RUNG 4
        ┌──┐
        │  │ Frontend Foundation
        │  │ React hooks
        │  │ State management
        └──┘
          ▲
        RUNG 3
        ┌──┐
        │  │ Backend Tools
        │  │ Async functions
        │  │ API integration
        └──┘
          ▲
        RUNG 2 ⭐⭐ (Also hard!)
        ┌──┐
        │  │ Backend LLM
        │  │ Async generators
        │  │ Streaming
        └──┘
          ▲
        RUNG 1
        ┌──┐
        │██│ Project Setup ← YOU ARE HERE
        │██│ Installation
        │██│ Configuration
        └──┘

Time to complete all: ~20-25 hours of focused work

Hard parts:
- RUNG 2: Understanding async/await and generators
- RUNG 5: Understanding stream parsing and real-time updates

Easy parts:
- RUNG 1: Just following instructions
- RUNG 3: Similar patterns to RUNG 2, just different code
- RUNG 6: If you understand the code, tests are straightforward
- RUNG 7: Building on what you know
```

---

## Quick Reference: File Purposes

```
BACKEND CONFIG:
├── .env                    What? Settings
├── app/config.py           What? Load .env into Python

BACKEND STRUCTURE:
├── app/main.py             What? FastAPI app entry point
├── app/models/schemas.py   What? Pydantic validation schemas
├── app/routes/chat.py      What? /api/chat endpoint
├── app/services/llm_service.py     What? LLM provider abstraction
├── app/services/tool_executor.py   What? Execute tools by name
├── app/tools/calculator.py What? Do math
├── app/tools/web_search.py What? Search web
└── app/tools/weather.py    What? Get weather

FRONTEND STRUCTURE:
├── .env.local              What? API URL, debug mode
├── src/App.tsx             What? Main component
├── src/hooks/useChat.ts    What? Chat logic (Phase 4)
├── src/hooks/useStreamParser.ts What? Parse SSE (Phase 5)
├── src/components/ChatInterface.tsx What? Main UI (Phase 4)
└── src/utils/validation.ts What? Input validation (Phase 4)
```

---

## The "Why It's Designed This Way" Cheat Sheet

| Design Choice | Why? | Benefit |
|---------------|------|---------|
| LLMProvider ABC | Multiple LLM providers | Swap Claude → GPT → Ollama easily |
| Tool Executor | Tools are plugins | Add new tools without touching core |
| Pydantic schemas | Type-safe requests | Catch errors early, good errors |
| Async/await | Non-blocking I/O | Handle 100s of users simultaneously |
| SSE streaming | Real-time feel | Users see tokens appearing live |
| Frontend hooks | Separation of concerns | Logic separate from UI |
| Environment config | Secrets not in code | Safe to commit, flexible per environment |
| FastAPI | Modern, auto-docs | Easy to understand, built-in validation |
| React components | Reusable UI | Message, Tool, Input are components |

---

## When You Get Stuck

### Stuck on Backend?

1. **Check the logs first**
   ```bash
   # You should see detailed error messages
   python -m uvicorn app.main:app --reload
   ```

2. **Follow the request flow**
   ```
   routes/chat.py → services/llm_service.py → Anthropic SDK
   Where did it fail? Check that file.
   ```

3. **Check the Pydantic error**
   ```
   If 422 error: Your request doesn't match ChatRequest schema
   If other error: Look at stack trace
   ```

### Stuck on Frontend?

1. **Open browser DevTools (F12)**
   ```
   Console tab: JavaScript errors
   Network tab: HTTP requests and responses
   ```

2. **Follow the component flow**
   ```
   ChatInterface.tsx → useChat.ts → fetch → useStreamParser.ts → setState
   Where did it fail?
   ```

3. **Check the network response**
   ```
   Open Network tab, click on chat request
   See what the backend actually returned
   ```

### Stuck on Streaming?

This is the hardest part. The approach:

1. **Get backend streaming working FIRST**
   ```
   Verify curl can read SSE stream
   curl -N http://localhost:8000/api/chat/completions
   ```

2. **Then add frontend parsing**
   ```
   One event type at a time
   First: text_delta
   Then: tool_use
   Then: message_stop
   ```

3. **Debug with console.log**
   ```typescript
   console.log("Received event:", event)
   console.log("Parsed event:", JSON.parse(line))
   ```

---

## The Golden Rules

1. **Understand the request first, response second**
   - Request: What data goes to backend?
   - Response: What data comes back?

2. **When confused, print everything**
   ```python
   # Backend
   logger.info(f"Received: {request}")
   
   # Frontend
   console.log("Event:", event)
   ```

3. **Test the happy path first, errors second**
   - Happy path: It works
   - Error path: It handles failures

4. **Phases are sequential, not optional**
   - Phase 1 → Phase 2 → Phase 3 ...
   - Each builds on the previous

5. **"It's broken" is not a question**
   - "When I send a message, the backend returns 500" is helpful
   - Check logs, narrow down exactly where it fails

---

## You've Got This

Remember: **Every expert programmer was once confused about async, streaming, and state management.**

The fact that you're reading this and thinking about the mental model means you're already ahead.

Next steps:
1. Read docs/CODE_AUDIT.md for best practices
2. Review the project structure
3. When ready, proceed to Phase 2: Backend Implementation
4. Take it slow, one file at a time
5. Ask questions when stuck (check logs first!)

Good luck! 🚀

