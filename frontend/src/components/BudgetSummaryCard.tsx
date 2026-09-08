"use client";

import React from "react";
import { 
  Wallet, 
  CheckCircle, 
  AlertCircle, 
  Sparkles, 
  Plane, 
  Building, 
  Utensils, 
  Bus, 
  Ticket 
} from "lucide-react";
import { BudgetInfo } from "@/types/travel";

interface BudgetSummaryCardProps {
  budget: BudgetInfo | null | undefined;
  requestedBudget?: number | null;
}

export const BudgetSummaryCard: React.FC<BudgetSummaryCardProps> = ({
  budget,
  requestedBudget,
}) => {
  if (!budget) {
    return (
      <div className="w-full bg-[#0a0a0a] border border-[#1f1f23] rounded-2xl p-6 text-center text-neutral-400 font-mono text-sm">
        No budget data generated yet.
      </div>
    );
  }

  const numTotal = typeof budget.total === "number" ? budget.total : parseFloat(String(budget.total)) || 0;
  const numFlights = typeof budget.flights === "number" ? budget.flights : parseFloat(String(budget.flights)) || 0;
  const numAccommodation = typeof budget.accommodation === "number" ? budget.accommodation : parseFloat(String(budget.accommodation)) || 0;
  const numFood = typeof budget.food === "number" ? budget.food : parseFloat(String(budget.food)) || 0;
  const numTransportation = typeof budget.transportation === "number" ? budget.transportation : parseFloat(String(budget.transportation)) || 0;
  const numActivities = typeof budget.activities === "number" ? budget.activities : parseFloat(String(budget.activities)) || 0;

  const targetBudget = requestedBudget || (budget.remaining != null ? numTotal + Number(budget.remaining) : numTotal);
  const percentUsed = targetBudget > 0 ? Math.min(Math.round((numTotal / targetBudget) * 100), 100) : 100;
  const isOverBudget = budget.status === "over_budget";

  const breakdownItems = [
    { label: "Flights", value: numFlights, icon: <Plane className="w-4 h-4" /> },
    { label: "Accommodation", value: numAccommodation, icon: <Building className="w-4 h-4" /> },
    { label: "Food & Dining", value: numFood, icon: <Utensils className="w-4 h-4" /> },
    { label: "Local Transit", value: numTransportation, icon: <Bus className="w-4 h-4" /> },
    { label: "Activities & Entry", value: numActivities, icon: <Ticket className="w-4 h-4" /> },
  ];

  return (
    <div className="w-full bg-[#0a0a0a] border border-[#1f1f23] rounded-2xl p-6 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-[#1f1f23]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-black border border-[#2a2a30] flex items-center justify-center text-white">
            <Wallet className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-white font-semibold text-base tracking-tight">
              Budget & Financial Analysis
            </h3>
            <p className="text-xs text-neutral-400">
              Evaluated by WaypointZero Budget Agent
            </p>
          </div>
        </div>

        {/* Status Pill */}
        <div>
          {isOverBudget ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-white text-black border border-white">
              <AlertCircle className="w-3.5 h-3.5" />
              OVER BUDGET
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-black text-white border border-neutral-600">
              <CheckCircle className="w-3.5 h-3.5 text-white" />
              WITHIN BUDGET
            </span>
          )}
        </div>
      </div>

      {/* Overview Numbers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-black border border-[#1f1f23]">
          <div className="text-xs text-neutral-400 uppercase tracking-wider font-mono">
            Total Estimated Cost
          </div>
          <div className="text-2xl font-bold text-white mt-1">
            ${numTotal.toLocaleString()} <span className="text-xs text-neutral-400 font-normal">{budget.currency || "USD"}</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-black border border-[#1f1f23]">
          <div className="text-xs text-neutral-400 uppercase tracking-wider font-mono">
            Allocated Budget
          </div>
          <div className="text-2xl font-bold text-neutral-200 mt-1">
            {targetBudget > 0 ? `$${targetBudget.toLocaleString()}` : "Flexible"}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-black border border-[#1f1f23]">
          <div className="text-xs text-neutral-400 uppercase tracking-wider font-mono">
            {isOverBudget ? "Over Budget By" : "Surplus / Savings"}
          </div>
          <div className="text-2xl font-bold text-white mt-1">
            {budget.remaining != null
              ? `$${Math.abs(Number(budget.remaining)).toLocaleString()}`
              : `$${Math.abs(targetBudget - numTotal).toLocaleString()}`}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      {targetBudget > 0 && (
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-neutral-400 font-mono">
            <span>Budget Utilization</span>
            <span>{percentUsed}%</span>
          </div>
          <div className="w-full h-2 rounded-full bg-neutral-900 border border-[#222] overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                isOverBudget ? "bg-white" : "bg-neutral-300"
              }`}
              style={{ width: `${Math.min(percentUsed, 100)}%` }}
            />
          </div>
        </div>
      )}

      {/* Itemized Categories */}
      <div>
        <div className="text-xs uppercase tracking-wider text-neutral-400 font-mono mb-3">
          Itemized Allocation
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {breakdownItems.map((item, idx) => (
            <div
              key={idx}
              className="p-3 rounded-xl bg-black border border-[#1a1a1e] flex flex-col justify-between"
            >
              <div className="flex items-center gap-2 text-neutral-400 text-xs">
                {item.icon}
                <span className="truncate">{item.label}</span>
              </div>
              <div className="text-sm font-semibold text-white mt-2 font-mono">
                ${item.value.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cost Saving Tips */}
      {budget.cost_saving_tips && budget.cost_saving_tips.length > 0 && (
        <div className="p-4 rounded-xl bg-black border border-[#1f1f23] space-y-2">
          <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-white font-mono font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-white" />
            Budget Agent Recommendations & Optimization Tips
          </div>
          <ul className="space-y-1.5 text-xs text-neutral-300">
            {budget.cost_saving_tips.map((tip, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-white font-mono font-bold">•</span>
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
