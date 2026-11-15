"use client";

import React, { useCallback, useEffect, useState } from "react";
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
  Download,
  FileUp,
  MessageSquareText,
  Sparkles,
} from "lucide-react";
import { API_BASE_URL, apiFetch, getExportDownloadUrl } from "@/lib/api";

interface SupportingRecord {
  review_id: string;
  product_id: string;
  product_sku: string;
  product_title: string;
  rating: number;
  verbatim_quote: string;
}

interface PainPointCluster {
  id: string;
  complaint_category: string;
  record_count: number;
  severity: string;
  affected_skus: string[];
  issue_summary: string;
  recommended_product_change: string;
  linked_roadmap_jira: string;
  supporting_records: SupportingRecord[];
}

interface FeedbackDashboardResponse {
  summary: {
    total_reviews: number;
    filtered_count: number;
    avg_rating: number;
    sentiment_distribution: Array<{
      sentiment: string;
      count: number;
      share_pct: number;
    }>;
    fit_consensus: Array<{
      fit_verdict: string;
      count: number;
      share_pct: number;
    }>;
  };
  complaint_categories: Array<{
    category: string;
    count: number;
    share_pct: number;
  }>;
  category_complaint_matrix: Array<{
    category_name: string;
    complaint_category: string;
    review_count: number;
    avg_rating: number;
  }>;
  sentiment_trend: Array<{
    period: string;
    negative_count: number;
    neutral_count: number;
    positive_count: number;
    total_count: number;
  }>;
  reviews: Array<{
    id: string;
    product_id: string;
    product_title: string;
    product_sku: string;
    category_name: string;
    user_name: string;
    persona_segment: string;
    rating: number;
    title: string;
    comment_text: string;
    sentiment: string;
    complaint_category: string;
    fit_feedback: string;
    created_at: string;
  }>;
  genai_intelligence: {
    provider_status: string;
    model_used: string;
    records_analyzed: number;
    executive_summary: string;
    recurring_pain_points: PainPointCluster[];
  };
}

export default function PMFeedbackIntelligencePage() {
  const [complaintFilter, setComplaintFilter] = useState<string>("all");
  const [sentimentFilter, setSentimentFilter] = useState<string>("all");
  const [data, setData] = useState<FeedbackDashboardResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Custom GenAI prompt question
  const [customPrompt, setCustomPrompt] = useState<string>("");
  const [runningAi, setRunningAi] = useState<boolean>(false);

  // Research file import state
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        complaint_category: complaintFilter,
        sentiment: sentimentFilter,
      });
      const res = await apiFetch<FeedbackDashboardResponse>(
        `/api/feedback?${params.toString()}`
      );
      setData(res);
    } finally {
      setLoading(false);
    }
  }, [complaintFilter, sentimentFilter]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const handleRunCustomAi = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!data) return;
    setRunningAi(true);
    try {
      const aiRes = await apiFetch<
        FeedbackDashboardResponse["genai_intelligence"]
      >("/api/feedback/analyze", {
        method: "POST",
        body: JSON.stringify({
          complaint_filter: complaintFilter,
          custom_question: customPrompt.trim() || undefined,
        }),
      });
      setData({ ...data, genai_intelligence: aiRes });
    } finally {
      setRunningAi(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    setUploadStatus("Uploading and indexing research records...");
    try {
      const res = await fetch(`${API_BASE_URL}/api/exports/import-feedback`, {
        method: "POST",
        body: formData,
      });
      const body = await res.json();
      if (!res.ok) throw new Error(body.detail || "Upload failed");
      setUploadStatus(
        `Imported ${body.rows_imported} research row(s) (${body.sample_review_ids.join(
          ", "
        )}). Refreshing synthesis...`
      );
      await loadDashboard();
    } catch (err) {
      setUploadStatus(
        `Upload error: ${err instanceof Error ? err.message : "Failed"}`
      );
    }
  };

  return (
    <div className="space-y-8 max-w-[1400px]">
      {/* Header & Exports / Import */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-5 border-b border-[#E2E0DC]">
        <div>
          <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
            Voice-of-Customer (VoC) &amp; Traceable GenAI Synthesis
          </p>
          <h1 className="font-serif text-3xl text-[#181615] mt-0.5">
            Customer Feedback Intelligence
          </h1>
          <p className="text-xs text-[#655E57] mt-1">
            Clusters verified customer reviews by complaint taxonomy and traces
            every recommendation to supporting review IDs.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <label className="cursor-pointer inline-flex items-center gap-1.5 border border-[#181615] bg-white hover:bg-[#F4F3F0] text-[#181615] px-3 py-2 text-xs font-mono uppercase tracking-wider">
            <FileUp className="w-3.5 h-3.5 text-[#7C2D26]" />
            Import Research (.CSV / .XLSX)
            <input
              type="file"
              accept=".csv,.xlsx"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>

          <a
            href={getExportDownloadUrl("customer_feedback", "xlsx")}
            className="inline-flex items-center gap-1.5 bg-[#181615] text-white px-3.5 py-2 text-xs font-mono uppercase tracking-wider hover:bg-[#7C2D26]"
          >
            <Download className="w-3.5 h-3.5" />
            Export Feedback (.XLSX)
          </a>
        </div>
      </div>

      {uploadStatus && (
        <div className="p-3 bg-[#F6EFE4] border border-[#D4B895] text-xs font-mono text-[#181615]">
          {uploadStatus}
        </div>
      )}

      {loading && (
        <div className="h-96 bg-white border border-[#E2E0DC] animate-pulse" />
      )}

      {data && !loading && (
        <>
          {/* GenAI / Deterministic Evidence Synthesis Panel */}
          <div className="p-6 bg-white border-2 border-[#181615] space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-[#E2E0DC]">
              <div>
                <span className="inline-flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-widest px-2.5 py-1 bg-[#181615] text-[#D4B895]">
                  <Sparkles className="w-3 h-3" />
                  Server-Side VoC Synthesis ·{" "}
                  {data.genai_intelligence.provider_status}
                </span>
                <h2 className="font-serif text-2xl text-[#181615] mt-2">
                  Traceable Customer Pain Points &amp; Product Recommendations
                </h2>
              </div>

              <div className="text-right font-mono text-xs text-[#655E57]">
                <div>Engine: {data.genai_intelligence.model_used}</div>
                <div>
                  Grounded in {data.genai_intelligence.records_analyzed} SQL
                  Review Records
                </div>
              </div>
            </div>

            {/* Executive Summary */}
            <div className="p-4 bg-[#FAF8F5] border border-[#E2E0DC]">
              <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26] mb-1">
                Executive Synthesis (Zero Fabricated Quotes)
              </p>
              <p className="text-sm text-[#181615] leading-relaxed">
                {data.genai_intelligence.executive_summary}
              </p>

              {/* Interactive Custom Question Prompt */}
              <form
                onSubmit={handleRunCustomAi}
                className="mt-3 pt-3 border-t border-[#E6E0D6] flex flex-col sm:flex-row gap-2"
              >
                <input
                  type="text"
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  placeholder="Ask a specific PM research question over the review dataset (e.g., 'Which SKUs have the worst waistband sizing issues?')..."
                  className="flex-1 bg-white border border-[#D5CEC2] px-3 py-1.5 text-xs"
                />
                <button
                  type="submit"
                  disabled={runningAi}
                  className="bg-[#7C2D26] hover:bg-[#9E3B33] text-white px-4 py-1.5 text-xs font-mono uppercase tracking-wider shrink-0"
                >
                  {runningAi ? "Synthesizing..." : "Re-Run Synthesis"}
                </button>
              </form>
            </div>

            {/* Traceable Pain Point Clusters */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {data.genai_intelligence.recurring_pain_points.map((pp) => (
                <div
                  key={pp.id}
                  className="p-5 border border-[#E2E0DC] bg-[#FAF9F6] flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="px-2 py-0.5 bg-[#7C2D26] text-white uppercase text-[10px]">
                        {pp.severity} · {pp.complaint_category} (
                        {pp.record_count} Reviews)
                      </span>
                      <Link
                        href="/pm/roadmap"
                        className="text-[#7C2D26] underline"
                      >
                        Jira: {pp.linked_roadmap_jira}
                      </Link>
                    </div>

                    <p className="text-xs text-[#181615] font-medium leading-relaxed">
                      {pp.issue_summary}
                    </p>

                    <div className="p-3 bg-white border border-[#E6E0D6] text-xs">
                      <strong className="font-mono uppercase text-[10px] text-[#2E5A3C] block">
                        Recommended Product Change:
                      </strong>
                      <span className="text-[#181615]">
                        {pp.recommended_product_change}
                      </span>
                    </div>
                  </div>

                  {/* Supporting Review Record Citations */}
                  <div className="space-y-2 pt-2 border-t border-[#E6E0D6]">
                    <p className="text-[10px] font-mono uppercase text-[#655E57]">
                      Supporting Database Records (Affected SKUs:{" "}
                      {pp.affected_skus.join(", ")})
                    </p>
                    {pp.supporting_records.map((cite) => (
                      <div
                        key={cite.review_id}
                        className="p-2.5 bg-white border border-[#E2E0DC] text-[11px]"
                      >
                        <div className="flex items-center justify-between font-mono text-[10px] text-[#7C2D26]">
                          <Link
                            href={`/products/${cite.product_id}`}
                            className="underline"
                          >
                            Record {cite.review_id} · {cite.product_sku} (
                            {cite.rating}★)
                          </Link>
                          <span>{cite.product_title}</span>
                        </div>
                        <p className="text-[#57514B] italic mt-1">
                          “{cite.verbatim_quote}”
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Complaint Categories Chart & Sentiment Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-7 p-6 bg-white border border-[#E2E0DC]">
              <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26]">
                Complaint Taxonomy Distribution
              </p>
              <h3 className="font-serif text-xl text-[#181615] mb-4">
                Feedback Volume by Topic Category
              </h3>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={data.complaint_categories}
                    layout="vertical"
                    margin={{ top: 5, right: 20, left: 30, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#ECEAE4" />
                    <XAxis
                      type="number"
                      tick={{ fontSize: 11, fill: "#655E57" }}
                    />
                    <YAxis
                      type="category"
                      dataKey="category"
                      width={140}
                      tick={{ fontSize: 11, fill: "#181615" }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#181615",
                        color: "#FAF8F5",
                        fontSize: "12px",
                      }}
                    />
                    <Bar dataKey="count" name="Review Count" fill="#7C2D26" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="lg:col-span-5 p-6 bg-white border border-[#E2E0DC] space-y-5">
              <div>
                <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26]">
                  Sentiment &amp; Fit Breakdown
                </p>
                <h3 className="font-serif text-xl text-[#181615]">
                  Verified Buyer Sentiment &amp; Fit Verdict
                </h3>
              </div>

              <div className="grid grid-cols-3 gap-3 font-mono text-xs">
                {data.summary.sentiment_distribution.map((s) => (
                  <div
                    key={s.sentiment}
                    className="p-3 bg-[#FAF8F5] border border-[#E2E0DC]"
                  >
                    <span className="uppercase text-[10px] text-[#655E57] block">
                      {s.sentiment}
                    </span>
                    <strong className="text-lg text-[#181615]">
                      {s.share_pct}%
                    </strong>
                    <span className="block text-[10px] text-[#7D776F]">
                      {s.count} reviews
                    </span>
                  </div>
                ))}
              </div>

              <div>
                <p className="text-[10px] font-mono uppercase text-[#655E57] mb-2">
                  Cross-Category Complaint Matrix
                </p>
                <div className="max-h-40 overflow-y-auto border border-[#E2E0DC]">
                  <table className="w-full text-xs font-mono border-collapse">
                    <thead>
                      <tr className="bg-[#FAF8F5] border-b border-[#E2E0DC] text-[10px] text-left text-[#655E57]">
                        <th className="p-2">Category</th>
                        <th className="p-2">Complaint</th>
                        <th className="p-2 text-right">Count</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#EFECE6]">
                      {data.category_complaint_matrix.slice(0, 8).map((m, i) => (
                        <tr key={i}>
                          <td className="p-2 truncate max-w-[140px]">
                            {m.category_name.split("&")[0]}
                          </td>
                          <td className="p-2 text-[#7C2D26]">
                            {m.complaint_category}
                          </td>
                          <td className="p-2 text-right font-semibold">
                            {m.review_count}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          {/* Filterable Customer Review Explorer */}
          <div className="p-6 bg-white border border-[#E2E0DC] space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <MessageSquareText className="w-4 h-4 text-[#7C2D26]" />
                <h3 className="font-serif text-xl text-[#181615]">
                  Individual Customer Feedback Records ({data.reviews.length})
                </h3>
              </div>

              <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
                <select
                  value={complaintFilter}
                  onChange={(e) => setComplaintFilter(e.target.value)}
                  className="border border-[#D5D2CC] bg-[#FAF8F5] px-3 py-1.5"
                >
                  <option value="all">All Complaint Categories</option>
                  <option value="Size and fit">Size and fit</option>
                  <option value="Search relevance">Search relevance</option>
                  <option value="Product images">Product images</option>
                  <option value="Product quality">Product quality</option>
                  <option value="Pricing">Pricing</option>
                  <option value="Delivery experience">
                    Delivery experience
                  </option>
                  <option value="Checkout experience">
                    Checkout experience
                  </option>
                  <option value="None (Praise)">None (Praise)</option>
                </select>

                <select
                  value={sentimentFilter}
                  onChange={(e) => setSentimentFilter(e.target.value)}
                  className="border border-[#D5D2CC] bg-[#FAF8F5] px-3 py-1.5"
                >
                  <option value="all">All Sentiments</option>
                  <option value="negative">Negative</option>
                  <option value="neutral">Neutral</option>
                  <option value="positive">Positive</option>
                </select>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="border-b border-[#E2E0DC] text-[10px] font-mono uppercase text-[#655E57] text-left">
                    <th className="py-2 pr-3">ID</th>
                    <th className="py-2 pr-3">SKU / Product</th>
                    <th className="py-2 pr-3">Customer</th>
                    <th className="py-2 pr-3">Rating</th>
                    <th className="py-2 pr-3">Topic / Fit</th>
                    <th className="py-2">Verbatim Feedback</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EFECE6]">
                  {data.reviews.slice(0, 20).map((r) => (
                    <tr key={r.id} className="align-top">
                      <td className="py-3 pr-3 font-mono text-[11px] text-[#7C2D26]">
                        {r.id}
                      </td>
                      <td className="py-3 pr-3 font-mono text-[11px]">
                        <Link
                          href={`/products/${r.product_id}`}
                          className="font-semibold text-[#181615] hover:underline block"
                        >
                          {r.product_sku}
                        </Link>
                        <span className="text-[#655E57]">
                          {r.product_title}
                        </span>
                      </td>
                      <td className="py-3 pr-3">
                        <div className="font-medium text-[#181615]">
                          {r.user_name}
                        </div>
                        <div className="text-[10px] font-mono text-[#655E57]">
                          {r.persona_segment}
                        </div>
                      </td>
                      <td className="py-3 pr-3 font-mono font-semibold text-[#7C2D26]">
                        {r.rating}★
                      </td>
                      <td className="py-3 pr-3 font-mono text-[11px]">
                        <span className="block text-[#181615]">
                          {r.complaint_category}
                        </span>
                        <span className="text-[#655E57]">
                          Fit: {r.fit_feedback}
                        </span>
                      </td>
                      <td className="py-3 max-w-md">
                        <div className="font-semibold text-[#181615]">
                          {r.title}
                        </div>
                        <p className="text-[#57514B] mt-0.5 leading-relaxed">
                          {r.comment_text}
                        </p>
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
