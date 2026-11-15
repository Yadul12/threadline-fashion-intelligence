"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  ArrowUpRight,
  CheckCircle2,
  Download,
  Info,
} from "lucide-react";
import { apiFetch, formatINR, getExportDownloadUrl } from "@/lib/api";

interface OverviewResponse {
  kpis: {
    active_users_mau: number;
    avg_dau: number;
    estimated_wau: number;
    total_sessions: number;
    search_volume: number;
    total_events_tracked: number;
    pdp_engagement_rate_pct: number;
    add_to_cart_rate_pct: number;
    conversion_rate_pct: number;
    gross_revenue_inr: number;
    total_orders: number;
    avg_order_value_inr: number;
    repeat_purchase_rate_pct: number;
  };
  feature_adoption: Array<{
    feature: string;
    adopted_users: number;
    adoption_rate_pct: number;
  }>;
  daily_trend: Array<{
    date: string;
    dau: number;
    sessions: number;
    searches: number;
    cart_adds: number;
    orders: number;
  }>;
  category_performance: Array<{
    category: string;
    department: string;
    units_sold: number;
    revenue: number;
    avg_return_rate_pct: number;
  }>;
  persona_segments: Array<{
    persona: string;
    users: number;
    sessions: number;
    orders: number;
    revenue: number;
    session_cvr_pct: number;
  }>;
  integrations: {
    database_mode: string;
    mixpanel_configured: boolean;
    mixpanel_status: string;
    gemini_configured: boolean;
    gemini_model: string;
  };
}

interface CohortRow {
  cohort_month: string;
  cohort_size: number;
  retention: Record<string, number>;
}

export default function PMOverviewPage() {
  const [data, setData] = useState<OverviewResponse | null>(null);
  const [cohorts, setCohorts] = useState<CohortRow[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      try {
        const [ov, ch] = await Promise.all([
          apiFetch<OverviewResponse>("/api/analytics/overview"),
          apiFetch<{ cohorts: CohortRow[] }>("/api/analytics/cohorts"),
        ]);
        if (!active) return;
        setData(ov);
        setCohorts(ch.cohorts || []);
      } catch (err) {
        if (active)
          setError(err instanceof Error ? err.message : "Failed to load KPIs");
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-24 bg-white border border-[#E2E0DC] animate-pulse" />
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-28 bg-white border border-[#E2E0DC] animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 border border-[#7C2D26] bg-[#FFF5F2] text-[#7C2D26]">
        <p className="font-mono text-xs uppercase font-semibold">
          Analytics Overview Error
        </p>
        <p className="text-sm mt-1">{error}</p>
      </div>
    );
  }

  const { kpis } = data;

  return (
    <div className="space-y-8 max-w-[1400px]">
      {/* Header & Honest Integration Status */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-5 border-b border-[#E2E0DC]">
        <div>
          <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
            Executive Telemetry &amp; Health
          </p>
          <h1 className="font-serif text-3xl text-[#181615] mt-0.5">
            Product Overview &amp; Cohort Retention
          </h1>
          <p className="text-xs text-[#655E57] mt-1">
            Real-time aggregation over customer sessions, discovery searches,
            product detail engagement, and repeat cohort retention.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <a
            href={getExportDownloadUrl("kpi_report", "xlsx")}
            className="inline-flex items-center gap-1.5 bg-[#181615] text-white px-3.5 py-2 text-xs font-mono uppercase tracking-wider hover:bg-[#7C2D26]"
          >
            <Download className="w-3.5 h-3.5" />
            Export KPI &amp; Cohort Workbook (.XLSX)
          </a>
          <a
            href={getExportDownloadUrl("kpi_report", "csv")}
            className="inline-flex items-center gap-1.5 border border-[#181615] bg-white text-[#181615] px-3.5 py-2 text-xs font-mono uppercase tracking-wider hover:bg-[#F4F3F0]"
          >
            CSV
          </a>
        </div>
      </div>

      {/* Honest Integration Connection Status Banner */}
      <div className="p-4 bg-white border border-[#E2E0DC] grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div className="flex items-start gap-2.5">
          <CheckCircle2 className="w-4 h-4 text-[#2E5A3C] shrink-0 mt-0.5" />
          <div>
            <span className="font-mono uppercase text-[10px] text-[#655E57] block">
              Database Engine
            </span>
            <strong className="font-mono text-[#181615]">
              {data.integrations.database_mode} (4 Tableau Views Ready)
            </strong>
          </div>
        </div>
        <div className="flex items-start gap-2.5">
          <Info className="w-4 h-4 text-[#7C2D26] shrink-0 mt-0.5" />
          <div>
            <span className="font-mono uppercase text-[10px] text-[#655E57] block">
              Event Tracking Adapter
            </span>
            <strong className="font-mono text-[#181615]">
              {data.integrations.mixpanel_status}
            </strong>
          </div>
        </div>
        <div className="flex items-start gap-2.5">
          <Info className="w-4 h-4 text-[#3B4D5E] shrink-0 mt-0.5" />
          <div>
            <span className="font-mono uppercase text-[10px] text-[#655E57] block">
              GenAI Customer Intelligence
            </span>
            <strong className="font-mono text-[#181615]">
              {data.integrations.gemini_configured
                ? `Live (${data.integrations.gemini_model})`
                : "Deterministic SQL Citation Engine (GEMINI_API_KEY unset)"}
            </strong>
          </div>
        </div>
      </div>

      {/* 7 Required Core KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {[
          {
            label: "Active Users (MAU)",
            val: kpis.active_users_mau.toLocaleString(),
            sub: `Avg DAU: ${kpis.avg_dau} · WAU: ${kpis.estimated_wau}`,
          },
          {
            label: "Search Volume",
            val: kpis.search_volume.toLocaleString(),
            sub: `${kpis.total_sessions} Total Sessions`,
          },
          {
            label: "PDP Engagement",
            val: `${kpis.pdp_engagement_rate_pct}%`,
            sub: "Sessions viewing >=1 SKU",
          },
          {
            label: "Add-to-Cart Rate",
            val: `${kpis.add_to_cart_rate_pct}%`,
            sub: "Session-to-Bag rate",
          },
          {
            label: "Conversion Rate",
            val: `${kpis.conversion_rate_pct}%`,
            sub: `${kpis.total_orders} Completed Orders`,
          },
          {
            label: "Gross Revenue",
            val: formatINR(kpis.gross_revenue_inr),
            sub: `AOV: ${formatINR(kpis.avg_order_value_inr)}`,
          },
          {
            label: "Repeat Retention",
            val: `${kpis.repeat_purchase_rate_pct}%`,
            sub: "Multi-order buyer share",
          },
        ].map((metric) => (
          <div
            key={metric.label}
            className="p-4 bg-white border border-[#E2E0DC] flex flex-col justify-between"
          >
            <span className="text-[10px] font-mono uppercase tracking-wider text-[#655E57]">
              {metric.label}
            </span>
            <div className="font-mono text-xl font-semibold text-[#181615] mt-2">
              {metric.val}
            </div>
            <span className="text-[11px] text-[#7D776F] mt-1">
              {metric.sub}
            </span>
          </div>
        ))}
      </div>

      {/* Charts Row: Daily DAU/Search/Cart Velocity & Category Merchandising */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 p-6 bg-white border border-[#E2E0DC]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26]">
                21-Day Behavioural Velocity
              </p>
              <h2 className="font-serif text-xl text-[#181615]">
                Daily Sessions, Searches &amp; Bag Additions
              </h2>
            </div>
            <span className="text-[11px] font-mono text-[#655E57]">
              Total Events: {kpis.total_events_tracked.toLocaleString()}
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={data.daily_trend}
                margin={{ top: 10, right: 10, left: -15, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#ECEAE4" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11, fill: "#655E57" }}
                  tickFormatter={(v: string) => v.slice(5)}
                />
                <YAxis tick={{ fontSize: 11, fill: "#655E57" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#181615",
                    color: "#FAF8F5",
                    border: "none",
                    fontSize: "12px",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="sessions"
                  name="Sessions"
                  stroke="#181615"
                  fill="#E6E0D6"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="searches"
                  name="Searches"
                  stroke="#3B4D5E"
                  fill="#D6E0E8"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="cart_adds"
                  name="Add to Bag"
                  stroke="#9E3B33"
                  fill="#F2D6D2"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="lg:col-span-5 p-6 bg-white border border-[#E2E0DC]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26]">
                Merchandising &amp; Return Exposure
              </p>
              <h2 className="font-serif text-xl text-[#181615]">
                Category Gross Revenue vs. Return Rate
              </h2>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.category_performance}
                layout="vertical"
                margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#ECEAE4" />
                <XAxis
                  type="number"
                  tick={{ fontSize: 10, fill: "#655E57" }}
                  tickFormatter={(v: number) => `₹${Math.round(v / 1000)}k`}
                />
                <YAxis
                  type="category"
                  dataKey="category"
                  width={130}
                  tick={{ fontSize: 10, fill: "#181615" }}
                  tickFormatter={(v: string) => v.split("&")[0].trim()}
                />
                <Tooltip
                  formatter={(val: number) => formatINR(val)}
                  contentStyle={{
                    backgroundColor: "#181615",
                    color: "#FAF8F5",
                    fontSize: "12px",
                  }}
                />
                <Bar dataKey="revenue" name="Gross Revenue" fill="#7C2D26" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Cohort Retention Heatmap Table & Persona Segmentation */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Monthly Cohort Retention Matrix */}
        <div className="lg:col-span-6 p-6 bg-white border border-[#E2E0DC] space-y-4">
          <div>
            <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26]">
              SQL Cohort Analysis
            </p>
            <h2 className="font-serif text-xl text-[#181615]">
              Monthly Customer Retention Matrix (%)
            </h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs border-collapse font-mono">
              <thead>
                <tr className="border-b border-[#E2E0DC] text-[#655E57] text-left">
                  <th className="py-2 pr-3">Cohort</th>
                  <th className="py-2 pr-3">Users</th>
                  <th className="py-2 px-2 text-center">M0</th>
                  <th className="py-2 px-2 text-center">M1</th>
                  <th className="py-2 px-2 text-center">M2</th>
                  <th className="py-2 px-2 text-center">M3</th>
                  <th className="py-2 px-2 text-center">M4</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#EFECE6]">
                {cohorts.map((row) => (
                  <tr key={row.cohort_month}>
                    <td className="py-2.5 pr-3 font-semibold text-[#181615]">
                      {row.cohort_month}
                    </td>
                    <td className="py-2.5 pr-3 text-[#655E57]">
                      {row.cohort_size}
                    </td>
                    {["M0", "M1", "M2", "M3", "M4"].map((mKey) => {
                      const val = row.retention[mKey];
                      const bg =
                        val === undefined
                          ? "bg-transparent"
                          : val >= 80
                          ? "bg-[#7C2D26] text-white"
                          : val >= 40
                          ? "bg-[#D9A79F] text-[#181615]"
                          : val >= 20
                          ? "bg-[#EFE0DC] text-[#181615]"
                          : "bg-[#F8F3F2] text-[#57514B]";
                      return (
                        <td
                          key={mKey}
                          className={`py-2 px-2 text-center border border-white ${bg}`}
                        >
                          {val !== undefined ? `${val}%` : "—"}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* User Segmentation & Feature Adoption */}
        <div className="lg:col-span-6 p-6 bg-white border border-[#E2E0DC] space-y-6">
          <div>
            <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26]">
              Behavioural Segmentation
            </p>
            <h2 className="font-serif text-xl text-[#181615]">
              Performance by Customer Persona Segment
            </h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr className="border-b border-[#E2E0DC] text-[11px] font-mono uppercase text-[#655E57] text-left">
                  <th className="py-2">Persona Segment</th>
                  <th className="py-2 text-right">Users</th>
                  <th className="py-2 text-right">Sessions</th>
                  <th className="py-2 text-right">CVR (%)</th>
                  <th className="py-2 text-right">Revenue</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#EFECE6] font-mono">
                {data.persona_segments.map((seg) => (
                  <tr key={seg.persona}>
                    <td className="py-2.5 font-sans font-medium text-[#181615]">
                      {seg.persona}
                    </td>
                    <td className="py-2.5 text-right">{seg.users}</td>
                    <td className="py-2.5 text-right">{seg.sessions}</td>
                    <td className="py-2.5 text-right text-[#7C2D26] font-semibold">
                      {seg.session_cvr_pct}%
                    </td>
                    <td className="py-2.5 text-right">
                      {formatINR(seg.revenue)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pt-3 border-t border-[#E2E0DC]">
            <p className="text-[10px] font-mono uppercase tracking-widest text-[#655E57] mb-2">
              Discovery Feature Adoption Across Active User Base
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {data.feature_adoption.map((fa) => (
                <div
                  key={fa.feature}
                  className="p-3 bg-[#FAF8F5] border border-[#E2E0DC]"
                >
                  <span className="text-[11px] text-[#57514B] block">
                    {fa.feature}
                  </span>
                  <div className="font-mono text-base font-semibold text-[#181615] mt-1">
                    {fa.adoption_rate_pct}% ({fa.adopted_users})
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Action Links to Deep-Dive Modules */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          href="/pm/search"
          className="p-4 bg-white border border-[#E2E0DC] hover:border-[#181615] flex items-center justify-between"
        >
          <div>
            <p className="text-[10px] font-mono uppercase text-[#7C2D26]">
              Discovery Bottleneck #1
            </p>
            <p className="text-sm font-medium text-[#181615] mt-0.5">
              Inspect Zero-Result Queries &amp; Synonym Expansion
            </p>
          </div>
          <ArrowUpRight className="w-4 h-4 text-[#181615]" />
        </Link>

        <Link
          href="/pm/feedback"
          className="p-4 bg-white border border-[#E2E0DC] hover:border-[#181615] flex items-center justify-between"
        >
          <div>
            <p className="text-[10px] font-mono uppercase text-[#7C2D26]">
              Discovery Bottleneck #2
            </p>
            <p className="text-sm font-medium text-[#181615] mt-0.5">
              Review Size &amp; Fit Complaints in GenAI VoC
            </p>
          </div>
          <ArrowUpRight className="w-4 h-4 text-[#181615]" />
        </Link>

        <Link
          href="/pm/experiments"
          className="p-4 bg-white border border-[#E2E0DC] hover:border-[#181615] flex items-center justify-between"
        >
          <div>
            <p className="text-[10px] font-mono uppercase text-[#2E5A3C]">
              Validated Solution
            </p>
            <p className="text-sm font-medium text-[#181615] mt-0.5">
              View A/B Test Statistical Results (p &lt; 0.05)
            </p>
          </div>
          <ArrowUpRight className="w-4 h-4 text-[#181615]" />
        </Link>
      </div>
    </div>
  );
}
