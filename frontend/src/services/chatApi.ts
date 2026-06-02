/**
 * Chat API client - Handles communication with backend
 */

import { StreamEvent, ChatRequest, Message } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export class ChatApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ChatApiError";
  }
}

/**
 * Stream chat completions from the backend
 * Yields SSE events as they arrive
 */
export async function* streamChatCompletion(
  request: ChatRequest
): AsyncGenerator<StreamEvent> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ChatApiError(
        response.status,
        errorData.error || `HTTP ${response.status}`
      );
    }

    if (!response.body) {
      throw new Error("No response body");
    }

    // Parse SSE stream
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE events
        const lines = buffer.split("\n");

        // Keep the last incomplete line in the buffer
        buffer = lines[lines.length - 1];

        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i];

          // Skip empty lines and comments
          if (!line || line.startsWith(":")) continue;

          // Parse SSE event
          if (line.startsWith("data: ")) {
            const data = line.slice(6);

            if (data === "[DONE]") {
              continue;
            }

            try {
              const event = JSON.parse(data) as StreamEvent;
              yield event;
            } catch (e) {
              console.error("Failed to parse SSE event:", data, e);
            }
          }
        }
      }

      // Process remaining buffer
      if (buffer.startsWith("data: ")) {
        const data = buffer.slice(6);
        if (data !== "[DONE]") {
          try {
            const event = JSON.parse(data) as StreamEvent;
            yield event;
          } catch (e) {
            console.error("Failed to parse final SSE event:", data, e);
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  } catch (error) {
    if (error instanceof ChatApiError) {
      throw error;
    }

    throw new ChatApiError(
      0,
      error instanceof Error ? error.message : "Unknown error"
    );
  }
}

/**
 * Send a chat message and get a streamed response
 */
export async function* chatMessage(
  messages: Message[],
  system?: string
): AsyncGenerator<StreamEvent> {
  const request: ChatRequest = {
    messages,
    system: system || "You are a helpful assistant.",
    temperature: 0.7,
    max_tokens: 2048,
    tools: [],
  };

  yield* streamChatCompletion(request);
}
