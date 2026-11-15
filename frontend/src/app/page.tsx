"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  Compass,
  Layers,
  Search,
  Sparkles,
  UserCheck,
} from "lucide-react";
import { StorefrontShell } from "@/components/storefront/StorefrontShell";
import { ProductCard } from "@/components/storefront/ProductCard";
import { apiFetch, Category, Product } from "@/lib/api";
import { useThreadline } from "@/lib/store";

interface BootstrapResponse {
  categories: Category[];
  featured_products: Product[];
  new_arrivals: Product[];
  recommended_for_user: Product[];
  active_user: {
    id: string;
    full_name: string;
    persona_segment: string;
    preferred_size: string;
    city_tier: string;
  } | null;
}

export default function StorefrontHomepage() {
  const router = useRouter();
  const { userId, trackEvent } = useThreadline();
  const [data, setData] = useState<BootstrapResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [heroSearch, setHeroSearch] = useState<string>("");

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await apiFetch<BootstrapResponse>(
          `/api/storefront/bootstrap?user_id=${encodeURIComponent(userId)}`
        );
        if (!active) return;
        setData(res);
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error ? err.message : "Failed to load storefront"
          );
        }
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    trackEvent("homepage_viewed", { properties: { section: "editorial_home" } });
    return () => {
      active = false;
    };
  }, [userId, trackEvent]);

  const handleHeroSearch = (e: React.FormEvent) => {
    e.preventDefault();
    router.push(`/search?q=${encodeURIComponent(heroSearch.trim())}`);
  };

  return (
    <StorefrontShell>
      {/* Editorial Asymmetric Split Hero */}
      <section className="border-b border-[#E6E0D6] bg-[#F5F1EA]">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-8 py-12 lg:py-16 grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 border border-[#D5CEC2] bg-[#FAF8F5] px-3 py-1 text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
              <span>Autumn / Winter — Archival Issue No. 04</span>
            </div>

            <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl leading-[1.08] text-[#181615] tracking-tight">
              Material Honesty &amp; Architectural Drape.
            </h1>

            <p className="text-base sm:text-lg text-[#57514B] max-w-2xl leading-relaxed">
              European flax tailoring, 22-momme mulberry silk bias cuts, and
              shuttle-loomed Japanese selvedge — accompanied by verified buyer
              fit consensus on every silhouette.
            </p>

            {/* Direct Discovery Search Bar */}
            <form
              onSubmit={handleHeroSearch}
              className="max-w-xl flex items-center bg-white border border-[#181615] p-1"
            >
              <Search className="w-4 h-4 text-[#655E57] ml-3 mr-2 shrink-0" />
              <input
                type="text"
                value={heroSearch}
                onChange={(e) => setHeroSearch(e.target.value)}
                placeholder="Search 'linen blazer', 'occasion dress', or try 'haldi guest outfit'..."
                className="w-full py-2.5 text-sm text-[#181615] placeholder:text-[#8C847B] focus:outline-none"
              />
              <button
                type="submit"
                className="bg-[#181615] hover:bg-[#7C2D26] text-white px-5 py-2.5 text-xs font-mono uppercase tracking-widest transition-colors shrink-0"
              >
                Explore
              </button>
            </form>

            <div className="flex flex-wrap items-center gap-2 text-xs text-[#655E57]">
              <span className="font-mono uppercase text-[11px] text-[#181615]">
                Trending Discovery:
              </span>
              {[
                "linen blazer",
                "wide leg trouser",
                "occasion dress",
                "merino cardigan",
                "haldi guest outfit",
              ].map((term) => (
                <Link
                  key={term}
                  href={`/search?q=${encodeURIComponent(term)}`}
                  className="px-2.5 py-1 bg-[#FAF8F5] border border-[#D5CEC2] hover:border-[#7C2D26] text-[#181615] transition-colors"
                >
                  {term}
                </Link>
              ))}
            </div>
          </div>

          <div className="lg:col-span-5 grid grid-cols-2 gap-4">
            <Link
              href="/products/prd_001"
              className="group relative aspect-[3/4] overflow-hidden border border-[#D5CEC2] bg-[#EAE4DC]"
            >
              <img
                src="https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=900&q=80"
                alt="Valence Belted European Linen Blazer"
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute bottom-0 inset-x-0 bg-[#181615]/85 text-[#FAF8F5] p-3">
                <p className="text-[10px] font-mono uppercase tracking-widest text-[#D4B895]">
                  Look 01 · Normandy Flax
                </p>
                <p className="font-serif text-sm mt-0.5">
                  Valence Belted Linen Blazer
                </p>
              </div>
            </Link>

            <Link
              href="/products/prd_005"
              className="group relative aspect-[3/4] overflow-hidden border border-[#D5CEC2] bg-[#EAE4DC] mt-6"
            >
              <img
                src="https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&w=900&q=80"
                alt="Seraphina Bias-Cut Mulberry Silk Midi Dress"
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute bottom-0 inset-x-0 bg-[#181615]/85 text-[#FAF8F5] p-3">
                <p className="text-[10px] font-mono uppercase tracking-widest text-[#D4B895]">
                  Look 02 · 22-Momme Silk
                </p>
                <p className="font-serif text-sm mt-0.5">
                  Seraphina Bias-Cut Midi
                </p>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* Loading & Error Handling */}
      {loading && (
        <div className="max-w-[1400px] mx-auto px-4 sm:px-8 py-16">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((n) => (
              <div
                key={n}
                className="h-96 bg-[#EFECE6] animate-pulse border border-[#E6E0D6]"
              />
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="max-w-[1400px] mx-auto px-4 sm:px-8 py-12">
          <div className="p-6 border border-[#7C2D26] bg-[#FFF5F2] text-[#7C2D26]">
            <p className="font-mono text-xs uppercase font-semibold">
              Storefront API Connection Error
            </p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {data && !loading && (
        <div className="max-w-[1400px] mx-auto px-4 sm:px-8 space-y-20 py-14">
          {/* 1. Category Architecture Navigation */}
          <section>
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 pb-6 border-b border-[#E6E0D6]">
              <div>
                <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26] flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5" />
                  Curated Departments
                </p>
                <h2 className="font-serif text-3xl text-[#181615] mt-1">
                  Browse by Material &amp; Silhouette
                </h2>
              </div>
              <Link
                href="/search"
                className="inline-flex items-center gap-1.5 text-xs font-mono uppercase tracking-wider text-[#181615] hover:text-[#7C2D26]"
              >
                View Complete 24-Piece Archive
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mt-6">
              {data.categories.map((cat, idx) => (
                <Link
                  key={cat.id}
                  href={`/search?category_id=${encodeURIComponent(cat.id)}`}
                  className="group p-6 border border-[#E6E0D6] bg-white hover:border-[#181615] transition-colors flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-widest text-[#655E57]">
                      <span>0{idx + 1} · {cat.parent_department}</span>
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform text-[#181615]" />
                    </div>
                    <h3 className="font-serif text-2xl text-[#181615] mt-2 group-hover:text-[#7C2D26] transition-colors">
                      {cat.name}
                    </h3>
                    <p className="text-xs text-[#655E57] mt-2 leading-relaxed">
                      {cat.editorial_tagline}
                    </p>
                  </div>
                  <div className="mt-5 pt-3 border-t border-[#F2EFE9] text-[11px] font-mono uppercase tracking-wider text-[#181615]">
                    Explore Capsule →
                  </div>
                </Link>
              ))}
            </div>
          </section>

          {/* 2. Personalized Recommendations for Active Persona */}
          {data.active_user && (
            <section className="p-6 sm:p-8 border border-[#D5CEC2] bg-[#F5F1EA]">
              <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-[#E0D9CE]">
                <div>
                  <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26] flex items-center gap-1.5">
                    <UserCheck className="w-3.5 h-3.5" />
                    Tailored Edit for {data.active_user.full_name} (
                    {data.active_user.persona_segment} · Size{" "}
                    {data.active_user.preferred_size})
                  </p>
                  <h2 className="font-serif text-3xl text-[#181615] mt-1">
                    Recommended in Your Size &amp; Fit Profile
                  </h2>
                </div>
                <Link
                  href={`/search?size=${encodeURIComponent(
                    data.active_user.preferred_size
                  )}`}
                  className="text-xs font-mono uppercase tracking-wider text-[#181615] hover:text-[#7C2D26] inline-flex items-center gap-1.5"
                >
                  Filter All Size {data.active_user.preferred_size} Pieces
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
                {data.recommended_for_user.map((p) => (
                  <ProductCard key={p.id} product={p} />
                ))}
              </div>
            </section>
          )}

          {/* 3. Featured Editorial Pieces */}
          <section>
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 pb-6 border-b border-[#E6E0D6]">
              <div>
                <p className="text-[11px] font-mono uppercase tracking-widest text-[#655E57] flex items-center gap-1.5">
                  <Compass className="w-3.5 h-3.5 text-[#7C2D26]" />
                  Signature Tailoring &amp; Drape
                </p>
                <h2 className="font-serif text-3xl text-[#181615] mt-1">
                  Featured Atelier Selection
                </h2>
              </div>
              <Link
                href="/search?sort_by=popularity"
                className="text-xs font-mono uppercase tracking-wider text-[#181615] hover:text-[#7C2D26] inline-flex items-center gap-1.5"
              >
                Sort by Bestsellers
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-7 mt-6">
              {data.featured_products.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          </section>

          {/* 4. New Arrivals */}
          <section>
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 pb-6 border-b border-[#E6E0D6]">
              <div>
                <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26] flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" />
                  Just Landed
                </p>
                <h2 className="font-serif text-3xl text-[#181615] mt-1">
                  New Season Arrivals
                </h2>
              </div>
              <Link
                href="/search"
                className="text-xs font-mono uppercase tracking-wider text-[#181615] hover:text-[#7C2D26] inline-flex items-center gap-1.5"
              >
                Explore All New Arrivals
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-7 mt-6">
              {data.new_arrivals.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          </section>
        </div>
      )}
    </StorefrontShell>
  );
}
