/**
 * ChatInterface Component - Main chat UI with Tailwind CSS and Tool Calling
 */

import { useState, useRef, useEffect } from "react";
import { useChat } from "../hooks/useChat";
import { ToolCall } from "./ToolCall";

export function ChatInterface() {
  const { messages, isLoading, error, currentStreamingMessage, toolCalls, sendMessage, clearHistory } =
    useChat();
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentStreamingMessage, toolCalls]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    await sendMessage(inputValue);
    setInputValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-purple-500 via-purple-600 to-purple-700 font-sans">
      {/* Header */}
      <div className="flex justify-between items-center px-8 py-6 bg-black/20 border-b border-white/10">
        <h1 className="text-2xl font-bold text-white">AI Chatbot</h1>
        {messages.length > 0 && (
          <button
            onClick={clearHistory}
            className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white border border-white/30 rounded-md text-sm font-semibold transition-all duration-200"
          >
            Clear
          </button>
        )}
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-4">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col justify-center items-center h-full text-center text-white/70">
            <p className="text-xl font-semibold mb-2">Start a conversation!</p>
            <p className="text-sm">
              Ask me to calculate (e.g., "What is 2+2?"), search the web (e.g., "Latest AI news"), or get the weather
              (e.g., "Weather in New York").
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col gap-2 p-4 rounded-lg animate-slideIn max-w-2xl ${
              msg.role === "user"
                ? "self-end bg-white/90 text-gray-900"
                : "self-start bg-black/20 text-white"
            }`}
          >
            <div className="text-xs font-semibold uppercase tracking-wider opacity-70">
              {msg.role === "user" ? "You" : "Assistant"}
            </div>
            <div className="text-sm leading-relaxed">{msg.content}</div>
            {msg.timestamp && (
              <div className="text-xs opacity-60 mt-1">{msg.timestamp.toLocaleTimeString()}</div>
            )}
          </div>
        ))}

        {/* Tool Calls Display */}
        {toolCalls.length > 0 && (
          <div className="flex flex-col gap-2 p-4 rounded-lg max-w-2xl self-start bg-black/20 text-white animate-slideIn">
            <div className="text-xs font-semibold uppercase tracking-wider opacity-70">Tools Used</div>
            <div className="space-y-2">
              {toolCalls.map((tool) => (
                <ToolCall key={tool.id} tool={tool} />
              ))}
            </div>
          </div>
        )}

        {isLoading && currentStreamingMessage && (
          <div className="flex flex-col gap-2 p-4 rounded-lg max-w-2xl self-start bg-black/30 text-white animate-slideIn">
            <div className="text-xs font-semibold uppercase tracking-wider opacity-70">Assistant</div>
            <div className="text-sm leading-relaxed">
              {currentStreamingMessage}
              <span className="inline-block ml-1 animate-blink">▌</span>
            </div>
          </div>
        )}

        {isLoading && !currentStreamingMessage && (
          <div className="flex flex-col gap-2 p-4 rounded-lg max-w-2xl self-start bg-black/30 text-white animate-slideIn">
            <div className="text-xs font-semibold uppercase tracking-wider opacity-70">Assistant</div>
            <div className="flex gap-1 items-center">
              <span
                className="inline-block w-2 h-2 bg-white/60 rounded-full animate-bounce-custom"
                style={{ animationDelay: "0s" }}
              ></span>
              <span
                className="inline-block w-2 h-2 bg-white/60 rounded-full animate-bounce-custom"
                style={{ animationDelay: "-0.32s" }}
              ></span>
              <span
                className="inline-block w-2 h-2 bg-white/60 rounded-full animate-bounce-custom"
                style={{ animationDelay: "-0.16s" }}
              ></span>
            </div>
          </div>
        )}

        {error && (
          <div className="flex flex-col gap-2 p-4 rounded-lg max-w-2xl self-center bg-red-500/20 text-red-200 border border-red-500/50">
            <div className="text-xs font-semibold uppercase tracking-wider opacity-70">Error</div>
            <div className="text-sm">{error}</div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="px-8 py-6 bg-black/10 border-t border-white/10">
        <div className="flex gap-3 max-w-4xl mx-auto">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (press Enter to send)"
            disabled={isLoading}
            className="flex-1 px-4 py-3 rounded-md bg-white/90 text-gray-900 placeholder-gray-500 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="px-6 py-3 bg-white/30 hover:bg-white/40 disabled:opacity-50 disabled:cursor-not-allowed text-white border border-white/50 rounded-md font-semibold transition-all duration-200"
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
