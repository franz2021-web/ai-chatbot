/**
 * Shared types for the AI Chatbot frontend
 */

export interface Message {
  role: "user" | "assistant";
  content: string;
  id?: string;
  timestamp?: Date;
}

export interface ToolCall {
  id: string;
  name: string;
  input: Record<string, unknown>;
}

export interface ToolResult {
  tool_use_id: string;
  content: string;
}

export interface ToolCallDisplay {
  id: string;
  name: string;
  input: Record<string, unknown>;
  status: "pending" | "executing" | "completed" | "error";
  result?: unknown;
  error?: string;
}

export interface StreamEvent {
  type:
    | "content_block_start"
    | "content_block_delta"
    | "content_block_stop"
    | "message_start"
    | "message_stop"
    | "error";
  delta?: {
    type?: "text_delta" | "tool_use";
    text?: string;
    id?: string;
    name?: string;
    input?: string;
  };
  error?: {
    type: string;
    message: string;
  };
}

export interface ChatRequest {
  messages: Message[];
  tools?: ToolDefinition[];
  system?: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface ToolDefinition {
  type: string;
  function?: {
    name: string;
    description: string;
    parameters: {
      type: string;
      properties: Record<string, unknown>;
      required?: string[];
    };
  };
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  currentStreamingMessage: string;
}
