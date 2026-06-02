/**
 * useChat Hook - Manages chat state and streaming with tool calling
 */

import { useState, useCallback, useRef } from "react";
import { Message, ChatState, ToolCallDisplay } from "../types";
import { chatMessage, ChatApiError } from "../services/chatApi";

const SYSTEM_PROMPT =
  "You are a helpful AI assistant. You can use tools to help answer questions. When using tools, be clear about what you're doing.";

interface InternalChatState extends ChatState {
  toolCalls: ToolCallDisplay[];
  currentToolCall: Partial<ToolCallDisplay> | null;
  currentToolInput: string;
}

export function useChat() {
  const [state, setState] = useState<InternalChatState>({
    messages: [],
    isLoading: false,
    error: null,
    currentStreamingMessage: "",
    toolCalls: [],
    currentToolCall: null,
    currentToolInput: "",
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Send a user message and stream the response
   */
  const sendMessage = useCallback(
    async (userMessage: string) => {
      if (!userMessage.trim()) {
        setState((prev) => ({
          ...prev,
          error: "Message cannot be empty",
        }));
        return;
      }

      // Add user message to conversation
      const newMessage: Message = {
        role: "user",
        content: userMessage,
        id: Date.now().toString(),
        timestamp: new Date(),
      };

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, newMessage],
        isLoading: true,
        error: null,
        currentStreamingMessage: "",
        toolCalls: [],
        currentToolCall: null,
        currentToolInput: "",
      }));

      try {
        let fullResponse = "";
        let assistantMessage: Message | null = null;

        // Stream the response
        const stream = chatMessage(
          [
            ...state.messages,
            { role: "user", content: userMessage },
          ] as Message[],
          SYSTEM_PROMPT
        );

        for await (const event of stream) {
          if (event.type === "content_block_delta") {
            if (event.delta?.type === "text_delta") {
              // Regular text response
              fullResponse += event.delta.text || "";
              setState((prev) => ({
                ...prev,
                currentStreamingMessage: fullResponse,
              }));
            } else if (event.delta?.type === "tool_use") {
              // Tool call detected
              const toolId = event.delta.id || `tool-${Date.now()}`;
              const toolName = event.delta.name || "unknown";
              const toolInput = event.delta.input || "";

              if (!state.currentToolCall || state.currentToolCall.id !== toolId) {
                // New tool call starting
                setState((prev) => ({
                  ...prev,
                  currentToolCall: {
                    id: toolId,
                    name: toolName,
                    input: {},
                    status: "pending" as const,
                  },
                  currentToolInput: toolInput,
                }));
              } else {
                // Accumulating tool input
                setState((prev) => ({
                  ...prev,
                  currentToolInput: prev.currentToolInput + (toolInput || ""),
                }));
              }
            }
          } else if (event.type === "content_block_stop") {
            // Tool call complete - parse the accumulated input
            if (state.currentToolCall && state.currentToolInput) {
              try {
                const parsedInput = JSON.parse(state.currentToolInput);
                const newToolCall: ToolCallDisplay = {
                  ...state.currentToolCall,
                  input: parsedInput,
                  status: "pending",
                } as ToolCallDisplay;

                setState((prev) => ({
                  ...prev,
                  toolCalls: [...prev.toolCalls, newToolCall],
                  currentToolCall: null,
                  currentToolInput: "",
                }));
              } catch (e) {
                console.error("Failed to parse tool input:", state.currentToolInput);
              }
            }
          } else if (event.type === "message_stop") {
            // Response complete
            if (!assistantMessage) {
              assistantMessage = {
                role: "assistant",
                content: fullResponse,
                id: Date.now().toString(),
                timestamp: new Date(),
              };

              setState((prev) => ({
                ...prev,
                messages: [...prev.messages, assistantMessage!],
                isLoading: false,
                currentStreamingMessage: "",
              }));
            }
          } else if (event.type === "error") {
            throw new Error(event.error?.message || "Unknown error");
          }
        }
      } catch (error) {
        const errorMessage =
          error instanceof ChatApiError
            ? `API Error: ${error.message}`
            : error instanceof Error
              ? error.message
              : "Unknown error occurred";

        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: errorMessage,
          currentStreamingMessage: "",
        }));

        console.error("Chat error:", error);
      }
    },
    [state.messages, state.currentToolCall, state.currentToolInput]
  );

  /**
   * Clear conversation history
   */
  const clearHistory = useCallback(() => {
    setState({
      messages: [],
      isLoading: false,
      error: null,
      currentStreamingMessage: "",
      toolCalls: [],
      currentToolCall: null,
      currentToolInput: "",
    });
  }, []);

  /**
   * Cancel ongoing streaming
   */
  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    setState((prev) => ({
      ...prev,
      isLoading: false,
    }));
  }, []);

  return {
    messages: state.messages,
    isLoading: state.isLoading,
    error: state.error,
    currentStreamingMessage: state.currentStreamingMessage,
    toolCalls: state.toolCalls,
    sendMessage,
    clearHistory,
    cancelStream,
  };
}
