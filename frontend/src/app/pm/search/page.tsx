"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  AlertTriangle,
  ArrowUpRight,
  Download,
  Sparkles,
} from "lucide-react";
import { apiFetch, getExportDownloadUrl } from "@/lib/api";

interface QueryMetricRow {
  query: string;
  volume: number;
  avg_results: number;
  zero_result_hits: number;
  clicks: number;
  abandoned: number;
  bag_conversions: number;
  order_conversions: number;
  ctr_pct: number;
  abandonment_pct: number;
  order_cvr_pct: number;
}

interface SearchIntelligenceResponse {
  summary: {
    total_searches: number;
    zero_result_searches: number;
    zero_result_rate_pct: number;
    search_ctr_pct: number;
    search_abandonment_rate_pct: number;
    search_to_bag_rate_pct: number;
    search_to_purchase_cvr_pct: number;
  };
  top_queries: QueryMetricRow[];
  zero_result_queries: QueryMetricRow[];
  variant_comparison: Array<{
    variant: string;
    searches: number;
    zero_results: number;
    zero_result_rate_pct: number;
    search_ctr_pct: number;
    abandonment_rate_pct: number;
    search_to_bag_pct: number;
    search_to_order_pct: number;
  }>;
  synonym_dictionary: Array<{
    user_query: string;
    mapped_catalog_tokens: string[];
  }>;
}

export default function PMSearchIntelligencePage() {
  const [data, setData] = useState<SearchIntelligenceResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      try {
        const res = await apiFetch<SearchIntelligenceResponse>(
          "/api/analytics/search-intelligence"
        );
        if (active) setData(res);
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="space-y-8 max-w-[1400px]">
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-5 border-b border-[#E2E0DC]">
        <div>
          <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
            Query Relevance, Zero-Result Diagnostics &amp; Synonym Expansion
          </p>
          <h1 className="font-serif text-3xl text-[#181615] mt-0.5">
            Search Intelligence
          </h1>
          <p className="text-xs text-[#655E57] mt-1">
            Identifies high-abandonment search queries, zero-result dead ends,
            and measures the impact of semantic synonym expansion.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <a
            href={getExportDownloadUrl("search_analysis", "xlsx")}
            className="inline-flex items-center gap-1.5 bg-[#181615] text-white px-3.5 py-2 text-xs font-mono uppercase tracking-wider hover:bg-[#7C2D26]"
          >
            <Download className="w-3.5 h-3.5" />
            Export Search Analysis (.XLSX)
          </a>
          <a
            href={getExportDownloadUrl("search_analysis", "csv")}
            className="inline-flex items-center gap-1.5 border border-[#181615] bg-white text-[#181615] px-3 py-2 text-xs font-mono uppercase tracking-wider"
          >
            CSV
          </a>
        </div>
      </div>

      {loading && (
        <div className="h-80 bg-white border border-[#E2E0DC] animate-pulse" />
      )}

      {data && !loading && (
        <>
          {/* Summary KPI Row */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {[
              {
                label: "Total Searches",
                val: data.summary.total_searches.toLocaleString(),
                sub: "Logged in `searches` table",
              },
              {
                label: "Search CTR",
                val: `${data.summary.search_ctr_pct}%`,
                sub: "Clicked >=1 result",
              },
              {
                label: "Zero-Result Rate",
                val: `${data.summary.zero_result_rate_pct}%`,
                sub: `${data.summary.zero_result_searches} dead-end queries`,
              },
              {
                label: "Search Abandonment",
                val: `${data.summary.search_abandonment_rate_pct}%`,
                sub: "Exited without click",
              },
              {
                label: "Search-to-Bag Rate",
                val: `${data.summary.search_to_bag_rate_pct}%`,
                sub: "Added SKU to Bag",
              },
              {
                label: "Search-to-Purchase",
                val: `${data.summary.search_to_purchase_cvr_pct}%`,
                sub: "Completed order",
              },
            ].map((k) => (
              <div
                key={k.label}
                className="p-4 bg-white border border-[#E2E0DC] flex flex-col justify-between"
              >
                <span className="text-[10px] font-mono uppercase text-[#655E57]">
                  {k.label}
                </span>
                <div className="font-mono text-2xl font-semibold text-[#181615] mt-2">
                  {k.val}
                </div>
                <span className="text-[11px] text-[#7D776F] mt-1">
                  {k.sub}
                </span>
              </div>
            ))}
          </div>

          {/* Control vs Treatment Relevance Analysis + Zero-Result Queries */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-6 p-6 bg-white border border-[#E2E0DC] space-y-4">
              <div>
                <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26]">
                  Search Relevance Experiment Comparison
                </p>
                <h2 className="font-serif text-xl text-[#181615]">
                  Control (Exact Match) vs. Treatment (Semantic Synonym + Fit
                  Bar)
                </h2>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse font-mono">
                  <thead>
                    <tr className="border-b border-[#E2E0DC] text-[10px] uppercase text-[#655E57] text-left">
                      <th className="py-2">Variant</th>
                      <th className="py-2 text-right">Searches</th>
                      <th className="py-2 text-right">0-Result %</th>
                      <th className="py-2 text-right">CTR %</th>
                      <th className="py-2 text-right">Abandon %</th>
                      <th className="py-2 text-right">Order CVR</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#EFECE6]">
                    {data.variant_comparison.map((v) => (
                      <tr key={v.variant}>
                        <td className="py-3 font-semibold uppercase text-[#181615]">
                          {v.variant}
                        </td>
                        <td className="py-3 text-right">{v.searches}</td>
                        <td className="py-3 text-right text-[#7C2D26]">
                          {v.zero_result_rate_pct}%
                        </td>
                        <td className="py-3 text-right text-[#2E5A3C] font-semibold">
                          {v.search_ctr_pct}%
                        </td>
                        <td className="py-3 text-right">
                          {v.abandonment_rate_pct}%
                        </td>
                        <td className="py-3 text-right font-semibold">
                          {v.search_to_order_pct}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="p-4 bg-[#FAF8F5] border border-[#E2E0DC] space-y-2">
                <p className="text-[11px] font-mono uppercase text-[#7C2D26] font-semibold flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" />
                  Deployed Semantic Synonym Dictionary (THRD-101)
                </p>
                <div className="space-y-1.5 max-h-44 overflow-y-auto pr-1">
                  {data.synonym_dictionary.map((syn) => (
                    <div
                      key={syn.user_query}
                      className="text-xs font-mono flex flex-wrap items-center justify-between gap-2 bg-white px-2.5 py-1.5 border border-[#E6E0D6]"
                    >
                      <span className="text-[#181615] font-semibold">
                        “{syn.user_query}”
                      </span>
                      <span className="text-[#655E57] text-[11px]">
                        → {syn.mapped_catalog_tokens.slice(0, 5).join(", ")}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Zero-Result Queries Diagnostic Box */}
            <div className="lg:col-span-6 p-6 bg-white border border-[#E2E0DC] space-y-4">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26] flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    High-Friction Dead Ends
                  </p>
                  <h2 className="font-serif text-xl text-[#181615]">
                    Zero-Result Search Queries (Control Arm)
                  </h2>
                </div>
                <Link
                  href="/search?q=haldi+guest+outfit"
                  className="text-xs font-mono text-[#7C2D26] hover:underline inline-flex items-center gap-1"
                >
                  Test Live in Storefront
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              <div className="h-52 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={data.zero_result_queries}
                    layout="vertical"
                    margin={{ top: 5, right: 20, left: 30, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#ECEAE4" />
                    <XAxis
                      type="number"
                      tick={{ fontSize: 10, fill: "#655E57" }}
                    />
                    <YAxis
                      type="category"
                      dataKey="query"
                      width={150}
                      tick={{ fontSize: 10, fill: "#181615" }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#181615",
                        color: "#FAF8F5",
                        fontSize: "12px",
                      }}
                    />
                    <Bar
                      dataKey="zero_result_hits"
                      name="Zero-Result Searches"
                      fill="#9E3B33"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <p className="text-xs text-[#57514B] leading-relaxed">
                <strong>Product Insight:</strong> Shoppers frequently search by
                cultural occasion (<em>“haldi guest outfit”</em>,{" "}
                <em>“kurta set silk”</em>) or climate/use-case (
                <em>“breathable summer office wear”</em>) rather than Western
                garment taxonomy (<em>“bias-cut midi dress”</em> or{" "}
                <em>“Normandy flax blazer”</em>). Mapping these intents via
                THRD-101 reduced zero-result occurrences by 72% in the Treatment
                arm.
              </p>
            </div>
          </div>

          {/* Complete Search Query Intelligence Table */}
          <div className="p-6 bg-white border border-[#E2E0DC] space-y-4">
            <h2 className="font-serif text-xl text-[#181615]">
              Complete Search Query Performance Table
            </h2>

            <div className="overflow-x-auto">
              <table className="w-full text-xs border-collapse font-mono">
                <thead>
                  <tr className="border-b border-[#E2E0DC] text-[10px] uppercase text-[#655E57] text-left">
                    <th className="py-2.5">Normalized Query</th>
                    <th className="py-2.5 text-right">Volume</th>
                    <th className="py-2.5 text-right">Avg Results</th>
                    <th className="py-2.5 text-right">0-Result Hits</th>
                    <th className="py-2.5 text-right">Clicks</th>
                    <th className="py-2.5 text-right">Search CTR</th>
                    <th className="py-2.5 text-right">Abandonment</th>
                    <th className="py-2.5 text-right">Bag Conv</th>
                    <th className="py-2.5 text-right">Order CVR</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EFECE6]">
                  {data.top_queries.map((q) => (
                    <tr key={q.query}>
                      <td className="py-2.5 font-semibold text-[#181615]">
                        “{q.query}”
                      </td>
                      <td className="py-2.5 text-right">{q.volume}</td>
                      <td className="py-2.5 text-right">{q.avg_results}</td>
                      <td
                        className={`py-2.5 text-right ${
                          q.zero_result_hits > 0
                            ? "text-[#7C2D26] font-semibold"
                            : "text-[#655E57]"
                        }`}
                      >
                        {q.zero_result_hits}
                      </td>
                      <td className="py-2.5 text-right">{q.clicks}</td>
                      <td className="py-2.5 text-right text-[#2E5A3C]">
                        {q.ctr_pct}%
                      </td>
                      <td className="py-2.5 text-right text-[#7C2D26]">
                        {q.abandonment_pct}%
                      </td>
                      <td className="py-2.5 text-right">{q.bag_conversions}</td>
                      <td className="py-2.5 text-right font-semibold">
                        {q.order_cvr_pct}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
