"use client";

import React from "react";
import { 
  Bot, 
  CheckCircle2, 
  Loader2, 
  Compass, 
  CloudSun, 
  Plane, 
  Building2, 
  CalendarDays, 
  Wallet,
  Activity
} from "lucide-react";
import { StreamEvent } from "@/types/travel";

export interface AgentStatus {
  name: string;
  label: string;
  category: "supervisor" | "parallel" | "synthesis" | "budget";
  status: "idle" | "running" | "completed" | "error";
  message?: string;
}

interface LiveAgentPipelineProps {
  events: StreamEvent[];
  isStreaming: boolean;
  activeAgents: Record<string, "idle" | "running" | "completed">;
}

export const LiveAgentPipeline: React.FC<LiveAgentPipelineProps> = ({
  events,
  isStreaming,
  activeAgents,
}) => {
  const getAgentIcon = (name: string) => {
    switch (name.toLowerCase()) {
      case "supervisor":
        return <Bot className="w-4 h-4" />;
      case "research":
        return <Compass className="w-4 h-4" />;
      case "weather":
        return <CloudSun className="w-4 h-4" />;
      case "transport":
        return <Plane className="w-4 h-4" />;
      case "accommodation":
        return <Building2 className="w-4 h-4" />;
      case "master_planner":
        return <CalendarDays className="w-4 h-4" />;
      case "budget":
        return <Wallet className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const agentsList = [
    { key: "supervisor", label: "Supervisor", category: "Routing" },
    { key: "research", label: "Attractions", category: "Parallel Discovery" },
    { key: "weather", label: "Weather", category: "Parallel Discovery" },
    { key: "transport", label: "Transit & Flights", category: "Parallel Discovery" },
    { key: "accommodation", label: "Lodging", category: "Parallel Discovery" },
    { key: "master_planner", label: "Master Planner", category: "Synthesis" },
    { key: "budget", label: "Budget Agent", category: "Financial Check" },
  ];

  return (
    <div className="w-full bg-[#0a0a0a] border border-[#1f1f23] rounded-2xl p-6 font-mono text-sm shadow-2xl backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between pb-5 border-b border-[#1f1f23]">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-black border border-[#2a2a30]">
            <Activity className="w-4 h-4 text-white" />
            {isStreaming && (
              <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-white"></span>
              </span>
            )}
          </div>
          <div>
            <h3 className="font-semibold text-white tracking-wider uppercase text-xs">
              Agent Orchestration Engine
            </h3>
            <p className="text-xs text-neutral-400 font-sans">
              LangGraph Multi-Agent Parallel Pipeline
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isStreaming ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs bg-white/10 text-white border border-white/20">
              <Loader2 className="w-3 h-3 animate-spin text-white" />
              EXECUTING
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs bg-neutral-900 text-neutral-400 border border-[#222]">
              <CheckCircle2 className="w-3 h-3 text-neutral-400" />
              IDLE
            </span>
          )}
        </div>
      </div>

      {/* Pipeline Visual Track */}
      <div className="mt-6">
        <div className="text-[11px] uppercase tracking-widest text-neutral-400 mb-3">
          Agent Execution Graph
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2.5">
          {agentsList.map((agent) => {
            const status = activeAgents[agent.key] || "idle";
            const isRunning = status === "running";
            const isDone = status === "completed";

            return (
              <div
                key={agent.key}
                className={`p-3 rounded-xl border transition-all duration-300 flex flex-col justify-between min-h-[90px] ${
                  isRunning
                    ? "bg-white text-black border-white shadow-[0_0_20px_rgba(255,255,255,0.2)]"
                    : isDone
                    ? "bg-black text-white border-neutral-700"
                    : "bg-[#0c0c0c] text-neutral-400 border-[#1a1a1e]"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div
                    className={`p-1.5 rounded-lg ${
                      isRunning
                        ? "bg-black text-white"
                        : isDone
                        ? "bg-neutral-800 text-white"
                        : "bg-neutral-900 text-neutral-400"
                    }`}
                  >
                    {getAgentIcon(agent.key)}
                  </div>
                  {isRunning && (
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-black" />
                  )}
                  {isDone && (
                    <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                  )}
                </div>

                <div className="mt-2">
                  <div className="font-sans font-semibold text-xs leading-tight">
                    {agent.label}
                  </div>
                  <div
                    className={`text-[10px] mt-0.5 tracking-tight ${
                      isRunning ? "text-neutral-700" : "text-neutral-400"
                    }`}
                  >
                    {agent.category}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Real-time Streaming Logs */}
      <div className="mt-6">
        <div className="flex items-center justify-between mb-2">
          <div className="text-[11px] uppercase tracking-widest text-neutral-400">
            Live Stream Feed
          </div>
          <div className="text-[11px] text-neutral-400">
            {events.length} events logged
          </div>
        </div>

        <div className="h-36 overflow-y-auto rounded-xl bg-black border border-[#1f1f23] p-3 space-y-1.5 text-xs select-text scrollbar-thin scrollbar-thumb-neutral-800">
          {events.length === 0 ? (
            <div className="h-full flex items-center justify-center text-neutral-400 italic">
              Awaiting trip planning query to stream graph execution...
            </div>
          ) : (
            events.map((ev, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2.5 hover:bg-neutral-900/40 px-1 py-0.5 rounded transition-colors"
              >
                <span className="text-neutral-400 text-[10px] shrink-0 pt-0.5">
                  {ev.timestamp ? ev.timestamp.slice(11, 19) : "00:00:00"}
                </span>
                <span
                  className={`font-semibold shrink-0 uppercase text-[10px] px-1.5 py-0.2 rounded border ${
                    ev.event_type === "agent_complete"
                      ? "text-white border-neutral-700 bg-neutral-900"
                      : ev.event_type === "agent_start"
                      ? "text-black border-white bg-white"
                      : "text-neutral-300 border-neutral-800"
                  }`}
                >
                  {ev.agent_name || ev.event_type}
                </span>
                <span className="text-neutral-300 break-all font-sans text-xs">
                  {ev.data?.message ||
                    (ev.data?.status === "completed"
                      ? "Agent execution finished successfully"
                      : JSON.stringify(ev.data))}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
