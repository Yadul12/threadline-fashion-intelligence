"use client";

import React, { useCallback, useEffect, useState } from "react";
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
  AlertCircle,
  CheckCircle2,
  Download,
  FlaskConical,
  Hash,
  Plus,
} from "lucide-react";
import { apiFetch, formatINR, getExportDownloadUrl } from "@/lib/api";

interface MetricStat {
  metric_key: string;
  metric_label: string;
  is_primary: boolean;
  control_conversions: number;
  treatment_conversions: number;
  control_rate_pct: number;
  treatment_rate_pct: number;
  absolute_lift_pct: number;
  relative_lift_pct: number;
  z_score: number;
  p_value: number;
  ci_95_low_pct: number;
  ci_95_high_pct: number;
  statistically_significant: boolean;
}

interface ExperimentEvaluated {
  id: string;
  key: string;
  name: string;
  problem_statement: string;
  hypothesis: string;
  primary_metric: string;
  secondary_metrics: string[];
  control_description: string;
  treatment_description: string;
  status: string;
  traffic_allocation_pct: number;
  target_sample_size: number;
  sample_adequacy_pct: number;
  is_adequately_powered: boolean;
  start_date: string;
  end_date: string | null;
  owner: string;
  sample_sizes: {
    total_exposed: number;
    control_users: number;
    treatment_users: number;
    control_revenue_inr: number;
    treatment_revenue_inr: number;
  };
  decision_classification: string;
  decision_recommendation: string;
  primary_metric_summary: MetricStat;
  metrics_breakdown: MetricStat[];
}

export default function PMExperimentsPage() {
  const [experiments, setExperiments] = useState<ExperimentEvaluated[]>([]);
  const [methodNote, setMethodNote] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);

  // Deterministic assignment tester state
  const [testExpKey, setTestExpKey] = useState<string>(
    "exp_semantic_size_fit_filters"
  );
  const [testUserId, setTestUserId] = useState<string>("usr_demo_001");
  const [assignResult, setAssignResult] = useState<{
    experiment_key: string;
    user_id: string;
    variant: string;
    assignment_method: string;
  } | null>(null);

  // New experiment form state
  const [newKey, setNewKey] = useState<string>("exp_sticky_size_chart_drawer");
  const [newName, setNewName] = useState<string>(
    "One-Click Garment Measurement Comparison Drawer on Mobile PDP"
  );
  const [newProblem, setNewProblem] = useState<string>(
    "Mobile shoppers abandon PDPs when switching between size guide modals and product photos."
  );
  const [newHypothesis, setNewHypothesis] = useState<string>(
    "Adding a sticky bottom comparison drawer showing garment waist/hip cm against user preferred size will lift mobile Add-to-Bag conversion by 12%."
  );
  const [newControl, setNewControl] = useState<string>(
    "Standard text link modal size table."
  );
  const [newTreatment, setNewTreatment] = useState<string>(
    "Persistent bottom sheet with interactive cm/inch toggle and fit comparison."
  );
  const [newSampleSize, setNewSampleSize] = useState<number>(300);

  const loadExperiments = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch<{
        experiments: ExperimentEvaluated[];
        statistical_method_note: string;
      }>("/api/experiments");
      setExperiments(res.experiments || []);
      setMethodNote(res.statistical_method_note || "");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadExperiments();
  }, [loadExperiments]);

  const handleTestAssign = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await apiFetch<{
      experiment_key: string;
      user_id: string;
      variant: string;
      assignment_method: string;
    }>("/api/experiments/assign", {
      method: "POST",
      body: JSON.stringify({
        experiment_key: testExpKey,
        user_id: testUserId.trim(),
      }),
    });
    setAssignResult(res);
    await loadExperiments();
  };

  const handleCreateExperiment = async (e: React.FormEvent) => {
    e.preventDefault();
    await apiFetch("/api/experiments", {
      method: "POST",
      body: JSON.stringify({
        key: newKey.trim(),
        name: newName.trim(),
        problem_statement: newProblem.trim(),
        hypothesis: newHypothesis.trim(),
        primary_metric: "add_to_cart_rate",
        secondary_metrics: ["search_ctr", "purchase_conversion"],
        control_description: newControl.trim(),
        treatment_description: newTreatment.trim(),
        traffic_allocation_pct: 100,
        target_sample_size: newSampleSize,
        owner: "Ananya Rao (PM - Discovery)",
      }),
    });
    setShowCreateModal(false);
    await loadExperiments();
  };

  return (
    <div className="space-y-8 max-w-[1400px]">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-5 border-b border-[#E2E0DC]">
        <div>
          <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
            Controlled A/B Testing &amp; Statistical Inference
          </p>
          <h1 className="font-serif text-3xl text-[#181615] mt-0.5">
            Experimentation Centre
          </h1>
          <p className="text-xs text-[#655E57] mt-1">{methodNote}</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setShowCreateModal((v) => !v)}
            className="inline-flex items-center gap-1.5 bg-[#7C2D26] hover:bg-[#9E3B33] text-white px-3.5 py-2 text-xs font-mono uppercase tracking-wider"
          >
            <Plus className="w-3.5 h-3.5" />
            Create New Experiment
          </button>

          <a
            href={getExportDownloadUrl("experiment_template", "xlsx")}
            className="inline-flex items-center gap-1.5 bg-[#181615] text-white px-3.5 py-2 text-xs font-mono uppercase tracking-wider hover:bg-[#333]"
          >
            <Download className="w-3.5 h-3.5" />
            Export Experiment Tracker (.XLSX)
          </a>
        </div>
      </div>

      {/* Create New Experiment Form Drawer */}
      {showCreateModal && (
        <form
          onSubmit={handleCreateExperiment}
          className="p-6 bg-white border-2 border-[#181615] space-y-4"
        >
          <div className="flex items-center justify-between border-b border-[#E2E0DC] pb-3">
            <h2 className="font-serif text-2xl text-[#181615]">
              Launch Controlled A/B Experiment
            </h2>
            <button
              type="button"
              onClick={() => setShowCreateModal(false)}
              className="text-xs font-mono text-[#655E57] hover:text-[#181615]"
            >
              Cancel
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block font-mono uppercase text-[10px] text-[#655E57] mb-1">
                Experiment Key
              </label>
              <input
                type="text"
                required
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
                className="w-full border border-[#D5D2CC] px-3 py-2 font-mono"
              />
            </div>
            <div>
              <label className="block font-mono uppercase text-[10px] text-[#655E57] mb-1">
                Experiment Title
              </label>
              <input
                type="text"
                required
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="w-full border border-[#D5D2CC] px-3 py-2"
              />
            </div>
            <div>
              <label className="block font-mono uppercase text-[10px] text-[#655E57] mb-1">
                Required Target Sample Size (Users)
              </label>
              <input
                type="number"
                min={50}
                required
                value={newSampleSize}
                onChange={(e) => setNewSampleSize(Number(e.target.value))}
                className="w-full border border-[#D5D2CC] px-3 py-2 font-mono"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-mono uppercase text-[10px] text-[#655E57] mb-1">
                Problem Statement
              </label>
              <textarea
                rows={2}
                required
                value={newProblem}
                onChange={(e) => setNewProblem(e.target.value)}
                className="w-full border border-[#D5D2CC] p-2"
              />
            </div>
            <div>
              <label className="block font-mono uppercase text-[10px] text-[#655E57] mb-1">
                Testable Hypothesis
              </label>
              <textarea
                rows={2}
                required
                value={newHypothesis}
                onChange={(e) => setNewHypothesis(e.target.value)}
                className="w-full border border-[#D5D2CC] p-2"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-mono uppercase text-[10px] text-[#655E57] mb-1">
                Control Variant Definition
              </label>
              <input
                type="text"
                required
                value={newControl}
                onChange={(e) => setNewControl(e.target.value)}
                className="w-full border border-[#D5D2CC] px-3 py-2"
              />
            </div>
            <div>
              <label className="block font-mono uppercase text-[10px] text-[#655E57] mb-1">
                Treatment Variant Definition
              </label>
              <input
                type="text"
                required
                value={newTreatment}
                onChange={(e) => setNewTreatment(e.target.value)}
                className="w-full border border-[#D5D2CC] px-3 py-2"
              />
            </div>
          </div>

          <button
            type="submit"
            className="bg-[#181615] hover:bg-[#7C2D26] text-white px-5 py-2.5 text-xs font-mono uppercase tracking-wider"
          >
            Register &amp; Initialize Experiment
          </button>
        </form>
      )}

      {/* Deterministic SHA-256 User Assignment Tester */}
      <div className="p-5 bg-white border border-[#E2E0DC] flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="space-y-1">
          <p className="text-[10px] font-mono uppercase tracking-widest text-[#7C2D26] flex items-center gap-1.5">
            <Hash className="w-3.5 h-3.5" />
            Deterministic User Bucketing Verifier (`SHA-256(experiment_key : user_id)`)
          </p>
          <p className="text-xs text-[#57514B]">
            Verify that assigning any user ID always produces a sticky,
            consistent variant assignment across sessions.
          </p>
        </div>

        <form
          onSubmit={handleTestAssign}
          className="flex flex-wrap items-center gap-2 text-xs font-mono"
        >
          <select
            value={testExpKey}
            onChange={(e) => setTestExpKey(e.target.value)}
            className="border border-[#D5D2CC] bg-[#FAF8F5] px-3 py-2"
          >
            {experiments.map((ex) => (
              <option key={ex.key} value={ex.key}>
                {ex.key}
              </option>
            ))}
          </select>

          <input
            type="text"
            value={testUserId}
            onChange={(e) => setTestUserId(e.target.value)}
            placeholder="User ID (e.g. usr_demo_001)"
            className="border border-[#D5D2CC] bg-white px-3 py-2 w-44"
          />

          <button
            type="submit"
            className="bg-[#181615] text-white px-4 py-2 uppercase tracking-wider hover:bg-[#7C2D26]"
          >
            Verify Assignment
          </button>

          {assignResult && (
            <span className="px-3 py-2 bg-[#F6EFE4] border border-[#D4B895] text-[#181615]">
              {assignResult.user_id} →{" "}
              <strong className="uppercase text-[#7C2D26]">
                {assignResult.variant}
              </strong>{" "}
              ({assignResult.assignment_method})
            </span>
          )}
        </form>
      </div>

      {loading && (
        <div className="h-96 bg-white border border-[#E2E0DC] animate-pulse" />
      )}

      {/* Experiments List */}
      <div className="space-y-8">
        {experiments.map((exp) => {
          const isWinner = exp.decision_classification.includes(
            "Statistically Supported"
          );
          const isExploratory =
            exp.decision_classification.includes("Exploratory");

          const chartData = exp.metrics_breakdown.map((m) => ({
            metric: m.metric_label.split("(")[0].trim(),
            Control: m.control_rate_pct,
            Treatment: m.treatment_rate_pct,
          }));

          return (
            <div
              key={exp.id}
              className="p-6 bg-white border border-[#E2E0DC] space-y-6"
            >
              {/* Top Experiment Metadata & Statistical Verdict Badge */}
              <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4 pb-4 border-b border-[#E2E0DC]">
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
                    <span className="px-2 py-0.5 bg-[#181615] text-white uppercase text-[10px]">
                      {exp.status}
                    </span>
                    <span className="text-[#7C2D26] font-semibold">
                      {exp.key}
                    </span>
                    <span className="text-[#655E57]">
                      · Started {exp.start_date} · Owner: {exp.owner}
                    </span>
                  </div>
                  <h2 className="font-serif text-2xl text-[#181615]">
                    {exp.name}
                  </h2>
                  <p className="text-xs text-[#57514B] max-w-3xl">
                    <strong>Hypothesis:</strong> {exp.hypothesis}
                  </p>
                </div>

                {/* Statistical Support vs Exploratory Badge */}
                <div
                  className={`p-3.5 border shrink-0 max-w-md ${
                    isWinner
                      ? "bg-[#F4F9F5] border-[#2E5A3C] text-[#1D3B26]"
                      : isExploratory
                      ? "bg-[#FFF9F2] border-[#D4B895] text-[#7C2D26]"
                      : "bg-[#F4F3F0] border-[#D5D2CC] text-[#57514B]"
                  }`}
                >
                  <div className="flex items-center gap-1.5 font-mono text-xs font-semibold uppercase">
                    {isWinner ? (
                      <CheckCircle2 className="w-4 h-4 text-[#2E5A3C]" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-[#7C2D26]" />
                    )}
                    {exp.decision_classification}
                  </div>
                  <p className="text-[11px] mt-1 leading-relaxed">
                    {exp.decision_recommendation}
                  </p>
                </div>
              </div>

              {/* Control vs Treatment Definitions & Sample Adequacy */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div className="p-3.5 bg-[#FAF8F5] border border-[#E2E0DC]">
                  <span className="font-mono uppercase text-[10px] text-[#655E57] block">
                    Control Arm (n = {exp.sample_sizes.control_users} users ·{" "}
                    {formatINR(exp.sample_sizes.control_revenue_inr)})
                  </span>
                  <p className="text-[#181615] mt-1">
                    {exp.control_description}
                  </p>
                </div>

                <div className="p-3.5 bg-[#FAF8F5] border border-[#E2E0DC]">
                  <span className="font-mono uppercase text-[10px] text-[#7C2D26] block">
                    Treatment Arm (n = {exp.sample_sizes.treatment_users} users
                    · {formatINR(exp.sample_sizes.treatment_revenue_inr)})
                  </span>
                  <p className="text-[#181615] mt-1">
                    {exp.treatment_description}
                  </p>
                </div>

                <div className="p-3.5 bg-[#FAF8F5] border border-[#E2E0DC] font-mono">
                  <div className="flex justify-between text-[10px] uppercase text-[#655E57]">
                    <span>Sample Power Adequacy</span>
                    <span>
                      {exp.sample_sizes.total_exposed} /{" "}
                      {exp.target_sample_size} Users (
                      {exp.sample_adequacy_pct}%)
                    </span>
                  </div>
                  <div className="w-full h-2 bg-[#E2E0DC] mt-2 overflow-hidden">
                    <div
                      className={`h-full ${
                        exp.is_adequately_powered
                          ? "bg-[#2E5A3C]"
                          : "bg-[#9E3B33]"
                      }`}
                      style={{ width: `${exp.sample_adequacy_pct}%` }}
                    />
                  </div>
                  <p className="text-[11px] font-sans text-[#57514B] mt-2">
                    {exp.is_adequately_powered
                      ? "Target sample size reached. Statistical inference is fully powered."
                      : "Sample size below MDE threshold — treat results as exploratory."}
                  </p>
                </div>
              </div>

              {/* Chart + Statistical Table */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
                <div className="lg:col-span-5 h-60">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={chartData}
                      margin={{ top: 10, right: 10, left: -15, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#ECEAE4" />
                      <XAxis
                        dataKey="metric"
                        tick={{ fontSize: 10, fill: "#181615" }}
                      />
                      <YAxis
                        tick={{ fontSize: 10, fill: "#655E57" }}
                        unit="%"
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#181615",
                          color: "#FAF8F5",
                          fontSize: "12px",
                        }}
                      />
                      <Bar dataKey="Control" fill="#8C847B" />
                      <Bar dataKey="Treatment" fill="#7C2D26" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="lg:col-span-7 overflow-x-auto">
                  <table className="w-full text-xs border-collapse font-mono">
                    <thead>
                      <tr className="border-b border-[#E2E0DC] text-[10px] uppercase text-[#655E57] text-left">
                        <th className="py-2">Metric</th>
                        <th className="py-2 text-right">Control</th>
                        <th className="py-2 text-right">Treatment</th>
                        <th className="py-2 text-right">Rel. Lift</th>
                        <th className="py-2 text-right">95% CI (Abs)</th>
                        <th className="py-2 text-right">Z / p-value</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#EFECE6]">
                      {exp.metrics_breakdown.map((m) => (
                        <tr key={m.metric_key}>
                          <td className="py-2.5 font-sans">
                            <span className="font-medium text-[#181615]">
                              {m.metric_label}
                            </span>
                            {m.is_primary && (
                              <span className="ml-1.5 text-[9px] font-mono uppercase px-1.5 py-0.5 bg-[#7C2D26] text-white">
                                Primary
                              </span>
                            )}
                          </td>
                          <td className="py-2.5 text-right">
                            {m.control_rate_pct}% ({m.control_conversions})
                          </td>
                          <td className="py-2.5 text-right font-semibold text-[#181615]">
                            {m.treatment_rate_pct}% ({m.treatment_conversions})
                          </td>
                          <td
                            className={`py-2.5 text-right font-semibold ${
                              m.relative_lift_pct > 0
                                ? "text-[#2E5A3C]"
                                : "text-[#7C2D26]"
                            }`}
                          >
                            {m.relative_lift_pct > 0
                              ? `+${m.relative_lift_pct}%`
                              : `${m.relative_lift_pct}%`}
                          </td>
                          <td className="py-2.5 text-right text-[#655E57]">
                            [{m.ci_95_low_pct}%, {m.ci_95_high_pct}%]
                          </td>
                          <td className="py-2.5 text-right">
                            <span
                              className={
                                m.statistically_significant &&
                                exp.is_adequately_powered
                                  ? "text-[#2E5A3C] font-semibold"
                                  : "text-[#655E57]"
                              }
                            >
                              Z={m.z_score} · p={m.p_value}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
