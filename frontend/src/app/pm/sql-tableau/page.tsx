"use client";

import React, { useEffect, useState } from "react";
import { Code2, Database, Download, Table } from "lucide-react";
import { apiFetch, getExportDownloadUrl } from "@/lib/api";

interface SqlQueriesResponse {
  available_queries: Array<{
    key: string;
    title: string;
    description: string;
  }>;
  active_query: {
    query_key: string;
    title: string;
    description: string;
    sql: string;
    columns: string[];
    row_count: number;
    rows: Array<Record<string, unknown>>;
  };
}

interface TableauViewsResponse {
  view_name: string;
  description: string;
  available_views: Array<{ name: string; description: string }>;
  columns: string[];
  row_count: number;
  rows: Array<Record<string, unknown>>;
}

export default function PMSqlAndTableauPage() {
  const [selectedQueryKey, setSelectedQueryKey] =
    useState<string>("conversion_funnel");
  const [sqlData, setSqlData] = useState<SqlQueriesResponse | null>(null);
  const [selectedViewName, setSelectedViewName] = useState<string>(
    "vw_tableau_daily_funnel"
  );
  const [viewData, setViewData] = useState<TableauViewsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let active = true;
    async function loadSql() {
      setLoading(true);
      try {
        const [qRes, vRes] = await Promise.all([
          apiFetch<SqlQueriesResponse>(
            `/api/analytics/sql-queries?query_key=${encodeURIComponent(
              selectedQueryKey
            )}`
          ),
          apiFetch<TableauViewsResponse>(
            `/api/analytics/tableau-views?view_name=${encodeURIComponent(
              selectedViewName
            )}`
          ),
        ]);
        if (!active) return;
        setSqlData(qRes);
        setViewData(vRes);
      } finally {
        if (active) setLoading(false);
      }
    }
    loadSql();
    return () => {
      active = false;
    };
  }, [selectedQueryKey, selectedViewName]);

  return (
    <div className="space-y-8 max-w-[1400px]">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-5 border-b border-[#E2E0DC]">
        <div>
          <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
            Relational PostgreSQL / SQLite Engine &amp; Tableau BI Views
          </p>
          <h1 className="font-serif text-3xl text-[#181615] mt-0.5">
            SQL Analytics &amp; Tableau BI Hub
          </h1>
          <p className="text-xs text-[#655E57] mt-1">
            Execute all 9 production analytical SQL queries live against the
            database and inspect the 4 materialized Tableau BI views.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <a
            href={getExportDownloadUrl("tableau_extract", "xlsx")}
            className="inline-flex items-center gap-1.5 bg-[#181615] text-white px-3.5 py-2 text-xs font-mono uppercase tracking-wider hover:bg-[#7C2D26]"
          >
            <Download className="w-3.5 h-3.5" />
            Download 4-Sheet Tableau Extract (.XLSX)
          </a>
          <a
            href={getExportDownloadUrl("tableau_extract", "csv")}
            className="inline-flex items-center gap-1.5 border border-[#181615] bg-white text-[#181615] px-3 py-2 text-xs font-mono uppercase tracking-wider"
          >
            Daily Funnel .CSV
          </a>
        </div>
      </div>

      {/* Section 1: 9 Live Analytical SQL Queries */}
      {sqlData && (
        <div className="p-6 bg-white border border-[#E2E0DC] space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-[#E2E0DC]">
            <div>
              <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26] flex items-center gap-1.5">
                <Code2 className="w-3.5 h-3.5" />
                Live SQL Execution Engine (`deliverables/sql/analytical_queries.sql`)
              </p>
              <h2 className="font-serif text-2xl text-[#181615]">
                {sqlData.active_query.title}
              </h2>
              <p className="text-xs text-[#655E57]">
                {sqlData.active_query.description}
              </p>
            </div>

            <select
              value={selectedQueryKey}
              onChange={(e) => setSelectedQueryKey(e.target.value)}
              className="border border-[#181615] bg-[#FAF8F5] px-3 py-2 text-xs font-mono text-[#181615]"
            >
              {sqlData.available_queries.map((q) => (
                <option key={q.key} value={q.key}>
                  {q.title}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-5 bg-[#141413] text-[#E6E2DC] p-4 overflow-x-auto border border-[#2A2826]">
              <div className="text-[10px] font-mono uppercase text-[#D4B895] mb-2">
                Executed SQL Statement
              </div>
              <pre className="text-[11px] font-mono leading-relaxed whitespace-pre-wrap">
                {sqlData.active_query.sql}
              </pre>
            </div>

            <div className="lg:col-span-7 overflow-x-auto border border-[#E2E0DC]">
              <div className="p-2.5 bg-[#FAF8F5] border-b border-[#E2E0DC] flex items-center justify-between text-xs font-mono">
                <span>
                  Query Result Set ({sqlData.active_query.row_count} rows)
                </span>
                {loading && <span>Executing...</span>}
              </div>
              <div className="max-h-80 overflow-y-auto">
                <table className="w-full text-xs font-mono border-collapse">
                  <thead>
                    <tr className="bg-[#F4F3F0] border-b border-[#E2E0DC] text-[10px] uppercase text-[#655E57] text-left">
                      {sqlData.active_query.columns.map((col) => (
                        <th key={col} className="p-2.5 whitespace-nowrap">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#EFECE6]">
                    {sqlData.active_query.rows.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-[#FAF8F5]">
                        {sqlData.active_query.columns.map((col) => (
                          <td
                            key={col}
                            className="p-2.5 whitespace-nowrap text-[#181615]"
                          >
                            {String(row[col] ?? "—")}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Section 2: Tableau Views Inspector */}
      {viewData && (
        <div className="p-6 bg-white border border-[#E2E0DC] space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-[#E2E0DC]">
            <div>
              <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26] flex items-center gap-1.5">
                <Table className="w-3.5 h-3.5" />
                Materialized SQL Views for Tableau (`002_tableau_views.sql`)
              </p>
              <h2 className="font-serif text-2xl text-[#181615]">
                {viewData.view_name}
              </h2>
              <p className="text-xs text-[#655E57]">{viewData.description}</p>
            </div>

            <div className="flex flex-wrap gap-2">
              {viewData.available_views.map((v) => (
                <button
                  key={v.name}
                  type="button"
                  onClick={() => setSelectedViewName(v.name)}
                  className={`px-3 py-1.5 text-xs font-mono border transition-colors ${
                    selectedViewName === v.name
                      ? "bg-[#181615] text-white border-[#181615]"
                      : "bg-[#FAF8F5] text-[#181615] border-[#D5D2CC]"
                  }`}
                >
                  {v.name}
                </button>
              ))}
            </div>
          </div>

          <div className="overflow-x-auto max-h-80 border border-[#E2E0DC]">
            <table className="w-full text-xs font-mono border-collapse">
              <thead>
                <tr className="bg-[#F4F3F0] border-b border-[#E2E0DC] text-[10px] uppercase text-[#655E57] text-left">
                  {viewData.columns.map((c) => (
                    <th key={c} className="p-2.5 whitespace-nowrap">
                      {c}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#EFECE6]">
                {viewData.rows.slice(0, 25).map((r, idx) => (
                  <tr key={idx}>
                    {viewData.columns.map((c) => (
                      <td key={c} className="p-2.5 whitespace-nowrap">
                        {String(r[c] ?? "—")}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-4 bg-[#FAF8F5] border border-[#E2E0DC] text-xs space-y-1">
            <strong className="font-mono uppercase text-[#181615] flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-[#7C2D26]" />
              Tableau Workbook &amp; Connection Status (Honest Reporting)
            </strong>
            <p className="text-[#57514B]">
              A ready-to-open Tableau Workbook (
              <code>
                deliverables/tableau/THREADLINE_Discovery_Intelligence.twb
              </code>
              ) and pre-extracted CSV/XLSX data sources (
              <code>deliverables/tableau/extracts/</code>) are generated on
              disk. Connect Tableau Desktop directly to PostgreSQL or open the{" "}
              <code>.twb</code> workbook against the local extract files.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
