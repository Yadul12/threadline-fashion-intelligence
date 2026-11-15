"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  ArrowLeft,
  BarChart3,
  Database,
  Download,
  FileSpreadsheet,
  Filter,
  FlaskConical,
  Map,
  MessageSquareWarning,
  SearchCode,
} from "lucide-react";
import { getExportDownloadUrl } from "@/lib/api";

const NAV_ITEMS = [
  {
    href: "/pm",
    label: "Product Overview",
    sub: "KPIs, Cohorts & Segments",
    icon: BarChart3,
  },
  {
    href: "/pm/funnel",
    label: "Customer Funnel",
    sub: "8-Step Conversion & Events",
    icon: Filter,
  },
  {
    href: "/pm/search",
    label: "Search Intelligence",
    sub: "CTR, Zero-Result & Synonyms",
    icon: SearchCode,
  },
  {
    href: "/pm/feedback",
    label: "Feedback & GenAI VoC",
    sub: "Complaints & Traceable AI",
    icon: MessageSquareWarning,
  },
  {
    href: "/pm/experiments",
    label: "Experimentation Centre",
    sub: "A/B Tests, Z-Score & 95% CI",
    icon: FlaskConical,
  },
  {
    href: "/pm/roadmap",
    label: "Product Roadmap & Ops",
    sub: "RICE Scoring, PRD & Jira",
    icon: Map,
  },
  {
    href: "/pm/sql-tableau",
    label: "SQL & Tableau BI Hub",
    sub: "9 Live Queries & Extracts",
    icon: Database,
  },
];

export default function PMWorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen flex bg-[#F4F3F0] text-[#181615] font-sans">
      {/* Compact Purposeful PM Sidebar */}
      <aside className="w-64 bg-[#141413] text-[#E6E2DC] flex flex-col justify-between shrink-0 border-r border-[#2A2826]">
        <div>
          <div className="p-5 border-b border-[#262422]">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs uppercase tracking-[0.2em] text-[#D4B895] font-semibold">
                THREADLINE · PM
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 bg-[#262422] text-[#A59E95] border border-[#383532]">
                v1.0
              </span>
            </div>
            <p className="text-xs text-[#9A948C] mt-1">
              Discovery &amp; CX Intelligence
            </p>
          </div>

          <nav className="p-3 space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const active =
                item.href === "/pm"
                  ? pathname === "/pm"
                  : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-start gap-3 px-3 py-2.5 text-xs transition-colors border-l-2 ${
                    active
                      ? "bg-[#22201E] text-white border-[#9E3B33]"
                      : "text-[#A59E95] hover:text-white hover:bg-[#1C1B19] border-transparent"
                  }`}
                >
                  <Icon
                    className={`w-4 h-4 mt-0.5 shrink-0 ${
                      active ? "text-[#D47A6E]" : "text-[#7A746C]"
                    }`}
                  />
                  <div>
                    <div className="font-medium leading-tight">
                      {item.label}
                    </div>
                    <div className="text-[10px] text-[#7D776F] mt-0.5">
                      {item.sub}
                    </div>
                  </div>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Bottom Quick Exports & Storefront Switch */}
        <div className="p-4 border-t border-[#262422] space-y-3 text-xs">
          <div className="space-y-1.5">
            <p className="text-[10px] font-mono uppercase tracking-wider text-[#8C857B] flex items-center gap-1">
              <FileSpreadsheet className="w-3 h-3" />
              Excel / Sheets Exports
            </p>
            <div className="grid grid-cols-2 gap-1.5 font-mono text-[10px]">
              <a
                href={getExportDownloadUrl("kpi_report", "xlsx")}
                className="px-2 py-1.5 bg-[#22201E] hover:bg-[#2E2B28] text-[#E6E2DC] border border-[#383532] flex items-center justify-between"
              >
                <span>KPIs .XLSX</span>
                <Download className="w-3 h-3" />
              </a>
              <a
                href={getExportDownloadUrl("jira_backlog", "csv")}
                className="px-2 py-1.5 bg-[#22201E] hover:bg-[#2E2B28] text-[#E6E2DC] border border-[#383532] flex items-center justify-between"
              >
                <span>Jira .CSV</span>
                <Download className="w-3 h-3" />
              </a>
            </div>
          </div>

          <Link
            href="/"
            className="w-full flex items-center justify-center gap-2 bg-[#7C2D26] hover:bg-[#9E3B33] text-white py-2 px-3 text-xs font-mono uppercase tracking-wider transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Return to Storefront
          </Link>
        </div>
      </aside>

      {/* Main Analytics Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Institutional Status Bar */}
        <header className="h-14 bg-white border-b border-[#E2E0DC] px-6 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-xs">
            <span className="inline-flex items-center gap-1.5 font-mono text-[11px] uppercase px-2.5 py-0.5 bg-[#F4F3F0] border border-[#D5D2CC] text-[#181615]">
              <Activity className="w-3.5 h-3.5 text-[#7C2D26]" />
              Synthetic Cohort Dataset (180 Users · 620 Sessions · 480 Searches)
            </span>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={getExportDownloadUrl("tableau_extract", "xlsx")}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 border border-[#D5D2CC] bg-[#FAF9F6] hover:border-[#181615] text-xs font-mono text-[#181615]"
            >
              <Download className="w-3.5 h-3.5 text-[#7C2D26]" />
              Download Tableau BI Extracts (.XLSX)
            </a>
          </div>
        </header>

        <main className="flex-1 p-6 lg:p-8 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
