"use client";

import React, { useState } from "react";
import { Send, Sparkles, MessageSquare, Loader2 } from "lucide-react";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface RefinementChatProps {
  sessionId: string;
  onSendMessage: (message: string) => Promise<void>;
  isRefining: boolean;
}

export const RefinementChat: React.FC<RefinementChatProps> = ({
  sessionId,
  onSendMessage,
  isRefining,
}) => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const quickPrompts = [
    "I don't have a lot of budget, can you generate something cheaper?",
    "Make Day 1 start at 11:00 AM instead.",
    "Add more street food and budget ramen spots.",
    "Swap one paid museum for a free outdoor park.",
  ];

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isRefining) return;

    const userText = input.trim();
    setInput("");

    const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    setMessages((prev) => [
      ...prev,
      { role: "user", content: userText, timestamp: now },
    ]);

    try {
      await onSendMessage(userText);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Itinerary and budget have been refined to your preferences.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Refinement error: ${err.message || "Failed to update trip"}`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    }
  };

  const handleQuickSelect = (promptText: string) => {
    setInput(promptText);
  };

  return (
    <div className="w-full bg-[#0a0a0a] border border-[#1f1f23] rounded-2xl p-6 shadow-2xl space-y-4">
      <div className="flex items-center justify-between pb-4 border-b border-[#1f1f23]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-black border border-[#2a2a30] flex items-center justify-center text-white">
            <MessageSquare className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-white font-semibold text-sm tracking-tight">
              Conversational Itinerary Refinement
            </h3>
            <p className="text-xs text-neutral-400">
              Session ID: <span className="font-mono text-neutral-300">{sessionId}</span>
            </p>
          </div>
        </div>
        {isRefining && (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs bg-white text-black font-semibold border border-white">
            <Loader2 className="w-3 h-3 animate-spin" />
            REFINING ITINERARY...
          </span>
        )}
      </div>

      {/* Chat History */}
      {messages.length > 0 && (
        <div className="max-h-56 overflow-y-auto space-y-3 p-3 bg-black rounded-xl border border-[#1f1f23] scrollbar-thin scrollbar-thumb-neutral-800">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${
                m.role === "user" ? "items-end" : "items-start"
              }`}
            >
              <div
                className={`max-w-[85%] rounded-xl px-3.5 py-2 text-xs leading-relaxed ${
                  m.role === "user"
                    ? "bg-white text-black font-medium"
                    : "bg-[#141414] text-neutral-200 border border-[#222]"
                }`}
              >
                {m.content}
              </div>
              <span className="text-[10px] text-neutral-400 font-mono mt-1 px-1">
                {m.timestamp}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Quick Suggestion Pills */}
      <div className="space-y-1.5">
        <span className="text-[11px] font-mono text-neutral-400 uppercase tracking-wider block">
          Suggested Tweaks
        </span>
        <div className="flex flex-wrap gap-2">
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleQuickSelect(prompt)}
              className="text-[11px] px-2.5 py-1 rounded-lg bg-black border border-[#1f1f23] text-neutral-300 hover:text-white hover:border-neutral-700 transition-colors flex items-center gap-1.5"
            >
              <Sparkles className="w-2.5 h-2.5 text-neutral-400" />
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex items-center gap-2 pt-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="E.g. I have a lower budget, swap expensive dinner with street food..."
          disabled={isRefining}
          className="flex-1 bg-black border border-[#2a2a30] focus:border-white rounded-xl px-4 py-3 text-xs text-white placeholder-neutral-400 outline-none transition-colors disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!input.trim() || isRefining}
          className="px-5 py-3 rounded-xl bg-white text-black hover:bg-neutral-200 font-medium text-xs flex items-center gap-1.5 transition-all disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
        >
          {isRefining ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <>
              <span>Update</span>
              <Send className="w-3.5 h-3.5" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};
