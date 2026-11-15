"use client";

import React, { Suspense, useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  AlertCircle,
  Check,
  Filter,
  RotateCcw,
  Ruler,
  Search,
  SlidersHorizontal,
  Sparkles,
} from "lucide-react";
import { StorefrontShell } from "@/components/storefront/StorefrontShell";
import { ProductCard } from "@/components/storefront/ProductCard";
import { API_BASE_URL, apiFetch, Product } from "@/lib/api";
import { useThreadline } from "@/lib/store";

interface SearchApiResponse {
  search_id: string | null;
  query: string;
  experiment_variant: string;
  synonym_expanded: boolean;
  expanded_tokens: string[];
  total_results: number;
  products: Product[];
  zero_result_recovery: {
    message: string;
    tip: string;
    suggested_queries: string[];
    fallback_products: Product[];
  } | null;
  available_facets: {
    brands: string[];
    fit_profiles: string[];
    colors: string[];
    sizes: string[];
  };
}

function SearchDiscoveryContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const {
    userId,
    sessionId,
    activePersona,
    categories,
    experimentVariant,
    setExperimentVariant,
    trackEvent,
  } = useThreadline();

  const [queryText, setQueryText] = useState<string>(
    searchParams.get("q") || ""
  );
  const [selectedCategory, setSelectedCategory] = useState<string>(
    searchParams.get("category_id") || "all"
  );
  const [selectedBrand, setSelectedBrand] = useState<string>("all");
  const [selectedSize, setSelectedSize] = useState<string>(
    searchParams.get("size") || "all"
  );
  const [selectedColor, setSelectedColor] = useState<string>("all");
  const [selectedFitProfile, setSelectedFitProfile] = useState<string>("all");
  const [maxPrice, setMaxPrice] = useState<number>(15000);
  const [sortBy, setSortBy] = useState<string>(
    searchParams.get("sort_by") || "relevance"
  );

  const [searchData, setSearchData] = useState<SearchApiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setQueryText(searchParams.get("q") || "");
    if (searchParams.get("category_id")) {
      setSelectedCategory(searchParams.get("category_id") || "all");
    }
    if (searchParams.get("size")) {
      setSelectedSize(searchParams.get("size") || "all");
    }
  }, [searchParams]);

  const runSearch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (queryText.trim()) params.set("q", queryText.trim());
      if (selectedCategory !== "all")
        params.set("category_id", selectedCategory);
      if (selectedBrand !== "all") params.set("brand", selectedBrand);
      if (selectedSize !== "all") params.set("size", selectedSize);
      if (selectedColor !== "all") params.set("color", selectedColor);
      if (selectedFitProfile !== "all")
        params.set("fit_profile", selectedFitProfile);
      if (maxPrice < 15000) params.set("max_price", String(maxPrice));
      params.set("sort_by", sortBy);
      params.set("experiment_variant", experimentVariant);
      params.set("user_id", userId);
      params.set("session_id", sessionId);

      const res = await apiFetch<SearchApiResponse>(
        `/api/storefront/search?${params.toString()}`
      );
      setSearchData(res);

      if (queryText.trim()) {
        trackEvent("search_submitted", {
          properties: {
            query: queryText.trim(),
            results_count: res.total_results,
            synonym_expanded: res.synonym_expanded,
            variant: experimentVariant,
          },
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }, [
    queryText,
    selectedCategory,
    selectedBrand,
    selectedSize,
    selectedColor,
    selectedFitProfile,
    maxPrice,
    sortBy,
    experimentVariant,
    userId,
    sessionId,
    trackEvent,
  ]);

  useEffect(() => {
    runSearch();
  }, [runSearch]);

  const applyFilterWithTracking = (filterName: string, value: string) => {
    trackEvent("filter_applied", {
      properties: { filter_type: filterName, value },
    });
  };

  const resetAllFilters = () => {
    setQueryText("");
    setSelectedCategory("all");
    setSelectedBrand("all");
    setSelectedSize("all");
    setSelectedColor("all");
    setSelectedFitProfile("all");
    setMaxPrice(15000);
    setSortBy("relevance");
    router.replace("/search");
  };

  const handleProductCardClick = async (product: Product) => {
    if (searchData?.search_id) {
      try {
        await fetch(`${API_BASE_URL}/api/storefront/search/click`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            search_id: searchData.search_id,
            product_id: product.id,
            click_position: 1,
            user_id: userId,
            session_id: sessionId,
            experiment_variant: experimentVariant,
          }),
        });
      } catch {
        // non-blocking
      }
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-8 py-10">
      {/* Page Title & Live Search Input */}
      <div className="pb-8 border-b border-[#E6E0D6] flex flex-col lg:flex-row lg:items-end justify-between gap-6">
        <div>
          <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
            Catalog Discovery &amp; Faceted Filtering
          </p>
          <h1 className="font-serif text-3xl sm:text-4xl text-[#181615] mt-1">
            {queryText
              ? `Search Results for “${queryText}”`
              : selectedCategory !== "all"
              ? categories.find((c) => c.id === selectedCategory)?.name ||
                "Collection Archive"
              : "Complete Atelier Collection"}
          </h1>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            runSearch();
          }}
          className="flex items-center border border-[#181615] bg-white w-full lg:w-[440px]"
        >
          <Search className="w-4 h-4 text-[#655E57] ml-3 mr-2 shrink-0" />
          <input
            type="text"
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            placeholder="Search fabric, occasion ('haldi guest outfit'), SKU..."
            className="w-full py-2 text-sm text-[#181615] focus:outline-none"
          />
          {queryText && (
            <button
              type="button"
              onClick={() => setQueryText("")}
              className="px-2 text-xs text-[#655E57] hover:text-[#181615]"
            >
              Clear
            </button>
          )}
          <button
            type="submit"
            className="bg-[#181615] text-white px-4 py-2 text-xs font-mono uppercase tracking-wider hover:bg-[#7C2D26]"
          >
            Search
          </button>
        </form>
      </div>

      {/* A/B Experiment Treatment Bar: Sticky 'In-My-Size & Fit Guidance' Quick Facets */}
      {experimentVariant === "treatment" ? (
        <div className="my-6 p-4 border border-[#D4B895] bg-[#F6EFE4] flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <span className="inline-flex items-center gap-1.5 bg-[#7C2D26] text-white px-2.5 py-1 text-[10px] font-mono uppercase tracking-widest">
              <Sparkles className="w-3 h-3" />
              Treatment Active (exp_semantic_size_fit_filters)
            </span>

            <button
              type="button"
              onClick={() => {
                const target =
                  selectedSize === (activePersona?.preferred_size || "S")
                    ? "all"
                    : activePersona?.preferred_size || "S";
                setSelectedSize(target);
                applyFilterWithTracking("in_my_size_pill", target);
              }}
              className={`px-3 py-1 text-xs font-mono border transition-colors inline-flex items-center gap-1.5 ${
                selectedSize === (activePersona?.preferred_size || "S")
                  ? "bg-[#181615] text-white border-[#181615]"
                  : "bg-white text-[#181615] border-[#D5CEC2] hover:border-[#181615]"
              }`}
            >
              <Check className="w-3 h-3" />
              In My Size ({activePersona?.preferred_size || "S"})
            </button>

            {["True to Size", "Relaxed Tailored", "Runs Small - Size Up"].map(
              (fp) => (
                <button
                  key={fp}
                  type="button"
                  onClick={() => {
                    const nextFp = selectedFitProfile === fp ? "all" : fp;
                    setSelectedFitProfile(nextFp);
                    applyFilterWithTracking("fit_profile_pill", nextFp);
                  }}
                  className={`px-3 py-1 text-xs font-mono border transition-colors inline-flex items-center gap-1 ${
                    selectedFitProfile === fp
                      ? "bg-[#7C2D26] text-white border-[#7C2D26]"
                      : "bg-white text-[#181615] border-[#D5CEC2] hover:border-[#7C2D26]"
                  }`}
                >
                  <Ruler className="w-3 h-3" />
                  {fp}
                </button>
              )
            )}
          </div>

          {searchData?.synonym_expanded && (
            <div className="text-xs font-mono text-[#7C2D26] bg-white px-3 py-1 border border-[#E8C5BE]">
              Semantic Synonym Match:{" "}
              {searchData.expanded_tokens.slice(0, 4).join(", ")}
            </div>
          )}
        </div>
      ) : (
        <div className="my-6 p-3 border border-[#E6E0D6] bg-[#F3EFE8] flex flex-wrap items-center justify-between gap-3 text-xs text-[#57514B]">
          <span>
            <strong className="font-mono uppercase text-[#181615]">
              Control Variant Active:
            </strong>{" "}
            Standard exact keyword matching without sticky size/fit pills or
            fit badges.
          </span>
          <button
            type="button"
            onClick={() => setExperimentVariant("treatment")}
            className="text-[#7C2D26] font-mono uppercase underline hover:text-[#181615]"
          >
            Switch to Treatment Variant →
          </button>
        </div>
      )}

      {/* Main Grid: Left Facet Sidebar + Right Product Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mt-6">
        {/* Left Filter Sidebar */}
        <aside className="lg:col-span-3 space-y-6 border-r-0 lg:border-r border-[#E6E0D6] lg:pr-6">
          <div className="flex items-center justify-between pb-3 border-b border-[#E6E0D6]">
            <span className="text-xs font-mono uppercase tracking-widest text-[#181615] flex items-center gap-1.5">
              <Filter className="w-3.5 h-3.5" />
              Refine Archive
            </span>
            <button
              type="button"
              onClick={resetAllFilters}
              className="text-[11px] font-mono text-[#7C2D26] hover:underline inline-flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" />
              Reset All
            </button>
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-[11px] font-mono uppercase tracking-wider text-[#655E57] mb-2">
              Category
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                applyFilterWithTracking("category", e.target.value);
              }}
              className="w-full border border-[#D5CEC2] bg-white px-3 py-2 text-xs text-[#181615]"
            >
              <option value="all">All Categories (24 SKUs)</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Size Pills */}
          <div>
            <label className="block text-[11px] font-mono uppercase tracking-wider text-[#655E57] mb-2">
              Size
            </label>
            <div className="grid grid-cols-3 gap-1.5">
              {["all", "XS", "S", "M", "L", "XL"].map((sz) => (
                <button
                  key={sz}
                  type="button"
                  onClick={() => {
                    setSelectedSize(sz);
                    applyFilterWithTracking("size", sz);
                  }}
                  className={`py-1.5 text-xs font-mono border transition-colors ${
                    selectedSize === sz
                      ? "bg-[#181615] text-white border-[#181615]"
                      : "bg-white text-[#181615] border-[#D5CEC2] hover:border-[#181615]"
                  }`}
                >
                  {sz === "all" ? "Any" : sz}
                </button>
              ))}
            </div>
          </div>

          {/* Brand Filter */}
          <div>
            <label className="block text-[11px] font-mono uppercase tracking-wider text-[#655E57] mb-2">
              Atelier Brand
            </label>
            <select
              value={selectedBrand}
              onChange={(e) => {
                setSelectedBrand(e.target.value);
                applyFilterWithTracking("brand", e.target.value);
              }}
              className="w-full border border-[#D5CEC2] bg-white px-3 py-2 text-xs text-[#181615]"
            >
              <option value="all">All Brands</option>
              {(searchData?.available_facets?.brands || []).map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </div>

          {/* Colour Filter */}
          <div>
            <label className="block text-[11px] font-mono uppercase tracking-wider text-[#655E57] mb-2">
              Colourway
            </label>
            <select
              value={selectedColor}
              onChange={(e) => {
                setSelectedColor(e.target.value);
                applyFilterWithTracking("color", e.target.value);
              }}
              className="w-full border border-[#D5CEC2] bg-white px-3 py-2 text-xs text-[#181615]"
            >
              <option value="all">All Colourways</option>
              {(searchData?.available_facets?.colors || []).map((clr) => (
                <option key={clr} value={clr}>
                  {clr}
                </option>
              ))}
            </select>
          </div>

          {/* Price Ceiling Slider */}
          <div>
            <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-[#655E57] mb-2">
              <span>Max Price</span>
              <span className="text-[#181615] font-semibold">
                ₹{maxPrice.toLocaleString("en-IN")}
              </span>
            </div>
            <input
              type="range"
              min={2500}
              max={15000}
              step={500}
              value={maxPrice}
              onChange={(e) => {
                const v = Number(e.target.value);
                setMaxPrice(v);
                applyFilterWithTracking("max_price", String(v));
              }}
              className="w-full accent-[#7C2D26]"
            />
            <div className="flex justify-between text-[10px] font-mono text-[#8C847B] mt-1">
              <span>₹2,500</span>
              <span>₹15,000</span>
            </div>
          </div>

          {/* Test Zero-Result Query Shortcut */}
          <div className="p-4 border border-[#E6E0D6] bg-[#F5F1EA] space-y-2">
            <p className="text-[11px] font-mono uppercase tracking-wider text-[#7C2D26] font-semibold">
              PM Discovery Test Scenarios
            </p>
            <p className="text-xs text-[#57514B] leading-relaxed">
              Test how occasion queries behave in Control (0 results) vs
              Treatment (Semantic Synonym Expansion):
            </p>
            <div className="flex flex-col gap-1.5 pt-1">
              {[
                "haldi guest outfit",
                "breathable summer office wear",
                "linen co-ord set",
              ].map((testQ) => (
                <button
                  key={testQ}
                  type="button"
                  onClick={() => setQueryText(testQ)}
                  className="text-left px-2.5 py-1.5 text-xs font-mono bg-white border border-[#D5CEC2] hover:border-[#7C2D26] text-[#181615]"
                >
                  “{testQ}”
                </button>
              ))}
            </div>
          </div>
        </aside>

        {/* Right Results Column */}
        <div className="lg:col-span-9">
          {/* Sorting & Count Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 pb-4 mb-6 border-b border-[#E6E0D6]">
            <p className="text-xs font-mono text-[#57514B]">
              Showing{" "}
              <strong className="text-[#181615]">
                {searchData?.total_results ?? 0}
              </strong>{" "}
              archival pieces
            </p>

            <div className="flex items-center gap-2">
              <SlidersHorizontal className="w-3.5 h-3.5 text-[#655E57]" />
              <span className="text-xs text-[#655E57]">Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="border border-[#D5CEC2] bg-white px-3 py-1.5 text-xs font-mono text-[#181615]"
              >
                <option value="relevance">Relevance &amp; Fit Score</option>
                <option value="popularity">Popularity</option>
                <option value="rating">Customer Rating</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
              </select>
            </div>
          </div>

          {loading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((n) => (
                <div
                  key={n}
                  className="h-96 bg-[#EFECE6] animate-pulse border border-[#E6E0D6]"
                />
              ))}
            </div>
          )}

          {error && (
            <div className="p-6 border border-[#7C2D26] bg-[#FFF5F2] text-[#7C2D26]">
              <p className="font-mono text-xs uppercase font-semibold">
                Search Error
              </p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}

          {/* Zero-Result Recovery Experience */}
          {!loading &&
            searchData &&
            searchData.total_results === 0 &&
            searchData.zero_result_recovery && (
              <div className="space-y-8">
                <div className="p-6 sm:p-8 border border-[#D4B895] bg-[#FFF9F2] space-y-4">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-[#7C2D26] shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs font-mono uppercase tracking-widest text-[#7C2D26]">
                        Zero Exact Keyword Matches Logged (`results_count = 0`)
                      </p>
                      <h3 className="font-serif text-2xl text-[#181615] mt-1">
                        {searchData.zero_result_recovery.message}
                      </h3>
                      <p className="text-xs text-[#57514B] mt-2 leading-relaxed">
                        {searchData.zero_result_recovery.tip}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setExperimentVariant("treatment")}
                      className="bg-[#7C2D26] hover:bg-[#9E3B33] text-white px-4 py-2 text-xs font-mono uppercase tracking-wider transition-colors"
                    >
                      Enable Treatment Variant (Semantic Synonym Expansion)
                    </button>
                    <button
                      type="button"
                      onClick={resetAllFilters}
                      className="border border-[#181615] text-[#181615] px-4 py-2 text-xs font-mono uppercase tracking-wider hover:bg-[#181615] hover:text-white transition-colors"
                    >
                      Clear All Filters
                    </button>
                  </div>

                  <div className="pt-3 border-t border-[#E8DFD1] flex flex-wrap items-center gap-2">
                    <span className="text-[11px] font-mono uppercase text-[#655E57]">
                      Try Suggested Queries:
                    </span>
                    {searchData.zero_result_recovery.suggested_queries.map(
                      (sq) => (
                        <button
                          key={sq}
                          type="button"
                          onClick={() => setQueryText(sq)}
                          className="px-2.5 py-1 text-xs bg-white border border-[#D5CEC2] hover:border-[#7C2D26]"
                        >
                          {sq}
                        </button>
                      )
                    )}
                  </div>
                </div>

                <div>
                  <h4 className="font-serif text-2xl text-[#181615] mb-4">
                    Curated Recovery Edit — Most Popular Pieces
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    {searchData.zero_result_recovery.fallback_products.map(
                      (fp) => (
                        <ProductCard
                          key={fp.id}
                          product={fp}
                          onProductClick={handleProductCardClick}
                        />
                      )
                    )}
                  </div>
                </div>
              </div>
            )}

          {/* Product Results Grid */}
          {!loading && searchData && searchData.total_results > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {searchData.products.map((p) => (
                <ProductCard
                  key={p.id}
                  product={p}
                  onProductClick={handleProductCardClick}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function SearchDiscoveryPage() {
  return (
    <StorefrontShell>
      <Suspense
        fallback={
          <div className="max-w-[1400px] mx-auto px-8 py-16 text-xs font-mono">
            Loading Search &amp; Discovery...
          </div>
        }
      >
        <SearchDiscoveryContent />
      </Suspense>
    </StorefrontShell>
  );
}
