"use client";

import React from "react";
import { Compass, History, Plus, Terminal } from "lucide-react";

interface NavbarProps {
  onNewTrip: () => void;
  onOpenHistory: () => void;
  hasActiveTrip: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  onNewTrip,
  onOpenHistory,
  hasActiveTrip,
}) => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-[#222222] bg-black/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo & Identity */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={onNewTrip}>
          <div className="flex h-9 w-9 items-center justify-center rounded-sm bg-white text-black font-black text-lg">
            W
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-base font-bold tracking-wider text-white">
                WAYPOINTZERO
              </span>
              <span className="hidden rounded-full border border-[#333333] px-2 py-0.5 font-mono text-[10px] uppercase text-[#888888] sm:inline-block">
                Multi-Agent Core
              </span>
            </div>
          </div>
        </div>

        {/* Live Status & Actions */}
        <div className="flex items-center space-x-3">
          <div className="hidden items-center space-x-2 rounded-full border border-[#222222] bg-[#0c0c0c] px-3 py-1 font-mono text-xs text-[#888888] md:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-white animate-pulse-subtle" />
            <span>AI AGENTS READY</span>
          </div>

          <button
            onClick={onOpenHistory}
            className="flex items-center space-x-1.5 rounded-sm border border-[#333333] bg-transparent px-3 py-1.5 font-mono text-xs text-white transition-colors hover:border-white hover:bg-[#111111]"
            title="Saved Trips"
          >
            <History className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Trips</span>
          </button>

          {hasActiveTrip && (
            <button
              onClick={onNewTrip}
              className="flex items-center space-x-1.5 rounded-sm bg-white px-3 py-1.5 font-mono text-xs font-semibold text-black transition-opacity hover:opacity-90"
            >
              <Plus className="h-3.5 w-3.5" />
              <span>New Plan</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
