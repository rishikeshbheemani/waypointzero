"use client";

import React, { useState } from "react";
import { Navbar } from "@/components/Navbar";
import { TripPlannerForm } from "@/components/TripPlannerForm";
import { LiveAgentPipeline } from "@/components/LiveAgentPipeline";
import { ItineraryView } from "@/components/ItineraryView";
import { BudgetSummaryCard } from "@/components/BudgetSummaryCard";
import { RefinementChat } from "@/components/RefinementChat";
import { PastTripsDrawer } from "@/components/PastTripsDrawer";
import { 
  TripRequest, 
  UserProfile, 
  TripResponse, 
  StreamEvent 
} from "@/types/travel";
import { HelpCircle, ArrowRight, Loader2, RefreshCw } from "lucide-react";

export default function Home() {
  const [tripResponse, setTripResponse] = useState<TripResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamEvents, setStreamEvents] = useState<StreamEvent[]>([]);
  const [activeAgents, setActiveAgents] = useState<Record<string, "idle" | "running" | "completed">>({});
  const [isRefining, setIsRefining] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Clarification state
  const [clarificationQuestion, setClarificationQuestion] = useState<string | null>(null);
  const [clarificationAnswer, setClarificationAnswer] = useState("");
  const [lastRequest, setLastRequest] = useState<TripRequest | null>(null);
  const [lastProfile, setLastProfile] = useState<UserProfile | null>(null);

  const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const API_URL = rawApiUrl.replace(/\/+$/, "");

  // Reset to create a new trip
  const handleNewTrip = () => {
    setTripResponse(null);
    setStreamEvents([]);
    setActiveAgents({});
    setClarificationQuestion(null);
    setErrorMessage(null);
  };

  // Submit trip request with SSE streaming & fallback
  const handleCreateTrip = async (trip: TripRequest, profile: UserProfile) => {
    setIsLoading(true);
    setIsStreaming(true);
    setErrorMessage(null);
    setStreamEvents([]);
    setActiveAgents({});
    setClarificationQuestion(null);
    setLastRequest(trip);
    setLastProfile(profile);

    const initialAgents: Record<string, "idle" | "running" | "completed"> = {
      supervisor: "running",
      research: "idle",
      weather: "idle",
      transport: "idle",
      accommodation: "idle",
      master_planner: "idle",
      budget: "idle",
    };
    setActiveAgents(initialAgents);

    try {
      // Attempt SSE streaming first
      const res = await fetch(`${API_URL}/api/trips/plan/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trip_request: trip, user_profile: profile }),
      });

      if (!res.ok || !res.body) {
        throw new Error(`Streaming failed: HTTP ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let completedTrip: TripResponse | null = null;

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith("data:")) {
            try {
              const eventData: StreamEvent = JSON.parse(trimmed.slice(5).trim());
              setStreamEvents((prev) => [...prev, eventData]);

              // Update agent states based on event
              if (eventData.event_type === "agent_start" && eventData.agent_name) {
                setActiveAgents((prev) => ({
                  ...prev,
                  [eventData.agent_name!]: "running",
                }));
              } else if (eventData.event_type === "agent_complete" && eventData.agent_name) {
                setActiveAgents((prev) => ({
                  ...prev,
                  [eventData.agent_name!]: "completed",
                }));
              } else if (eventData.event_type === "clarification_needed") {
                setClarificationQuestion(eventData.data?.question || "Could you provide more details?");
              } else if (eventData.event_type === "pipeline_complete") {
                const finalTrip: TripResponse = eventData.data?.trip;
                if (finalTrip) {
                  completedTrip = finalTrip;
                  setTripResponse(finalTrip);
                }
              }
            } catch (jsonErr) {
              console.warn("Could not parse SSE JSON line:", trimmed, jsonErr);
            }
          }
        }
      }

      // If streaming finished without final trip data, trigger fallback direct fetch
      if (!completedTrip) {
        const fallbackRes = await fetch(`${API_URL}/api/trips/plan`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ trip_request: trip, user_profile: profile }),
        });
        if (fallbackRes.ok) {
          const data: TripResponse = await fallbackRes.json();
          setTripResponse(data);
          if (data.status === "needs_clarification") {
            setClarificationQuestion(data.clarification_question || "Could you provide more details?");
          }
        }
      }
    } catch (err: any) {
      console.warn("SSE stream failed, falling back to standard POST /api/trips/plan:", err);
      // Fallback to standard synchronous endpoint
      try {
        const fallbackRes = await fetch(`${API_URL}/api/trips/plan`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ trip_request: trip, user_profile: profile }),
        });
        if (!fallbackRes.ok) {
          throw new Error(`API returned HTTP ${fallbackRes.status}`);
        }
        const data: TripResponse = await fallbackRes.json();
        setTripResponse(data);
        if (data.status === "needs_clarification") {
          setClarificationQuestion(data.clarification_question || "Could you provide more details?");
        }
        // Mark all agents completed
        setActiveAgents({
          supervisor: "completed",
          research: "completed",
          weather: "completed",
          transport: "completed",
          accommodation: "completed",
          master_planner: "completed",
          budget: "completed",
        });
      } catch (fallbackErr: any) {
        setErrorMessage(
          `Could not connect to backend server at ${API_URL}. Ensure the FastAPI server is running.`
        );
      }
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  // Handle clarification response from user
  const handleClarificationSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!clarificationAnswer.trim() || !lastRequest) return;

    const updatedTrip: TripRequest = {
      ...lastRequest,
      constraints: [...(lastRequest.constraints || []), `Clarification: ${clarificationAnswer.trim()}`],
    };

    setClarificationQuestion(null);
    setClarificationAnswer("");
    await handleCreateTrip(updatedTrip, lastProfile || {});
  };

  // Handle conversational refinement
  const handleRefineTrip = async (message: string) => {
    if (!tripResponse?.session_id) return;
    setIsRefining(true);
    setErrorMessage(null);

    try {
      const res = await fetch(`${API_URL}/api/trips/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: tripResponse.session_id,
          message: message,
        }),
      });

      if (!res.ok) {
        throw new Error(`Refinement error: HTTP ${res.status}`);
      }

      const updated: TripResponse = await res.json();
      setTripResponse(updated);
    } catch (err: any) {
      console.error("Refinement failed:", err);
      throw err;
    } finally {
      setIsRefining(false);
    }
  };

  // Load a saved trip from history
  const handleSelectPastTrip = async (sessionId: string) => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const res = await fetch(`${API_URL}/api/trips/${sessionId}`);
      if (!res.ok) {
        throw new Error(`Failed to load trip: HTTP ${res.status}`);
      }
      const data = await res.json();
      const loadedTrip: TripResponse = {
        session_id: data.session_id,
        status: data.has_itinerary ? "completed" : "needs_clarification",
        itinerary: data.itinerary,
        budget: data.budget,
        hotels: data.hotels || [],
        transport: data.transport,
        weather: data.weather,
      };
      setTripResponse(loadedTrip);
      setActiveAgents({
        supervisor: "completed",
        research: "completed",
        weather: "completed",
        transport: "completed",
        accommodation: "completed",
        master_planner: "completed",
        budget: "completed",
      });
    } catch (err: any) {
      setErrorMessage(`Failed to load trip: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white selection:bg-white selection:text-black">
      {/* Top Monochrome Navbar */}
      <Navbar
        onNewTrip={handleNewTrip}
        onOpenHistory={() => setHistoryOpen(true)}
        hasActiveTrip={!!tripResponse}
      />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Error Alert */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-700 text-neutral-300 text-xs flex items-center justify-between">
            <span>{errorMessage}</span>
            <button
              onClick={() => setErrorMessage(null)}
              className="px-2 py-1 text-white hover:underline text-[11px]"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Form View (Shown when no trip loaded) */}
        {!tripResponse && (
          <div className="space-y-8 animate-fadeIn">
            <TripPlannerForm onSubmit={handleCreateTrip} isLoading={isLoading} />

            {/* Live Pipeline Tracker while loading */}
            {(isLoading || streamEvents.length > 0) && (
              <div className="max-w-4xl mx-auto">
                <LiveAgentPipeline
                  events={streamEvents}
                  isStreaming={isStreaming}
                  activeAgents={activeAgents}
                />
              </div>
            )}
          </div>
        )}

        {/* Clarification Modal / Prompt */}
        {clarificationQuestion && (
          <div className="max-w-2xl mx-auto p-6 rounded-2xl bg-[#0a0a0a] border border-[#2a2a30] shadow-2xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-black border border-[#333] flex items-center justify-center text-white">
                <HelpCircle className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">
                  Agent Clarification Needed
                </h3>
                <p className="text-xs text-neutral-400">
                  The Supervisor agent requires additional details to synthesize an optimal plan.
                </p>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-black border border-[#1f1f23] text-xs text-neutral-200">
              {clarificationQuestion}
            </div>

            <form onSubmit={handleClarificationSubmit} className="flex items-center gap-2">
              <input
                type="text"
                required
                value={clarificationAnswer}
                onChange={(e) => setClarificationAnswer(e.target.value)}
                placeholder="Type your response here..."
                className="flex-1 bg-black border border-[#262626] focus:border-white rounded-xl px-4 py-2.5 text-xs text-white placeholder-neutral-500 outline-none"
              />
              <button
                type="submit"
                className="px-4 py-2.5 rounded-xl bg-white text-black font-semibold text-xs hover:bg-neutral-200 transition-colors flex items-center gap-1.5"
              >
                <span>Continue</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        )}

        {/* Full Trip Blueprint Dashboard */}
        {tripResponse && (
          <div className="space-y-8 animate-fadeIn">
            {/* Live Agent Status Bar */}
            <LiveAgentPipeline
              events={streamEvents}
              isStreaming={isStreaming}
              activeAgents={activeAgents}
            />

            {/* Budget Analysis */}
            <BudgetSummaryCard
              budget={tripResponse.budget}
              requestedBudget={lastRequest?.budget}
            />

            {/* Synthesized Itinerary & Exploration View */}
            <ItineraryView
              itinerary={tripResponse.itinerary}
              hotels={tripResponse.hotels}
              transport={tripResponse.transport}
              weather={tripResponse.weather}
            />

            {/* Multi-turn Conversational Refinement */}
            <RefinementChat
              sessionId={tripResponse.session_id}
              onSendMessage={handleRefineTrip}
              isRefining={isRefining}
            />
          </div>
        )}
      </main>

      {/* Past Trips Drawer */}
      <PastTripsDrawer
        isOpen={historyOpen}
        onClose={() => setHistoryOpen(false)}
        onSelectTrip={handleSelectPastTrip}
        apiUrl={API_URL}
      />
    </div>
  );
}
