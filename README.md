# AI Chatbot - Model Agnostic Learning Project

A full-stack AI chatbot application with streaming support, tool calling, and multiple LLM provider support (Claude, GPT, Ollama).

**Learning Goals:**
- Understand the full request/response cycle in AI applications
- Learn frontend-backend interaction patterns
- Implement streaming responses and real-time updates
- Build a model-agnostic system architecture
- Practice testing, validation, and secure coding patterns

## Project Structure

```
ai-chatbot/
├── frontend/              # Vite + React + TypeScript
├── backend/               # FastAPI + Python
├── docs/                  # Documentation
└── README.md             # This file
```

## Prerequisites

- **Node.js** (v18+) and npm
- **Python** (v3.10+)
- **Anthropic API Key** (for Claude models)

## Quick Start

### 1. Backend Setup

```bash
# Create and activate Python virtual environment
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env file and add your ANTHROPIC_API_KEY
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn app.main:app --reload
```

The backend will start at `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

The frontend will start at `http://localhost:5173`

### 4. Test the Application

Open your browser to `http://localhost:5173` and try:
- Type a math question: "What is 2 + 2?"
- Ask about weather: "What's the weather like?"
- Web search: "Latest news about AI"

## Architecture Overview

### Three-Layer Design

```
┌─ FRONTEND (React + TypeScript)
│  ├─ User input validation
│  ├─ Message history management
│  └─ SSE stream parsing + real-time updates

├─ API BRIDGE (HTTP + JSON)
│  ├─ Request: { messages, tools, system }
│  └─ Response: SSE stream with tokens + tool calls

└─ BACKEND (FastAPI + Python)
   ├─ LLM Provider abstraction
   ├─ Tool execution
   └─ Streaming response management
```

### Key Concepts

1. **Model Agnostic**: Switch between Claude, GPT, Ollama without changing frontend
2. **Tool Calling**: LLM can call tools (calculator, web search, weather)
3. **Streaming**: Tokens arrive in real-time, not waiting for full response
4. **Validation**: Both frontend (UX) and backend (security)
5. **Type Safety**: TypeScript + Pydantic for full type coverage

## Development Phases

### Phase 1: Project Setup ✅
- Project structure
- Dependencies
- Configuration

### Phase 2: Backend Foundation (In Progress)
- LLM provider abstraction
- Tool definitions
- Chat endpoint with streaming

### Phase 3: Tools Implementation
- Calculator tool
- Web search (DuckDuckGo)
- Weather tool (Open-Meteo)

### Phase 4: Frontend Foundation
- Chat UI components
- Request building
- State management

### Phase 5: Frontend Streaming
- SSE parsing
- Real-time text display
- Tool call handling

### Phase 6: Testing
- Unit tests (tools)
- Integration tests (endpoints)
- Component tests (UI)

### Phase 7: Polish & Documentation
- Input/output validation
- Rate limiting
- Error handling
- Security best practices

## Configuration

### Backend (.env)
```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
FRONTEND_URL=http://localhost:5173
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000/api
VITE_DEBUG=true
```

## API Endpoints

### Chat Completions (Streaming)
```
POST /api/chat/completions
```

Request:
```json
{
  "messages": [
    {"role": "user", "content": "What is 2+2?"}
  ],
  "tools": [...],
  "system": "You are a helpful assistant",
  "model": "claude-3-5-sonnet-20241022",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

Response: `text/event-stream` with SSE events
```
data: {"type": "content_block_start", "content_block": {"type": "text"}}
data: {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "The"}}
data: {"type": "message_stop"}
```

## Testing

### Run Backend Tests
```bash
cd backend
pytest tests/
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

## Key Learning Points

### Frontend
- React hooks (useState, useEffect)
- Async/await and fetch API
- SSE stream parsing
- TypeScript interfaces
- State management patterns

### Backend
- FastAPI routing and middleware
- Async Python patterns
- LLM abstraction & dependency injection
- Tool execution and error handling
- Streaming responses

### Full Stack
- Request/response cycle
- Real-time communication
- Tool calling pattern
- Type safety across boundaries
- Security & validation

## Security Practices

- ✅ Input validation (frontend + backend)
- ✅ API key in environment variables
- ✅ CORS properly configured
- ✅ Rate limiting
- ✅ Request timeouts
- ✅ Error sanitization

## Troubleshooting

### Backend won't start
- Check Python version: `python --version`
- Ensure virtual environment is activated
- Check ANTHROPIC_API_KEY in .env

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check VITE_API_URL in .env.local
- Check CORS settings in backend

### LLM API errors
- Verify ANTHROPIC_API_KEY is valid
- Check rate limits haven't been exceeded
- See backend logs for detailed errors

## References

- [Plan & Mental Model](./docs/MENTAL_MODEL.md)
- [Architecture Decisions](./docs/ARCHITECTURE.md)
- [API Specification](./docs/API_SPEC.md)

## Next Steps

1. ✅ Phase 1: Project Setup
2. → Phase 2: Implement LLM abstraction and chat endpoint
3. → Phase 3: Implement tools
4. → Phase 4-5: Build frontend and streaming
5. → Phase 6: Add tests
6. → Phase 7: Polish and document

---

Built as a learning project to understand AI application architecture.
