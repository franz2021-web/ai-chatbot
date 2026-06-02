/**
 * ToolCall Component - Displays tool calls and results
 */

import { ToolCallDisplay } from "../types";

interface ToolCallProps {
  tool: ToolCallDisplay;
}

export function ToolCall({ tool }: ToolCallProps) {
  return (
    <div className="mt-3 p-3 rounded-md bg-white/10 border border-white/20">
      <div className="flex items-center gap-2 mb-2">
        <div className={`w-3 h-3 rounded-full ${
          tool.status === "completed"
            ? "bg-green-400"
            : tool.status === "error"
              ? "bg-red-400"
              : tool.status === "executing"
                ? "bg-yellow-400 animate-pulse"
                : "bg-blue-400"
        }`}></div>
        <span className="font-semibold text-white/90">{tool.name}</span>
        <span className="text-xs text-white/60 ml-auto">
          {tool.status === "completed"
            ? "✓ Done"
            : tool.status === "error"
              ? "✗ Error"
              : tool.status === "executing"
                ? "⟳ Running"
                : "⏳ Pending"}
        </span>
      </div>

      {/* Input Parameters */}
      <div className="bg-black/20 rounded p-2 mb-2">
        <div className="text-xs text-white/60 mb-1 font-mono">Input:</div>
        <div className="text-sm text-white/80 font-mono whitespace-pre-wrap break-words">
          {JSON.stringify(tool.input, null, 2)}
        </div>
      </div>

      {/* Results */}
      {tool.result && (
        <div className="bg-black/20 rounded p-2 mb-2">
          <div className="text-xs text-white/60 mb-1 font-mono">Result:</div>
          <div className="text-sm text-white/80 font-mono whitespace-pre-wrap break-words">
            {typeof tool.result === "string"
              ? tool.result
              : JSON.stringify(tool.result, null, 2)}
          </div>
        </div>
      )}

      {/* Error Message */}
      {tool.error && (
        <div className="bg-red-500/20 rounded p-2 border border-red-500/30">
          <div className="text-xs text-red-200 font-mono">{tool.error}</div>
        </div>
      )}
    </div>
  );
}
