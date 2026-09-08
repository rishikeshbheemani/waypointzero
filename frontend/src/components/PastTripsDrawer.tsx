"use client";

import React, { useState, useEffect } from "react";
import { 
  History, 
  X, 
  MapPin, 
  Calendar, 
  Wallet, 
  ArrowRight, 
  Loader2, 
  RefreshCw 
} from "lucide-react";

interface PastTrip {
  session_id: string;
  destination: string;
  origin?: string | null;
  duration_days: number;
  budget?: number | null;
  status: string;
  created_at: string;
}

interface PastTripsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTrip: (sessionId: string) => Promise<void>;
  apiUrl: string;
}

export const PastTripsDrawer: React.FC<PastTripsDrawerProps> = ({
  isOpen,
  onClose,
  onSelectTrip,
  apiUrl,
}) => {
  const [trips, setTrips] = useState<PastTrip[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const fetchTrips = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${apiUrl}/api/trips`);
      if (res.ok) {
        const data = await res.json();
        setTrips(data.trips || []);
      }
    } catch (err) {
      console.error("Failed to load past trips:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchTrips();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSelect = async (sessionId: string) => {
    try {
      setSelectedId(sessionId);
      await onSelectTrip(sessionId);
      onClose();
    } finally {
      setSelectedId(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/80 backdrop-blur-sm transition-all animate-fadeIn">
      <div className="w-full max-w-md bg-[#0a0a0a] border-l border-[#1f1f23] h-full flex flex-col shadow-2xl">
        {/* Drawer Header */}
        <div className="flex items-center justify-between p-6 border-b border-[#1f1f23]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-black border border-[#2a2a30] flex items-center justify-center text-white">
              <History className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-semibold text-white text-sm">Saved Trip Records</h3>
              <p className="text-xs text-neutral-400">Database History</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={fetchTrips}
              className="p-2 rounded-lg bg-black border border-[#1f1f23] text-neutral-400 hover:text-white transition-colors"
              title="Refresh"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-2 rounded-lg bg-black border border-[#1f1f23] text-neutral-400 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Trips List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-3 scrollbar-thin scrollbar-thumb-neutral-800">
          {loading ? (
            <div className="h-40 flex flex-col items-center justify-center text-neutral-400 gap-2 font-mono text-xs">
              <Loader2 className="w-5 h-5 animate-spin text-white" />
              <span>Querying saved trips...</span>
            </div>
          ) : trips.length === 0 ? (
            <div className="h-40 flex flex-col items-center justify-center text-neutral-400 font-mono text-xs text-center">
              <span>No trips recorded yet.</span>
              <span className="text-[11px] text-neutral-400 mt-1">Generate your first plan to save it to the database.</span>
            </div>
          ) : (
            trips.map((trip) => (
              <div
                key={trip.session_id}
                className="p-4 rounded-xl bg-black border border-[#1a1a1e] hover:border-neutral-700 transition-all flex flex-col justify-between gap-3 group"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-1.5 text-white font-semibold text-sm">
                      <MapPin className="w-3.5 h-3.5 text-neutral-400" />
                      <span>{trip.destination}</span>
                    </div>
                    {trip.origin && (
                      <span className="text-[11px] text-neutral-400 block mt-0.5">
                        Departing from {trip.origin}
                      </span>
                    )}
                  </div>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-neutral-900 text-neutral-300 border border-[#222]">
                    {trip.status}
                  </span>
                </div>

                <div className="flex items-center gap-4 text-xs text-neutral-400 font-mono">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3 text-neutral-400" />
                    {trip.duration_days} days
                  </span>
                  {trip.budget != null && (
                    <span className="flex items-center gap-1">
                      <Wallet className="w-3 h-3 text-neutral-400" />
                      ${trip.budget}
                    </span>
                  )}
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-[#141414]">
                  <span className="text-[10px] text-neutral-400 font-mono">
                    {trip.created_at ? trip.created_at.slice(0, 10) : ""}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleSelect(trip.session_id)}
                    disabled={selectedId === trip.session_id}
                    className="inline-flex items-center gap-1 text-xs text-white group-hover:translate-x-0.5 transition-all font-medium"
                  >
                    {selectedId === trip.session_id ? (
                      <Loader2 className="w-3 h-3 animate-spin" />
                    ) : (
                      <>
                        <span>Load Blueprint</span>
                        <ArrowRight className="w-3 h-3" />
                      </>
                    )}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
