/**
 * useChat Hook - Manages chat state and streaming
 */

import { useState, useCallback, useRef } from "react";
import { Message, ChatState } from "../types";
import { chatMessage, ChatApiError } from "../services/chatApi";

const SYSTEM_PROMPT =
  "You are a helpful AI assistant. You can use tools to help answer questions.";

export function useChat() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
    currentStreamingMessage: "",
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
      }));

      try {
        let fullResponse = "";

        // Stream the response
        const stream = chatMessage(
          [
            ...state.messages,
            { role: "user", content: userMessage },
          ] as Message[],
          SYSTEM_PROMPT
        );

        for await (const event of stream) {
          if (event.type === "content_block_delta" && event.delta?.type === "text_delta") {
            fullResponse += event.delta.text || "";
            setState((prev) => ({
              ...prev,
              currentStreamingMessage: fullResponse,
            }));
          } else if (event.type === "message_stop") {
            // Response complete
            const assistantMessage: Message = {
              role: "assistant",
              content: fullResponse,
              id: Date.now().toString(),
              timestamp: new Date(),
            };

            setState((prev) => ({
              ...prev,
              messages: [...prev.messages, assistantMessage],
              isLoading: false,
              currentStreamingMessage: "",
            }));
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
    [state.messages]
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
    ...state,
    sendMessage,
    clearHistory,
    cancelStream,
  };
}
