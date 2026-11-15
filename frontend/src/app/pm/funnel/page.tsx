"use client";

import React, { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, Filter } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface FunnelStep {
  event_name: string;
  step_label: string;
  description: string;
  sessions: number;
  conversion_from_top_pct: number;
  step_to_step_conversion_pct: number;
  drop_off_pct: number;
  is_micro_conversion: boolean;
}

interface FunnelResponse {
  filters_applied: {
    device_type: string;
    acquisition_channel: string;
    experiment_variant: string;
  };
  steps: FunnelStep[];
  by_device: Array<{
    device_type: string;
    sessions: number;
    pdp_sessions: number;
    cart_sessions: number;
    order_sessions: number;
    cvr_pct: number;
  }>;
  by_channel: Array<{
    acquisition_channel: string;
    sessions: number;
    search_sessions: number;
    cart_sessions: number;
    order_sessions: number;
    cvr_pct: number;
  }>;
}

interface RecentEventsResponse {
  canonical_events: string[];
  mixpanel_configured: boolean;
  events: Array<{
    id: string;
    event_name: string;
    user_id: string;
    session_id: string;
    product_id: string | null;
    category: string | null;
    price: number | null;
    brand: string | null;
    device_type: string;
    acquisition_channel: string;
    experiment_variant: string | null;
    mixpanel_dispatched: boolean;
    event_timestamp: string;
  }>;
}

export default function PMFunnelAnalyticsPage() {
  const [deviceFilter, setDeviceFilter] = useState<string>("all");
  const [channelFilter, setChannelFilter] = useState<string>("all");
  const [variantFilter, setVariantFilter] = useState<string>("all");

  const [funnel, setFunnel] = useState<FunnelResponse | null>(null);
  const [recentEvents, setRecentEvents] =
    useState<RecentEventsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      try {
        const params = new URLSearchParams({
          device_type: deviceFilter,
          acquisition_channel: channelFilter,
          experiment_variant: variantFilter,
        });
        const [fRes, eRes] = await Promise.all([
          apiFetch<FunnelResponse>(`/api/analytics/funnel?${params.toString()}`),
          apiFetch<RecentEventsResponse>("/api/events/recent?limit=15"),
        ]);
        if (!active) return;
        setFunnel(fRes);
        setRecentEvents(eRes);
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, [deviceFilter, channelFilter, variantFilter]);

  return (
    <div className="space-y-8 max-w-[1400px]">
      {/* Header & Segment Slicers */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-5 border-b border-[#E2E0DC]">
        <div>
          <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
            8-Step Journey Diagnostics &amp; Mixpanel Schema
          </p>
          <h1 className="font-serif text-3xl text-[#181615] mt-0.5">
            Customer Funnel Analytics
          </h1>
          <p className="text-xs text-[#655E57] mt-1">
            Slice conversion progression by device platform, acquisition
            channel, and A/B experiment arm.
          </p>
        </div>

        {/* Slicer Controls */}
        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          <span className="inline-flex items-center gap-1 text-[#655E57] mr-1">
            <Filter className="w-3.5 h-3.5" />
            Slice Funnel:
          </span>

          <select
            value={deviceFilter}
            onChange={(e) => setDeviceFilter(e.target.value)}
            className="border border-[#D5D2CC] bg-white px-3 py-1.5 text-xs"
          >
            <option value="all">All Devices</option>
            <option value="mobile_ios">Mobile iOS</option>
            <option value="mobile_android">Mobile Android</option>
            <option value="desktop_web">Desktop Web</option>
          </select>

          <select
            value={channelFilter}
            onChange={(e) => setChannelFilter(e.target.value)}
            className="border border-[#D5D2CC] bg-white px-3 py-1.5 text-xs"
          >
            <option value="all">All Acquisition Channels</option>
            <option value="organic_search">Organic Search</option>
            <option value="paid_social_ig">Paid Social (IG)</option>
            <option value="editorial_newsletter">Editorial Newsletter</option>
            <option value="influencer_referral">Influencer Referral</option>
            <option value="direct">Direct</option>
          </select>

          <select
            value={variantFilter}
            onChange={(e) => setVariantFilter(e.target.value)}
            className="border border-[#D5D2CC] bg-white px-3 py-1.5 text-xs"
          >
            <option value="all">All Experiment Variants</option>
            <option value="control">Control Variant Only</option>
            <option value="treatment">Treatment Variant Only</option>
          </select>
        </div>
      </div>

      {loading && (
        <div className="h-96 bg-white border border-[#E2E0DC] animate-pulse" />
      )}

      {funnel && !loading && (
        <>
          {/* 8-Step Funnel Chart + Step Conversion Table */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-6 p-6 bg-white border border-[#E2E0DC]">
              <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26]">
                Session Progression
              </p>
              <h2 className="font-serif text-xl text-[#181615] mb-4">
                8-Stage Discovery-to-Purchase Funnel
              </h2>

              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={funnel.steps}
                    layout="vertical"
                    margin={{ top: 5, right: 25, left: 30, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#ECEAE4" />
                    <XAxis
                      type="number"
                      tick={{ fontSize: 11, fill: "#655E57" }}
                    />
                    <YAxis
                      type="category"
                      dataKey="step_label"
                      width={150}
                      tick={{ fontSize: 11, fill: "#181615" }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#181615",
                        color: "#FAF8F5",
                        fontSize: "12px",
                      }}
                    />
                    <Bar dataKey="sessions" name="Unique Sessions">
                      {funnel.steps.map((entry, idx) => (
                        <Cell
                          key={entry.event_name}
                          fill={
                            entry.is_micro_conversion
                              ? "#8C847B"
                              : idx >= 5
                              ? "#7C2D26"
                              : "#181615"
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="lg:col-span-6 p-6 bg-white border border-[#E2E0DC] overflow-x-auto">
              <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26]">
                Step-by-Step Drop-Off Diagnostics
              </p>
              <h2 className="font-serif text-xl text-[#181615] mb-4">
                Stage Conversion &amp; Friction Points
              </h2>

              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="border-b border-[#E2E0DC] text-[10px] font-mono uppercase text-[#655E57] text-left">
                    <th className="py-2">Funnel Stage</th>
                    <th className="py-2 text-right">Sessions</th>
                    <th className="py-2 text-right">% of Top</th>
                    <th className="py-2 text-right">Step Conv</th>
                    <th className="py-2 text-right">Drop-Off</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EFECE6] font-mono">
                  {funnel.steps.map((s) => (
                    <tr key={s.event_name}>
                      <td className="py-2.5 font-sans">
                        <div className="font-medium text-[#181615]">
                          {s.step_label}
                        </div>
                        <div className="text-[10px] font-mono text-[#7D776F]">
                          {s.event_name}
                        </div>
                      </td>
                      <td className="py-2.5 text-right font-semibold">
                        {s.sessions}
                      </td>
                      <td className="py-2.5 text-right">
                        {s.conversion_from_top_pct}%
                      </td>
                      <td className="py-2.5 text-right text-[#2E5A3C]">
                        {s.step_to_step_conversion_pct}%
                      </td>
                      <td className="py-2.5 text-right text-[#7C2D26]">
                        {s.drop_off_pct > 0 ? `-${s.drop_off_pct}%` : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Device & Channel Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-6 bg-white border border-[#E2E0DC]">
              <h3 className="font-serif text-xl text-[#181615] mb-3">
                Funnel Efficiency by Device Platform
              </h3>
              <table className="w-full text-xs border-collapse font-mono">
                <thead>
                  <tr className="border-b border-[#E2E0DC] text-[10px] uppercase text-[#655E57] text-left">
                    <th className="py-2">Device</th>
                    <th className="py-2 text-right">Sessions</th>
                    <th className="py-2 text-right">PDP Views</th>
                    <th className="py-2 text-right">Bag Adds</th>
                    <th className="py-2 text-right">Orders</th>
                    <th className="py-2 text-right">CVR (%)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EFECE6]">
                  {funnel.by_device.map((d) => (
                    <tr key={d.device_type}>
                      <td className="py-2.5 font-semibold text-[#181615]">
                        {d.device_type}
                      </td>
                      <td className="py-2.5 text-right">{d.sessions}</td>
                      <td className="py-2.5 text-right">{d.pdp_sessions}</td>
                      <td className="py-2.5 text-right">{d.cart_sessions}</td>
                      <td className="py-2.5 text-right">{d.order_sessions}</td>
                      <td className="py-2.5 text-right text-[#7C2D26] font-semibold">
                        {d.cvr_pct}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="p-6 bg-white border border-[#E2E0DC]">
              <h3 className="font-serif text-xl text-[#181615] mb-3">
                Funnel Efficiency by Acquisition Channel
              </h3>
              <table className="w-full text-xs border-collapse font-mono">
                <thead>
                  <tr className="border-b border-[#E2E0DC] text-[10px] uppercase text-[#655E57] text-left">
                    <th className="py-2">Channel</th>
                    <th className="py-2 text-right">Sessions</th>
                    <th className="py-2 text-right">Searches</th>
                    <th className="py-2 text-right">Bag Adds</th>
                    <th className="py-2 text-right">Orders</th>
                    <th className="py-2 text-right">CVR (%)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EFECE6]">
                  {funnel.by_channel.map((c) => (
                    <tr key={c.acquisition_channel}>
                      <td className="py-2.5 font-semibold text-[#181615]">
                        {c.acquisition_channel}
                      </td>
                      <td className="py-2.5 text-right">{c.sessions}</td>
                      <td className="py-2.5 text-right">
                        {c.search_sessions}
                      </td>
                      <td className="py-2.5 text-right">{c.cart_sessions}</td>
                      <td className="py-2.5 text-right">{c.order_sessions}</td>
                      <td className="py-2.5 text-right text-[#7C2D26] font-semibold">
                        {c.cvr_pct}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Live Event Stream Inspector */}
          {recentEvents && (
            <div className="p-6 bg-white border border-[#E2E0DC] space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26] flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5" />
                    Mixpanel &amp; Relational Event Log (`events` Table)
                  </p>
                  <h3 className="font-serif text-xl text-[#181615]">
                    Latest Tracked Customer Events
                  </h3>
                </div>
                <span className="text-[11px] font-mono px-2.5 py-1 bg-[#FAF8F5] border border-[#D5D2CC]">
                  Mixpanel Cloud Token:{" "}
                  {recentEvents.mixpanel_configured
                    ? "Configured (Dual-Write)"
                    : "Not Set (Local SQL Adapter Active)"}
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse font-mono">
                  <thead>
                    <tr className="border-b border-[#E2E0DC] text-[10px] uppercase text-[#655E57] text-left">
                      <th className="py-2">Event ID</th>
                      <th className="py-2">Event Name</th>
                      <th className="py-2">User ID</th>
                      <th className="py-2">Session ID</th>
                      <th className="py-2">Product</th>
                      <th className="py-2">Device / Channel</th>
                      <th className="py-2">Variant</th>
                      <th className="py-2">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#EFECE6]">
                    {recentEvents.events.map((ev) => (
                      <tr key={ev.id}>
                        <td className="py-2 text-[#655E57]">{ev.id}</td>
                        <td className="py-2 font-semibold text-[#7C2D26]">
                          {ev.event_name}
                        </td>
                        <td className="py-2">{ev.user_id}</td>
                        <td className="py-2 text-[#655E57]">
                          {ev.session_id}
                        </td>
                        <td className="py-2">
                          {ev.product_id || "—"}
                        </td>
                        <td className="py-2 text-[#655E57]">
                          {ev.device_type} · {ev.acquisition_channel}
                        </td>
                        <td className="py-2">
                          <span
                            className={`px-1.5 py-0.5 text-[10px] uppercase ${
                              ev.experiment_variant === "treatment"
                                ? "bg-[#7C2D26] text-white"
                                : "bg-[#E6E0D6] text-[#181615]"
                            }`}
                          >
                            {ev.experiment_variant || "control"}
                          </span>
                        </td>
                        <td className="py-2 text-[#655E57]">
                          {ev.event_timestamp}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
