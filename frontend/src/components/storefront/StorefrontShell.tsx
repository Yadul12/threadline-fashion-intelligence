"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Activity,
  ArrowUpRight,
  BarChart3,
  Heart,
  Search,
  ShoppingBag,
  SlidersHorizontal,
  UserCheck,
  X,
} from "lucide-react";
import { apiFetch, formatINR, Product } from "@/lib/api";
import { useThreadline } from "@/lib/store";

export function StorefrontShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const {
    userId,
    setUserId,
    activePersona,
    personas,
    categories,
    experimentVariant,
    setExperimentVariant,
    cart,
    liveEventCount,
    lastTrackedEvent,
    toasts,
    dismissToast,
  } = useThreadline();

  const [searchOpen, setSearchOpen] = useState(false);
  const [searchInput, setSearchInput] = useState("");
  const [suggestions, setSuggestions] = useState<{
    suggested_queries: string[];
    matching_products: Product[];
  } | null>(null);

  useEffect(() => {
    if (!searchOpen) return;
    let active = true;
    const timer = setTimeout(async () => {
      try {
        const res = await apiFetch<{
          suggested_queries: string[];
          matching_products: Product[];
        }>(
          `/api/storefront/autocomplete?q=${encodeURIComponent(searchInput)}`
        );
        if (active) setSuggestions(res);
      } catch {
        // ignore
      }
    }, 120);
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [searchOpen, searchInput]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchOpen(false);
    router.push(`/search?q=${encodeURIComponent(searchInput.trim())}`);
  };

  const bagCount = cart?.summary?.bag_count || 0;
  const wishlistCount = cart?.summary?.wishlist_count || 0;

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F5] text-[#181615]">
      {/* Top Product Operations & Experimentation Telemetry Bar */}
      <div className="bg-[#181615] text-[#EDE8DF] text-xs border-b border-[#2E2A27]">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-8 py-2 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-4">
            <span className="inline-flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-wider text-[#D4B895]">
              <Activity className="w-3.5 h-3.5 text-[#9E3B33]" />
              Live Telemetry
              {lastTrackedEvent ? (
                <span className="text-[#FAF8F5] bg-[#2A2623] px-2 py-0.5 border border-[#3E3834]">
                  {lastTrackedEvent} ({liveEventCount})
                </span>
              ) : (
                <span className="text-[#9A928A]">Ready</span>
              )}
            </span>

            {/* Persona Switcher */}
            <div className="flex items-center gap-1.5">
              <UserCheck className="w-3.5 h-3.5 text-[#A59D94]" />
              <span className="text-[#A59D94] hidden sm:inline">Shopper:</span>
              <select
                aria-label="Active Shopper Persona"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                className="bg-[#25221F] text-[#FAF8F5] border border-[#3E3834] px-2 py-0.5 text-xs focus:outline-none focus:border-[#9E3B33]"
              >
                {personas.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.full_name} ({p.persona_segment} · Size {p.preferred_size})
                  </option>
                ))}
              </select>
            </div>

            {/* Live A/B Experiment Variant Toggle */}
            <div className="flex items-center gap-1.5">
              <SlidersHorizontal className="w-3.5 h-3.5 text-[#A59D94]" />
              <span className="text-[#A59D94] hidden md:inline">
                A/B Exp (Search &amp; Fit):
              </span>
              <div className="inline-flex border border-[#3E3834] bg-[#25221F]">
                <button
                  type="button"
                  onClick={() => setExperimentVariant("control")}
                  className={`px-2 py-0.5 text-[11px] font-mono uppercase transition-colors ${
                    experimentVariant === "control"
                      ? "bg-[#FAF8F5] text-[#181615] font-semibold"
                      : "text-[#A59D94] hover:text-white"
                  }`}
                >
                  Control
                </button>
                <button
                  type="button"
                  onClick={() => setExperimentVariant("treatment")}
                  className={`px-2 py-0.5 text-[11px] font-mono uppercase transition-colors ${
                    experimentVariant === "treatment"
                      ? "bg-[#7C2D26] text-white font-semibold"
                      : "text-[#A59D94] hover:text-white"
                  }`}
                >
                  Treatment
                </button>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/pm"
              className="inline-flex items-center gap-1.5 bg-[#7C2D26] hover:bg-[#9E3B33] text-white px-3 py-1 text-xs font-medium tracking-wide transition-colors"
            >
              <BarChart3 className="w-3.5 h-3.5" />
              Open PM Intelligence Workspace
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Main Editorial Navigation Header */}
      <header className="sticky top-0 z-30 bg-[#FAF8F5]/95 backdrop-blur-xs border-b border-[#E6E0D6]">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-8 h-20 flex items-center justify-between gap-6">
          <div className="flex items-center gap-10">
            <Link href="/" className="group flex flex-col">
              <span className="font-serif text-2xl sm:text-3xl tracking-[0.18em] font-semibold text-[#181615]">
                THREADLINE
              </span>
              <span className="text-[10px] font-mono uppercase tracking-[0.24em] text-[#655E57] -mt-1">
                Atelier &amp; Contemporary Archive
              </span>
            </Link>

            <nav className="hidden lg:flex items-center gap-7 text-sm">
              <Link
                href="/"
                className={`py-1 border-b-2 transition-colors ${
                  pathname === "/"
                    ? "border-[#7C2D26] text-[#181615] font-medium"
                    : "border-transparent text-[#57514B] hover:text-[#181615]"
                }`}
              >
                Editorial Home
              </Link>
              <Link
                href="/search"
                className={`py-1 border-b-2 transition-colors ${
                  pathname.startsWith("/search")
                    ? "border-[#7C2D26] text-[#181615] font-medium"
                    : "border-transparent text-[#57514B] hover:text-[#181615]"
                }`}
              >
                All Collections &amp; Search
              </Link>
              {categories.slice(0, 4).map((cat) => (
                <Link
                  key={cat.id}
                  href={`/search?category_id=${encodeURIComponent(cat.id)}`}
                  className="py-1 border-b-2 border-transparent text-[#57514B] hover:text-[#181615] transition-colors whitespace-nowrap"
                >
                  {cat.name.split("&")[0].trim()}
                </Link>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => setSearchOpen((v) => !v)}
              className="flex items-center gap-2.5 border border-[#D5CEC2] bg-white px-3.5 py-2 text-xs text-[#57514B] hover:border-[#181615] transition-colors min-w-[180px] sm:min-w-[240px]"
            >
              <Search className="w-3.5 h-3.5 text-[#181615]" />
              <span className="truncate">
                Search linen, silk, size {activePersona?.preferred_size || "S"}...
              </span>
            </button>

            <Link
              href="/bag?tab=wishlist"
              className="relative p-2 text-[#181615] hover:text-[#7C2D26] transition-colors"
              title="Saved Curation / Wishlist"
            >
              <Heart className="w-5 h-5" />
              {wishlistCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-[#655E57] text-white text-[10px] font-mono flex items-center justify-center">
                  {wishlistCount}
                </span>
              )}
            </Link>

            <Link
              href="/bag"
              className="relative inline-flex items-center gap-2 bg-[#181615] hover:bg-[#2E2A27] text-[#FAF8F5] px-3.5 py-2 text-xs font-mono uppercase tracking-wider transition-colors"
            >
              <ShoppingBag className="w-4 h-4" />
              <span>Bag ({bagCount})</span>
            </Link>
          </div>
        </div>

        {/* Autocomplete Search Drawer */}
        {searchOpen && (
          <div className="border-t border-[#E6E0D6] bg-white shadow-lg">
            <div className="max-w-[1400px] mx-auto px-4 sm:px-8 py-6">
              <form
                onSubmit={handleSearchSubmit}
                className="flex items-center gap-3 pb-4 border-b border-[#E6E0D6]"
              >
                <Search className="w-5 h-5 text-[#655E57]" />
                <input
                  type="text"
                  autoFocus
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Search by garment, fabric ('European flax linen', '22-momme silk'), or occasion ('haldi guest outfit', 'breathable summer office wear')..."
                  className="w-full text-base bg-transparent text-[#181615] placeholder:text-[#8C847B] focus:outline-none"
                />
                <button
                  type="submit"
                  className="bg-[#7C2D26] text-white px-5 py-2 text-xs font-mono uppercase tracking-wider hover:bg-[#9E3B33]"
                >
                  Search
                </button>
                <button
                  type="button"
                  onClick={() => setSearchOpen(false)}
                  className="p-2 text-[#655E57] hover:text-[#181615]"
                >
                  <X className="w-5 h-5" />
                </button>
              </form>

              <div className="grid grid-cols-1 md:grid-cols-12 gap-8 pt-5">
                <div className="md:col-span-4">
                  <p className="text-[11px] font-mono uppercase tracking-widest text-[#655E57] mb-3">
                    Suggested &amp; Experiment Test Queries
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {(
                      suggestions?.suggested_queries || [
                        "linen blazer",
                        "occasion dress",
                        "wide leg trouser",
                        "haldi guest outfit",
                        "breathable summer office wear",
                      ]
                    ).map((qText) => (
                      <button
                        key={qText}
                        type="button"
                        onClick={() => {
                          setSearchOpen(false);
                          router.push(`/search?q=${encodeURIComponent(qText)}`);
                        }}
                        className="px-3 py-1.5 text-xs bg-[#FAF8F5] border border-[#E6E0D6] hover:border-[#7C2D26] text-[#181615] transition-colors"
                      >
                        {qText}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="md:col-span-8">
                  <p className="text-[11px] font-mono uppercase tracking-widest text-[#655E57] mb-3">
                    Instant Catalog Matches
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {(suggestions?.matching_products || []).slice(0, 4).map((p) => (
                      <Link
                        key={p.id}
                        href={`/products/${p.id}`}
                        onClick={() => setSearchOpen(false)}
                        className="group flex items-center gap-3 p-2 border border-transparent hover:border-[#E6E0D6] bg-[#FAF8F5]/60"
                      >
                        <img
                          src={p.image_url}
                          alt={p.title}
                          className="w-12 h-16 object-cover bg-[#EAE4DC]"
                        />
                        <div className="min-w-0">
                          <p className="text-[11px] font-mono text-[#655E57] truncate">
                            {p.brand}
                          </p>
                          <p className="text-xs font-medium text-[#181615] truncate group-hover:text-[#7C2D26]">
                            {p.title}
                          </p>
                          <p className="text-xs font-mono text-[#181615] mt-0.5">
                            {formatINR(p.price)}
                          </p>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1">{children}</main>

      {/* Toast Notifications */}
      {toasts.length > 0 && (
        <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
          {toasts.map((t) => (
            <div
              key={t.id}
              className={`pointer-events-auto p-4 border shadow-md flex items-start justify-between gap-3 ${
                t.tone === "error"
                  ? "bg-[#4A1C18] text-white border-[#7C2D26]"
                  : t.tone === "accent"
                  ? "bg-[#181615] text-[#FAF8F5] border-[#7C2D26]"
                  : "bg-white text-[#181615] border-[#D5CEC2]"
              }`}
            >
              <div>
                <p className="text-xs font-semibold tracking-wide uppercase font-mono">
                  {t.title}
                </p>
                {t.detail && (
                  <p className="text-xs mt-1 opacity-90 leading-relaxed">
                    {t.detail}
                  </p>
                )}
              </div>
              <button
                type="button"
                onClick={() => dismissToast(t.id)}
                className="opacity-70 hover:opacity-100 text-xs"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Editorial Footer */}
      <footer className="border-t border-[#E6E0D6] bg-[#F3EFE8] mt-20">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-8 py-12 grid grid-cols-1 md:grid-cols-4 gap-8 text-xs text-[#57514B]">
          <div>
            <p className="font-serif text-xl tracking-[0.18em] text-[#181615] font-semibold">
              THREADLINE
            </p>
            <p className="mt-3 leading-relaxed">
              Independent fictional fashion marketplace &amp; customer experience
              intelligence platform built to demonstrate full-lifecycle Product
              Management: discovery funnel telemetry, SQL &amp; Tableau BI,
              statistical experimentation, and traceable GenAI VoC synthesis.
            </p>
          </div>
          <div>
            <p className="font-mono uppercase tracking-widest text-[#181615] mb-3">
              Collections
            </p>
            <ul className="space-y-2">
              {categories.map((c) => (
                <li key={c.id}>
                  <Link
                    href={`/search?category_id=${c.id}`}
                    className="hover:text-[#7C2D26]"
                  >
                    {c.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="font-mono uppercase tracking-widest text-[#181615] mb-3">
              PM Intelligence Modules
            </p>
            <ul className="space-y-2">
              <li>
                <Link href="/pm" className="hover:text-[#7C2D26]">
                  1. Product Overview &amp; Cohorts
                </Link>
              </li>
              <li>
                <Link href="/pm/funnel" className="hover:text-[#7C2D26]">
                  2. 8-Step Conversion Funnel
                </Link>
              </li>
              <li>
                <Link href="/pm/search" className="hover:text-[#7C2D26]">
                  3. Search &amp; Zero-Result Intelligence
                </Link>
              </li>
              <li>
                <Link href="/pm/feedback" className="hover:text-[#7C2D26]">
                  4. GenAI Customer Feedback Synthesis
                </Link>
              </li>
              <li>
                <Link href="/pm/experiments" className="hover:text-[#7C2D26]">
                  5. A/B Experimentation Centre
                </Link>
              </li>
              <li>
                <Link href="/pm/roadmap" className="hover:text-[#7C2D26]">
                  6. RICE Product Roadmap &amp; Jira Backlog
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <p className="font-mono uppercase tracking-widest text-[#181615] mb-3">
              Synthetic Data Notice
            </p>
            <p className="leading-relaxed">
              All 180 customer profiles, 620 sessions, 480 searches, 96 verified
              reviews, and experiment outcomes are synthetic and self-contained.
              No proprietary brand assets are used.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
