"use client";

import React, { useState } from "react";
import { ArrowRight, DollarSign, Globe, MapPin, Sparkles, User } from "lucide-react";
import { TripRequest, UserProfile } from "@/types/travel";

interface TripPlannerFormProps {
  onSubmit: (trip: TripRequest, profile: UserProfile) => void;
  isLoading: boolean;
}

const STYLE_OPTIONS = [
  "Balanced",
  "Cultural Explorer",
  "Budget Backpacker",
  "Luxury & Boutique",
  "Relaxed & Foodie",
];

const INTEREST_OPTIONS = [
  "Historical Landmarks",
  "Local Street Food",
  "Hidden Gems & Alleys",
  "Museums & Art",
  "Scenic Nature & Parks",
  "Nightlife & Izakayas",
];

export const TripPlannerForm: React.FC<TripPlannerFormProps> = ({
  onSubmit,
  isLoading,
}) => {
  const [destination, setDestination] = useState("Tokyo, Japan");
  const [origin, setOrigin] = useState("Seattle, WA");
  const [durationDays, setDurationDays] = useState(4);
  const [budget, setBudget] = useState<number | undefined>(2500);
  const [travelStyle, setTravelStyle] = useState("Balanced");
  const [selectedInterests, setSelectedInterests] = useState<string[]>([
    "Historical Landmarks",
    "Local Street Food",
  ]);
  const [constraints, setConstraints] = useState("");

  const toggleInterest = (interest: string) => {
    if (selectedInterests.includes(interest)) {
      setSelectedInterests(selectedInterests.filter((i) => i !== interest));
    } else {
      setSelectedInterests([...selectedInterests, interest]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!destination.trim() || isLoading) return;

    const trip: TripRequest = {
      destination: destination.trim(),
      origin: origin.trim() || undefined,
      duration_days: Number(durationDays),
      budget: budget ? Number(budget) : undefined,
      interests: selectedInterests,
      constraints: constraints ? [constraints.trim()] : [],
    };

    const profile: UserProfile = {
      travel_style: travelStyle,
    };

    onSubmit(trip, profile);
  };

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-8 text-center">
        <span className="mb-2 inline-block rounded-full border border-[#222222] bg-[#0c0c0c] px-3 py-1 font-mono text-[11px] uppercase tracking-wider text-[#888888]">
          WaypointZero Multi-Agent System
        </span>
        <h1 className="text-3xl font-extrabold tracking-tight sm:text-5xl text-white">
          Autonomous Travel Planning
        </h1>
        <p className="mt-3 text-sm text-[#888888] sm:text-base max-w-xl mx-auto">
          Orchestrating specialized agents for research, transport, weather, lodging, master scheduling, and budget optimization.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="rounded-lg border border-[#222222] bg-[#0a0a0a] p-6 sm:p-8 shadow-2xl"
      >
        <div className="space-y-6">
          {/* Destination & Origin */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 flex items-center space-x-1.5 font-mono text-xs text-[#aaaaaa]">
                <MapPin className="h-3.5 w-3.5 text-white" />
                <span>DESTINATION</span>
              </label>
              <input
                type="text"
                required
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="e.g. Tokyo, Rome, Paris, Kyoto"
                className="w-full rounded border border-[#262626] bg-[#050505] px-3.5 py-2.5 font-sans text-sm text-white placeholder-[#555555] transition-colors hover:border-[#444444]"
              />
            </div>

            <div>
              <label className="mb-1.5 flex items-center space-x-1.5 font-mono text-xs text-[#aaaaaa]">
                <Globe className="h-3.5 w-3.5 text-white" />
                <span>DEPARTURE ORIGIN (OPTIONAL)</span>
              </label>
              <input
                type="text"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                placeholder="e.g. New York, London, SEA"
                className="w-full rounded border border-[#262626] bg-[#050505] px-3.5 py-2.5 font-sans text-sm text-white placeholder-[#555555] transition-colors hover:border-[#444444]"
              />
            </div>
          </div>

          {/* Duration & Budget */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 flex items-center justify-between font-mono text-xs text-[#aaaaaa]">
                <span>DURATION (DAYS)</span>
                <span className="text-white font-bold">{durationDays} Days</span>
              </label>
              <div className="flex space-x-2">
                {[3, 4, 5, 7, 10].map((d) => (
                  <button
                    key={d}
                    type="button"
                    onClick={() => setDurationDays(d)}
                    className={`flex-1 rounded border py-2 font-mono text-xs transition-colors ${
                      durationDays === d
                        ? "border-white bg-white font-bold text-black"
                        : "border-[#262626] bg-[#050505] text-[#888888] hover:border-[#444444] hover:text-white"
                    }`}
                  >
                    {d}D
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="mb-1.5 flex items-center space-x-1.5 font-mono text-xs text-[#aaaaaa]">
                <DollarSign className="h-3.5 w-3.5 text-white" />
                <span>TOTAL BUDGET (USD, OPTIONAL)</span>
              </label>
              <input
                type="number"
                min="0"
                step="50"
                value={budget !== undefined ? budget : ""}
                onChange={(e) =>
                  setBudget(e.target.value ? Number(e.target.value) : undefined)
                }
                placeholder="e.g. 2000 (leave blank for flexible)"
                className="w-full rounded border border-[#262626] bg-[#050505] px-3.5 py-2 font-mono text-sm text-white placeholder-[#555555] transition-colors hover:border-[#444444]"
              />
            </div>
          </div>

          {/* Travel Style */}
          <div>
            <label className="mb-2 block font-mono text-xs text-[#aaaaaa]">
              TRAVEL STYLE & PACING
            </label>
            <div className="flex flex-wrap gap-2">
              {STYLE_OPTIONS.map((style) => (
                <button
                  key={style}
                  type="button"
                  onClick={() => setTravelStyle(style)}
                  className={`rounded-full border px-3.5 py-1.5 font-mono text-xs transition-colors ${
                    travelStyle === style
                      ? "border-white bg-white font-semibold text-black"
                      : "border-[#262626] bg-[#050505] text-[#888888] hover:border-[#444444] hover:text-white"
                  }`}
                >
                  {style}
                </button>
              ))}
            </div>
          </div>

          {/* Interests */}
          <div>
            <label className="mb-2 block font-mono text-xs text-[#aaaaaa]">
              EXPERIENCES & INTERESTS
            </label>
            <div className="flex flex-wrap gap-2">
              {INTEREST_OPTIONS.map((interest) => {
                const isSelected = selectedInterests.includes(interest);
                return (
                  <button
                    key={interest}
                    type="button"
                    onClick={() => toggleInterest(interest)}
                    className={`rounded-full border px-3 py-1 font-mono text-xs transition-colors ${
                      isSelected
                        ? "border-white bg-white text-black font-semibold"
                        : "border-[#262626] bg-[#050505] text-[#888888] hover:border-[#444444] hover:text-white"
                    }`}
                  >
                    {isSelected ? "✓ " : "+ "}
                    {interest}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Constraints */}
          <div>
            <label className="mb-1.5 block font-mono text-xs text-[#aaaaaa]">
              CONSTRAINTS / NOTES (OPTIONAL)
            </label>
            <input
              type="text"
              value={constraints}
              onChange={(e) => setConstraints(e.target.value)}
              placeholder="e.g. Vegetarian dining, avoid early mornings, wheelchair accessible"
              className="w-full rounded border border-[#262626] bg-[#050505] px-3.5 py-2 font-sans text-sm text-white placeholder-[#555555] transition-colors hover:border-[#444444]"
            />
          </div>

          {/* Submit CTA */}
          <button
            type="submit"
            disabled={isLoading || !destination.trim()}
            className="group relative flex w-full items-center justify-center space-x-2 rounded border border-white bg-white py-3.5 font-mono text-sm font-bold text-black transition-all hover:bg-[#e4e4e7] disabled:opacity-50"
          >
            {isLoading ? (
              <span className="flex items-center space-x-2">
                <span className="h-4 w-4 rounded-full border-2 border-black border-t-transparent animate-spin" />
                <span>ORCHESTRATING AGENT PIPELINE...</span>
              </span>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                <span>GENERATE AUTONOMOUS ITINERARY</span>
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
