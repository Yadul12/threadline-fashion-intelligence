"use client";

import React, { useCallback, useEffect, useState } from "react";
import {
  CheckSquare,
  Download,
  FileText,
  Layers,
  Map,
  Users,
} from "lucide-react";
import { apiFetch, getExportDownloadUrl } from "@/lib/api";

interface RoadmapItem {
  id: string;
  jira_key: string;
  epic_name: string;
  title: string;
  problem_evidence: string;
  user_story: string;
  acceptance_criteria: string[];
  reach_score: number;
  impact_score: number;
  confidence_pct: number;
  effort_person_weeks: number;
  rice_score: number;
  customer_impact: string;
  business_impact: string;
  status: string;
  sprint: string;
  owner: string;
}

export default function PMRoadmapAndJiraPage() {
  const [items, setItems] = useState<RoadmapItem[]>([]);
  const [formula, setFormula] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<
    "rice" | "prd" | "personas" | "ceremonies"
  >("rice");
  const [selectedItem, setSelectedItem] = useState<RoadmapItem | null>(null);

  const loadRoadmap = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch<{ formula: string; items: RoadmapItem[] }>(
        "/api/roadmap"
      );
      setItems(res.items || []);
      setFormula(res.formula || "");
      if (res.items?.length && !selectedItem) {
        setSelectedItem(res.items[0]);
      }
    } finally {
      setLoading(false);
    }
  }, [selectedItem]);

  useEffect(() => {
    loadRoadmap();
  }, [loadRoadmap]);

  const handleStatusChange = async (item: RoadmapItem, nextStatus: string) => {
    const updated = await apiFetch<RoadmapItem>(`/api/roadmap/${item.id}`, {
      method: "PATCH",
      body: JSON.stringify({
        reach_score: item.reach_score,
        impact_score: item.impact_score,
        confidence_pct: item.confidence_pct,
        effort_person_weeks: item.effort_person_weeks,
        status: nextStatus,
      }),
    });
    setItems((prev) =>
      prev.map((it) => (it.id === updated.id ? updated : it))
    );
    if (selectedItem?.id === updated.id) {
      setSelectedItem(updated);
    }
  };

  return (
    <div className="space-y-8 max-w-[1400px]">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-5 border-b border-[#E2E0DC]">
        <div>
          <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
            Agile Product Operations, RICE Prioritization &amp; Jira Backlog
          </p>
          <h1 className="font-serif text-3xl text-[#181615] mt-0.5">
            Product Roadmap &amp; PRD Documentation
          </h1>
          <p className="text-xs text-[#655E57] mt-1">{formula}</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <a
            href={getExportDownloadUrl("jira_backlog", "csv")}
            className="inline-flex items-center gap-1.5 bg-[#181615] text-white px-3.5 py-2 text-xs font-mono uppercase tracking-wider hover:bg-[#7C2D26]"
          >
            <Download className="w-3.5 h-3.5" />
            Export Jira Backlog (.CSV)
          </a>
          <a
            href={getExportDownloadUrl("jira_backlog", "xlsx")}
            className="inline-flex items-center gap-1.5 border border-[#181615] bg-white text-[#181615] px-3.5 py-2 text-xs font-mono uppercase tracking-wider"
          >
            .XLSX
          </a>
        </div>
      </div>

      {/* Sub-Navigation Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-[#E2E0DC] pb-3 font-mono text-xs">
        {[
          {
            id: "rice" as const,
            label: "1. RICE Backlog & Jira User Stories",
            icon: Map,
          },
          {
            id: "prd" as const,
            label: "2. Product Requirements Document (PRD)",
            icon: FileText,
          },
          {
            id: "personas" as const,
            label: "3. User Personas & Journey Map",
            icon: Users,
          },
          {
            id: "ceremonies" as const,
            label: "4. Sprint Planning, Release Notes & Retro",
            icon: Layers,
          },
        ].map((t) => {
          const Icon = t.icon;
          return (
            <button
              key={t.id}
              type="button"
              onClick={() => setActiveTab(t.id)}
              className={`inline-flex items-center gap-2 px-4 py-2 border transition-colors ${
                activeTab === t.id
                  ? "bg-[#181615] text-white border-[#181615]"
                  : "bg-white text-[#181615] border-[#D5D2CC] hover:border-[#181615]"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {t.label}
            </button>
          );
        })}
      </div>

      {loading && (
        <div className="h-80 bg-white border border-[#E2E0DC] animate-pulse" />
      )}

      {/* TAB 1: RICE Prioritization Table & User Story Inspector */}
      {!loading && activeTab === "rice" && (
        <div className="space-y-6">
          <div className="p-6 bg-white border border-[#E2E0DC] overflow-x-auto">
            <h2 className="font-serif text-xl text-[#181615] mb-4">
              RICE-Ranked Feature Backlog (Click Any Story to Inspect Acceptance
              Criteria)
            </h2>

            <table className="w-full text-xs border-collapse font-mono">
              <thead>
                <tr className="border-b border-[#E2E0DC] text-[10px] uppercase text-[#655E57] text-left">
                  <th className="py-2.5 pr-2">Jira Key</th>
                  <th className="py-2.5 pr-3">Epic &amp; Feature Title</th>
                  <th className="py-2.5 text-right">Reach</th>
                  <th className="py-2.5 text-right">Impact</th>
                  <th className="py-2.5 text-right">Conf %</th>
                  <th className="py-2.5 text-right">Effort (Wks)</th>
                  <th className="py-2.5 text-right">RICE Score</th>
                  <th className="py-2.5 pl-3">Sprint / Status</th>
                  <th className="py-2.5">Owner</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#EFECE6]">
                {items.map((it) => (
                  <tr
                    key={it.id}
                    onClick={() => setSelectedItem(it)}
                    className={`cursor-pointer transition-colors ${
                      selectedItem?.id === it.id
                        ? "bg-[#F6EFE4]"
                        : "hover:bg-[#FAF8F5]"
                    }`}
                  >
                    <td className="py-3 pr-2 font-semibold text-[#7C2D26]">
                      {it.jira_key}
                    </td>
                    <td className="py-3 pr-3 font-sans">
                      <div className="text-[10px] font-mono uppercase text-[#655E57]">
                        {it.epic_name}
                      </div>
                      <div className="font-semibold text-[#181615]">
                        {it.title}
                      </div>
                    </td>
                    <td className="py-3 text-right">
                      {it.reach_score.toLocaleString()}
                    </td>
                    <td className="py-3 text-right">{it.impact_score}x</td>
                    <td className="py-3 text-right">{it.confidence_pct}%</td>
                    <td className="py-3 text-right">
                      {it.effort_person_weeks}w
                    </td>
                    <td className="py-3 text-right font-semibold text-base text-[#181615]">
                      {it.rice_score}
                    </td>
                    <td
                      className="py-3 pl-3"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <select
                        value={it.status}
                        onChange={(e) =>
                          handleStatusChange(it, e.target.value)
                        }
                        className="border border-[#D5D2CC] bg-white px-2 py-1 text-[11px]"
                      >
                        <option value="Shipped">Shipped</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Next Sprint">Next Sprint</option>
                        <option value="Planned Q1">Planned Q1</option>
                      </select>
                      <span className="block text-[10px] text-[#655E57] mt-0.5">
                        {it.sprint}
                      </span>
                    </td>
                    <td className="py-3 text-[11px] text-[#57514B]">
                      {it.owner}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Selected Story Deep-Dive */}
          {selectedItem && (
            <div className="p-6 bg-white border-2 border-[#181615] grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-7 space-y-4">
                <div className="flex items-center gap-2 font-mono text-xs">
                  <span className="px-2.5 py-0.5 bg-[#7C2D26] text-white font-semibold">
                    {selectedItem.jira_key}
                  </span>
                  <span className="uppercase text-[#655E57]">
                    Epic: {selectedItem.epic_name}
                  </span>
                </div>

                <h3 className="font-serif text-2xl text-[#181615]">
                  {selectedItem.title}
                </h3>

                <div className="p-4 bg-[#F6EFE4] border border-[#D4B895]">
                  <span className="text-[10px] font-mono uppercase text-[#7C2D26] block">
                    Agile User Story
                  </span>
                  <p className="font-serif text-lg text-[#181615] mt-1">
                    “{selectedItem.user_story}”
                  </p>
                </div>

                <div className="text-xs space-y-1">
                  <strong className="font-mono uppercase text-[#181615] block">
                    Quantitative &amp; VoC Problem Evidence:
                  </strong>
                  <p className="text-[#57514B] leading-relaxed">
                    {selectedItem.problem_evidence}
                  </p>
                </div>
              </div>

              <div className="lg:col-span-5 space-y-4 border-t lg:border-t-0 lg:border-l border-[#E2E0DC] pt-4 lg:pt-0 lg:pl-6">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-[#2E5A3C] flex items-center gap-1.5 font-semibold">
                    <CheckSquare className="w-3.5 h-3.5" />
                    Measurable Acceptance Criteria (Definition of Done)
                  </span>
                  <ul className="space-y-2 mt-3 text-xs text-[#181615]">
                    {selectedItem.acceptance_criteria.map((ac, idx) => (
                      <li
                        key={idx}
                        className="p-2.5 bg-[#FAF8F5] border border-[#E2E0DC] flex items-start gap-2"
                      >
                        <span className="font-mono text-[#7C2D26] font-semibold">
                          0{idx + 1}.
                        </span>
                        <span>{ac}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="p-3 bg-[#FAF8F5] border border-[#E2E0DC] text-xs font-mono">
                  <span className="text-[#655E57] block text-[10px] uppercase">
                    Projected Business Impact
                  </span>
                  <strong className="text-[#181615]">
                    {selectedItem.business_impact}
                  </strong>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Complete Product Requirements Document (PRD) */}
      {activeTab === "prd" && (
        <div className="p-8 bg-white border border-[#E2E0DC] space-y-6 max-w-4xl">
          <div className="border-b border-[#E2E0DC] pb-4">
            <span className="text-[11px] font-mono uppercase text-[#7C2D26]">
              Document ID: PRD-2026-Q4-DISCOVERY · Author: Ananya Rao (PM)
            </span>
            <h2 className="font-serif text-3xl text-[#181615] mt-1">
              PRD: Semantic Search Expansion &amp; Verified Buyer Fit
              Intelligence
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs leading-relaxed text-[#57514B]">
            <div className="space-y-2">
              <h3 className="font-mono uppercase text-[#181615] font-semibold">
                1. Executive Problem Statement
              </h3>
              <p>
                Behavioural funnel telemetry across 620 sessions and 480
                searches reveals two primary conversion bottlenecks on
                THREADLINE: (a) <strong>14.2% of searches return zero results</strong>{" "}
                when shoppers use occasion or climate phrasing (e.g.,{" "}
                <em>“haldi guest outfit”</em>,{" "}
                <em>“breathable summer office wear”</em>), causing a 54% search
                abandonment rate; and (b) <strong>41% of PDP viewers drop off</strong>{" "}
                before adding to bag due to sizing uncertainty on structured
                non-stretch garments (38% of negative reviews cite{" "}
                <em>Size and fit</em>).
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="font-mono uppercase text-[#181615] font-semibold">
                2. Objectives &amp; Key Results (OKRs)
              </h3>
              <ul className="list-disc pl-4 space-y-1 text-[#181615]">
                <li>
                  Reduce Zero-Result Search Rate from <strong>14.2%</strong> to{" "}
                  <strong>&lt; 3.5%</strong> within 30 days of rollout.
                </li>
                <li>
                  Increase Search-to-PDP Click-Through Rate (CTR) from{" "}
                  <strong>58%</strong> to <strong>&gt; 72%</strong>.
                </li>
                <li>
                  Lift Session Add-to-Cart Rate by <strong>+18% relative</strong>{" "}
                  (validated via Experiment `exp_semantic_size_fit_filters` at p
                  &lt; 0.05).
                </li>
                <li>
                  Reduce size-mismatch exchange rate on tailored linen &amp;
                  selvedge denim SKUs by <strong>20%</strong>.
                </li>
              </ul>
            </div>
          </div>

          <div className="space-y-3 pt-4 border-t border-[#E2E0DC] text-xs">
            <h3 className="font-mono uppercase text-[#181615] font-semibold">
              3. Solution Scope &amp; Technical Architecture
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-[#FAF8F5] border border-[#E2E0DC]">
                <strong className="font-mono text-[#7C2D26] block mb-1">
                  Pillar A: Semantic Synonym Engine
                </strong>
                <p className="text-[#57514B]">
                  Maps cultural occasion, climate, and silhouette queries to
                  catalog `occasion`, `fabric`, and `subcategory` tokens with
                  transparent UI match callouts.
                </p>
              </div>
              <div className="p-4 bg-[#FAF8F5] border border-[#E2E0DC]">
                <strong className="font-mono text-[#7C2D26] block mb-1">
                  Pillar B: Sticky Size &amp; Fit Facet Bar
                </strong>
                <p className="text-[#57514B]">
                  One-tap `In My Size` filter pill pre-bound to user profile +
                  Fit Profile facet pills (`True to Size`, `Runs Small - Size
                  Up`).
                </p>
              </div>
              <div className="p-4 bg-[#FAF8F5] border border-[#E2E0DC]">
                <strong className="font-mono text-[#7C2D26] block mb-1">
                  Pillar C: PDP Fit Consensus Bar
                </strong>
                <p className="text-[#57514B]">
                  Aggregates verified buyer `fit_feedback` records from SQL in
                  real time directly above the PDP size selector.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: User Personas & Customer Journey Map */}
      {activeTab === "personas" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              {
                name: "Ananya Rao (29, Bengaluru)",
                segment: "Fit-Conscious Minimalist",
                goal: "Build a breathable European linen capsule wardrobe for architect studio workdays without having to exchange sizes.",
                frustration:
                  "Structured non-stretch trouser waistbands run smaller than generic size charts; hates surprise exchange delays.",
                preferred_channels: "Editorial Newsletter · Desktop & iOS",
              },
              {
                name: "Meera Kapoor (26, Jaipur)",
                segment: "Occasion Explorer",
                goal: "Find contemporary silk and pleated dresses for destination wedding events using occasion search terms.",
                frustration:
                  "Searching 'haldi guest outfit' or 'festive cocktail maxi' returns zero results on rigid keyword engines.",
                preferred_channels: "Instagram Paid Social · Mobile iOS",
              },
              {
                name: "Vikram Sethi (34, Mumbai)",
                segment: "Editorial Curator",
                goal: "Invest in Italian slub linen shirts, unstructured hopsack blazers, and Goodyear/Blake leather loafers.",
                frustration:
                  "Wants complete fabric GSM weight, mill provenance, and cross-category outfit pairing inspiration.",
                preferred_channels: "Organic Search · Mobile iOS",
              },
              {
                name: "Kabir Deshmukh (24, Pune)",
                segment: "Value Trend-Seeker",
                goal: "Acquire Japanese selvedge denim and chore jackets during seasonal tier promotions.",
                frustration:
                  "Unclear promo eligibility and shipping thresholds until the final checkout screen.",
                preferred_channels: "Influencer Referral · Mobile Android",
              },
            ].map((p) => (
              <div
                key={p.name}
                className="p-5 bg-white border border-[#E2E0DC] space-y-3 text-xs"
              >
                <span className="px-2 py-0.5 bg-[#181615] text-[#D4B895] font-mono text-[10px] uppercase">
                  {p.segment}
                </span>
                <h3 className="font-serif text-xl text-[#181615]">{p.name}</h3>
                <p className="text-[#57514B]">
                  <strong className="text-[#181615]">Core Goal:</strong>{" "}
                  {p.goal}
                </p>
                <p className="text-[#7C2D26]">
                  <strong>Pain Point:</strong> {p.frustration}
                </p>
                <p className="font-mono text-[10px] text-[#655E57] pt-2 border-t border-[#EFECE6]">
                  {p.preferred_channels}
                </p>
              </div>
            ))}
          </div>

          <div className="p-6 bg-white border border-[#E2E0DC] space-y-4">
            <h3 className="font-serif text-xl text-[#181615]">
              End-to-End Customer Discovery Journey Map
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
              {[
                {
                  stage: "1. Trigger & Landing",
                  action: "Arrives via Editorial Lookbook or IG reel (`homepage_viewed`).",
                  emotion: "Inspired, curious about fabric drape.",
                  intervention: "Editorial Hero + Persona-aware Size Edit.",
                },
                {
                  stage: "2. Search & Filter",
                  action: "Searches 'breathable summer office wear' + filters Size S.",
                  emotion: "Frustrated if 0 results appear.",
                  intervention: "THRD-101 Synonym Expansion + THRD-102 Fit Bar.",
                },
                {
                  stage: "3. PDP Evaluation",
                  action: "Inspects Solstice Linen Trouser (`product_viewed`).",
                  emotion: "Anxious whether non-stretch waist runs small.",
                  intervention: "THRD-103 Inline Buyer Fit Consensus (68% Runs Small).",
                },
                {
                  stage: "4. Bag & Validation",
                  action: "Adds Size M (sized up per guidance) (`add_to_cart`).",
                  emotion: "Checking shipping fee & delivery timeline.",
                  intervention: "THRD-106 Free Shipping Bar + City-Tier ETA.",
                },
                {
                  stage: "5. Post-Purchase VoC",
                  action: "Receives order (`order_placed`) & leaves verified review.",
                  emotion: "Satisfied first-time fit; high repeat intent.",
                  intervention: "THRD-108 GenAI VoC pipeline updates SKU fit score.",
                },
              ].map((st) => (
                <div
                  key={st.stage}
                  className="p-4 bg-[#FAF8F5] border border-[#E2E0DC] space-y-2"
                >
                  <strong className="font-mono text-[#7C2D26] block">
                    {st.stage}
                  </strong>
                  <p className="text-[#181615]">{st.action}</p>
                  <p className="text-[#655E57] italic">Mood: {st.emotion}</p>
                  <p className="text-[11px] font-mono text-[#2E5A3C] pt-1 border-t border-[#E6E0D6]">
                    PM Fix: {st.intervention}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Sprint Planning, Release Notes, Stakeholder Log & Retrospective */}
      {activeTab === "ceremonies" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 text-xs">
          <div className="p-6 bg-white border border-[#E2E0DC] space-y-4">
            <span className="text-[10px] font-mono uppercase text-[#7C2D26]">
              Scrum Execution · 2-Week Cadence
            </span>
            <h3 className="font-serif text-2xl text-[#181615]">
              Sprint 13–15 Release Milestones &amp; Release Notes
            </h3>
            <div className="space-y-3">
              <div className="p-3.5 bg-[#FAF8F5] border border-[#E2E0DC]">
                <strong className="font-mono text-[#2E5A3C]">
                  Release v1.3 (Sprint 13 — Shipped):
                </strong>
                <p className="text-[#57514B] mt-1">
                  Delivered THRD-103 (PDP Verified Buyer Fit Spectrum), THRD-104
                  (Zero-Result Recovery Edit), and THRD-108 (Server-Side GenAI
                  VoC Synthesis with deterministic SQL fallback).
                </p>
              </div>
              <div className="p-3.5 bg-[#F6EFE4] border border-[#D4B895]">
                <strong className="font-mono text-[#7C2D26]">
                  Release v1.4 (Sprint 14 — Active A/B Rollout):
                </strong>
                <p className="text-[#181615] mt-1">
                  THRD-101 (Semantic Occasion &amp; Fabric Synonym Expansion)
                  and THRD-102 (Sticky In-My-Size &amp; Fit-Profile Bar) live in
                  Experiment `exp_semantic_size_fit_filters` showing
                  statistically significant +45% relative lift in Add-to-Bag.
                </p>
              </div>
              <div className="p-3.5 bg-[#FAF8F5] border border-[#E2E0DC]">
                <strong className="font-mono text-[#181615]">
                  Release v1.5 (Sprint 15 — Next Sprint Committed):
                </strong>
                <p className="text-[#57514B] mt-1">
                  THRD-105 (Natural Daylight Color Swatches) and THRD-106
                  (City-Tier ETA &amp; Promo Calculator in Bag).
                </p>
              </div>
            </div>
          </div>

          <div className="p-6 bg-white border border-[#E2E0DC] space-y-4">
            <span className="text-[10px] font-mono uppercase text-[#7C2D26]">
              Stakeholder Alignment &amp; Sprint 13 Retrospective
            </span>
            <h3 className="font-serif text-2xl text-[#181615]">
              Stakeholder Feedback Log &amp; Retro Action Items
            </h3>
            <div className="space-y-3">
              <div className="p-3.5 bg-[#FAF8F5] border border-[#E2E0DC]">
                <strong className="font-mono text-[#181615]">
                  VP of Merchandising (Stakeholder Review):
                </strong>
                <p className="text-[#57514B] mt-1">
                  “Flagging high-return SKUs like TL-LIN-002 and TL-DEN-001 via
                  buyer fit badges rather than hiding them protected our gross
                  margin while setting accurate sizing expectations.”
                </p>
              </div>
              <div className="p-3.5 bg-[#FAF8F5] border border-[#E2E0DC]">
                <strong className="font-mono text-[#181615]">
                  Data Science &amp; Analytics Lead:
                </strong>
                <p className="text-[#57514B] mt-1">
                  “Require strict sample-size power gating in the
                  Experimentation Centre so exploratory tests (`n &lt; target`)
                  are never prematurely declared winners.” →{" "}
                  <span className="text-[#2E5A3C] font-mono">
                    Implemented in `experiment_service.py`
                  </span>
                </p>
              </div>
              <div className="p-3.5 bg-[#FAF8F5] border border-[#E2E0DC]">
                <strong className="font-mono text-[#181615]">
                  Sprint Retrospective — What Went Well / To Improve:
                </strong>
                <p className="text-[#57514B] mt-1">
                  <strong>Went Well:</strong> Dual-write event adapter ensured
                  zero analytics blind spots when local environments run without
                  Mixpanel tokens. <br />
                  <strong>Action Item:</strong> Expand occasion synonym coverage
                  to regional festive queries in Sprint 15.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
