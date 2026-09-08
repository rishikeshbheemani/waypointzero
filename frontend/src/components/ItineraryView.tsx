"use client";

import React, { useState } from "react";
import { 
  Calendar, 
  Clock, 
  MapPin, 
  Building2, 
  Plane, 
  CloudSun, 
  Tag, 
  Compass,
  Star,
  Luggage,
  Sparkles,
  Ticket
} from "lucide-react";
import { 
  Itinerary, 
  HotelRecommendation, 
  TransportInfo, 
  WeatherInfo 
} from "@/types/travel";

interface ItineraryViewProps {
  itinerary: Itinerary | null | undefined;
  hotels?: HotelRecommendation[];
  transport?: TransportInfo | null;
  weather?: WeatherInfo | null;
}

export const ItineraryView: React.FC<ItineraryViewProps> = ({
  itinerary,
  hotels = [],
  transport,
  weather,
}) => {
  const [activeDayIndex, setActiveDayIndex] = useState(0);
  const [activeTab, setActiveTab] = useState<"itinerary" | "hotels" | "transport" | "weather">("itinerary");

  if (!itinerary || !itinerary.days || itinerary.days.length === 0) {
    return (
      <div className="w-full bg-[#0a0a0a] border border-[#1f1f23] rounded-2xl p-12 text-center text-neutral-400 font-mono">
        <Calendar className="w-8 h-8 mx-auto mb-3 text-neutral-400" />
        No synthesized itinerary available yet. Submit your trip request above.
      </div>
    );
  }

  const days = itinerary.days;
  const currentDay = days[activeDayIndex] || days[0];

  return (
    <div className="w-full bg-[#0a0a0a] border border-[#1f1f23] rounded-2xl p-6 shadow-2xl space-y-6">
      {/* Title & Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-6 border-b border-[#1f1f23]">
        <div>
          <span className="text-[11px] font-mono tracking-widest text-neutral-400 uppercase">
            Master Planner Synthesized Itinerary
          </span>
          <h2 className="text-2xl lg:text-3xl font-bold text-white tracking-tight mt-1">
            {itinerary.trip_title || "Your Custom Travel Blueprint"}
          </h2>
          {itinerary.summary && (
            <p className="text-sm text-neutral-300 mt-2 max-w-3xl leading-relaxed">
              {itinerary.summary}
            </p>
          )}
        </div>

        {/* Section Navigation Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-black rounded-xl border border-[#1f1f23] self-start lg:self-auto shrink-0">
          <button
            type="button"
            onClick={() => setActiveTab("itinerary")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === "itinerary"
                ? "bg-white text-black font-semibold shadow"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            Daily Plan
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("hotels")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeTab === "hotels"
                ? "bg-white text-black font-semibold shadow"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            Lodging {hotels.length > 0 && `(${hotels.length})`}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("transport")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeTab === "transport"
                ? "bg-white text-black font-semibold shadow"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            <Plane className="w-3.5 h-3.5" />
            Transit
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("weather")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeTab === "weather"
                ? "bg-white text-black font-semibold shadow"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            <CloudSun className="w-3.5 h-3.5" />
            Weather
          </button>
        </div>
      </div>

      {/* Main Tab Content */}
      {activeTab === "itinerary" && (
        <div className="space-y-6">
          {/* Day Selector Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-neutral-800">
            {days.map((d, index) => {
              const isSelected = index === activeDayIndex;
              return (
                <button
                  key={d.day || index}
                  type="button"
                  onClick={() => setActiveDayIndex(index)}
                  className={`px-4 py-2 rounded-xl text-xs font-mono shrink-0 transition-all border ${
                    isSelected
                      ? "bg-white text-black border-white font-bold shadow-lg"
                      : "bg-black text-neutral-400 border-[#1f1f23] hover:text-white hover:border-neutral-700"
                  }`}
                >
                  Day {d.day || index + 1}
                  {d.theme && (
                    <span className={`block text-[10px] font-sans font-normal truncate max-w-[120px] ${
                      isSelected ? "text-neutral-700" : "text-neutral-400"
                    }`}>
                      {d.theme}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Current Day Header */}
          <div className="p-4 rounded-xl bg-black border border-[#1f1f23]">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-mono uppercase tracking-wider text-neutral-400">
                  Day {currentDay.day} Focus
                </span>
                <h3 className="text-lg font-bold text-white mt-0.5">
                  {currentDay.theme || `Day ${currentDay.day} Exploration`}
                </h3>
              </div>
              <span className="text-xs text-neutral-400 font-mono">
                {currentDay.activities?.length || 0} Scheduled Activities
              </span>
            </div>
            {currentDay.day_summary && (
              <p className="text-xs text-neutral-300 mt-2 leading-relaxed">
                {currentDay.day_summary}
              </p>
            )}
          </div>

          {/* Activities Timeline */}
          <div className="space-y-4 relative before:absolute before:inset-0 before:left-3.5 before:w-px before:bg-[#1f1f23]">
            {currentDay.activities?.map((act, actIdx) => (
              <div key={actIdx} className="relative flex items-start gap-4 pl-8 group">
                {/* Timeline node */}
                <div className="absolute left-2.5 top-2 w-2.5 h-2.5 rounded-full bg-white border-2 border-black group-hover:scale-125 transition-transform" />

                {/* Activity Card */}
                <div className="w-full p-4 rounded-xl bg-black border border-[#1a1a1e] group-hover:border-[#2a2a30] transition-colors">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center gap-1 text-xs font-mono px-2 py-0.5 rounded bg-neutral-900 text-white border border-[#26262a]">
                        <Clock className="w-3 h-3 text-neutral-400" />
                        {act.time}
                      </span>
                      <h4 className="text-sm font-semibold text-white">
                        {act.title}
                      </h4>
                    </div>

                    <div className="flex items-center gap-2 text-xs">
                      {act.activity_type && (
                        <span className="inline-flex items-center gap-1 text-[11px] text-neutral-400 border border-[#222] px-2 py-0.5 rounded-full">
                          <Tag className="w-2.5 h-2.5" />
                          {act.activity_type}
                        </span>
                      )}
                      {act.cost_estimate != null && (
                        <span className="font-mono text-white font-medium text-xs">
                          {act.cost_estimate === 0 ? "Free" : `$${act.cost_estimate}`}
                        </span>
                      )}
                    </div>
                  </div>

                  {act.location && (
                    <div className="flex items-center gap-1.5 text-xs text-neutral-400 mt-2">
                      <MapPin className="w-3 h-3 text-neutral-400 shrink-0" />
                      <span>{act.location}</span>
                    </div>
                  )}

                  <p className="text-xs text-neutral-300 mt-2 leading-relaxed">
                    {act.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Lodging Tab */}
      {activeTab === "hotels" && (
        <div className="space-y-4">
          <div className="text-xs font-mono uppercase tracking-wider text-neutral-400">
            Recommended Accommodations & Neighborhoods
          </div>
          {hotels.length === 0 ? (
            <div className="p-8 text-center text-xs text-neutral-400 font-mono bg-black rounded-xl border border-[#1f1f23]">
              No accommodation options found.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {hotels.map((h, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-black border border-[#1f1f23] space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="text-sm font-semibold text-white">{h.name}</h4>
                      {h.neighborhood && (
                        <div className="flex items-center gap-1 text-xs text-neutral-400 mt-0.5">
                          <MapPin className="w-3 h-3" />
                          <span>{h.neighborhood}</span>
                        </div>
                      )}
                    </div>
                    {(h.price_per_night_usd || h.price_per_night) && (
                      <div className="text-right">
                        <span className="text-sm font-bold text-white font-mono">
                          ${h.price_per_night_usd || h.price_per_night}
                        </span>
                        <span className="text-[10px] text-neutral-400 block">/night</span>
                      </div>
                    )}
                  </div>

                  {h.description && (
                    <p className="text-xs text-neutral-300 leading-relaxed">
                      {h.description}
                    </p>
                  )}

                  {h.location_advantage && (
                    <div className="text-xs text-neutral-400 flex items-start gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-white shrink-0 mt-0.5" />
                      <span>{h.location_advantage}</span>
                    </div>
                  )}

                  {h.amenities && h.amenities.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-2 border-t border-[#1a1a1e]">
                      {h.amenities.map((amenity, aIdx) => (
                        <span key={aIdx} className="text-[10px] px-2 py-0.5 rounded bg-neutral-900 text-neutral-300 border border-[#222]">
                          {amenity}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Transit Tab */}
      {activeTab === "transport" && (
        <div className="space-y-4">
          <div className="text-xs font-mono uppercase tracking-wider text-neutral-400">
            Transit Routes, Passes & Flight Guidance
          </div>

          {!transport ? (
            <div className="p-8 text-center text-xs text-neutral-400 font-mono bg-black rounded-xl border border-[#1f1f23]">
              No transit data synthesized.
            </div>
          ) : (
            <div className="space-y-4">
              {/* Travel Passes */}
              {transport.pass_options && transport.pass_options.length > 0 && (
                <div className="p-4 rounded-xl bg-black border border-[#1f1f23] space-y-3">
                  <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-white">
                    <Ticket className="w-3.5 h-3.5" />
                    Recommended Transit Passes
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {transport.pass_options.map((pass, pIdx) => (
                      <div key={pIdx} className="p-3 rounded-lg bg-neutral-950 border border-[#1a1a1e]">
                        <div className="flex justify-between items-start">
                          <span className="text-xs font-semibold text-white">{pass.name}</span>
                          {pass.estimated_price != null && (
                            <span className="text-xs font-mono text-white font-bold">${pass.estimated_price}</span>
                          )}
                        </div>
                        {pass.coverage && (
                          <p className="text-[11px] text-neutral-400 mt-1">{pass.coverage}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Transit Tips */}
              {transport.tips && transport.tips.length > 0 && (
                <div className="p-4 rounded-xl bg-black border border-[#1f1f23] space-y-2">
                  <div className="text-xs font-mono uppercase tracking-wider text-white">
                    Local Transportation Intelligence
                  </div>
                  <ul className="space-y-1.5 text-xs text-neutral-300">
                    {transport.tips.map((tip, tIdx) => (
                      <li key={tIdx} className="flex items-start gap-2">
                        <span className="text-white font-mono">•</span>
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Weather Tab */}
      {activeTab === "weather" && (
        <div className="space-y-4">
          <div className="text-xs font-mono uppercase tracking-wider text-neutral-400">
            Destination Climate & Packing Intelligence
          </div>

          {!weather ? (
            <div className="p-8 text-center text-xs text-neutral-400 font-mono bg-black rounded-xl border border-[#1f1f23]">
              No weather forecast available.
            </div>
          ) : (
            <div className="space-y-4">
              {/* Daily Forecast */}
              {weather.forecast && weather.forecast.length > 0 && (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                  {weather.forecast.map((wf, wIdx) => (
                    <div key={wIdx} className="p-3 rounded-xl bg-black border border-[#1f1f23] text-center space-y-1">
                      <div className="text-[11px] font-mono text-neutral-400">{wf.date}</div>
                      <CloudSun className="w-5 h-5 mx-auto text-white my-1" />
                      <div className="text-xs font-semibold text-white">{wf.weather_description || "Clear"}</div>
                      <div className="text-xs font-mono text-neutral-300">
                        {wf.temperature_max_celsius != null ? `${wf.temperature_max_celsius}°C` : "--"}
                        {wf.temperature_min_celsius != null && ` / ${wf.temperature_min_celsius}°C`}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Packing Recommendations */}
              {weather.packing_recommendations && weather.packing_recommendations.length > 0 && (
                <div className="p-4 rounded-xl bg-black border border-[#1f1f23] space-y-2">
                  <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-white">
                    <Luggage className="w-3.5 h-3.5" />
                    Recommended Packing List
                  </div>
                  <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-neutral-300">
                    {weather.packing_recommendations.map((item, pIdx) => (
                      <li key={pIdx} className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-white shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
