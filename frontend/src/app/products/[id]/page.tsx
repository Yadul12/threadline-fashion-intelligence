"use client";

import React, { use, useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  CheckCircle2,
  Heart,
  Ruler,
  ShieldCheck,
  ShoppingBag,
  Star,
} from "lucide-react";
import { StorefrontShell } from "@/components/storefront/StorefrontShell";
import { ProductCard } from "@/components/storefront/ProductCard";
import { apiFetch, formatINR, Product } from "@/lib/api";
import { useThreadline } from "@/lib/store";

interface ProductReviewItem {
  id: string;
  user_name: string;
  persona_segment: string;
  rating: number;
  title: string;
  comment_text: string;
  sentiment: string;
  complaint_category: string;
  fit_feedback: string;
  verified_purchase: boolean;
  helpful_votes: number;
  created_at: string;
}

interface ProductDetailResponse {
  product: Product;
  fit_consensus: {
    runs_small_pct: number;
    true_to_size_pct: number;
    runs_large_pct: number;
    total_verified_reviews: number;
  };
  reviews: ProductReviewItem[];
  related_products: Product[];
}

export default function ProductDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const {
    userId,
    sessionId,
    activePersona,
    addToCartOrWishlist,
    trackEvent,
    pushToast,
  } = useThreadline();

  const [data, setData] = useState<ProductDetailResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeImage, setActiveImage] = useState<string>("");
  const [selectedSize, setSelectedSize] = useState<string>("M");
  const [selectedColor, setSelectedColor] = useState<string>("");

  // Review form state
  const [reviewRating, setReviewRating] = useState<number>(5);
  const [reviewTitle, setReviewTitle] = useState<string>("");
  const [reviewComment, setReviewComment] = useState<string>("");
  const [reviewComplaintCat, setReviewComplaintCat] =
    useState<string>("Size and fit");
  const [reviewFitFeedback, setReviewFitFeedback] =
    useState<string>("True to Size");
  const [submittingReview, setSubmittingReview] = useState<boolean>(false);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await apiFetch<ProductDetailResponse>(
          `/api/storefront/products/${encodeURIComponent(id)}`
        );
        if (!active) return;
        setData(res);
        setActiveImage(res.product.image_url);
        const pref = activePersona?.preferred_size || "M";
        setSelectedSize(
          res.product.available_sizes.includes(pref)
            ? pref
            : res.product.available_sizes[0] || "M"
        );
        setSelectedColor(res.product.primary_color);

        trackEvent("product_viewed", {
          product_id: res.product.id,
          category: res.product.category_name,
          price: res.product.price,
          brand: res.product.brand,
          properties: {
            sku: res.product.sku,
            fit_profile: res.product.fit_profile,
          },
        });
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error ? err.message : "Could not load product"
          );
        }
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, [id, activePersona, trackEvent]);

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!data || !reviewTitle.trim() || !reviewComment.trim()) return;
    setSubmittingReview(true);
    try {
      await apiFetch(`/api/storefront/products/${data.product.id}/reviews`, {
        method: "POST",
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          product_id: data.product.id,
          rating: reviewRating,
          title: reviewTitle.trim(),
          comment_text: reviewComment.trim(),
          complaint_category:
            reviewRating >= 4 ? "None (Praise)" : reviewComplaintCat,
          fit_feedback: reviewFitFeedback,
        }),
      });
      const updated = await apiFetch<ProductDetailResponse>(
        `/api/storefront/products/${encodeURIComponent(id)}`
      );
      setData(updated);
      setReviewTitle("");
      setReviewComment("");
      pushToast(
        "Verified Review Published",
        "Your review and fit feedback are now live in Customer Feedback Intelligence.",
        "accent"
      );
    } catch (err) {
      pushToast(
        "Review submission failed",
        err instanceof Error ? err.message : "Please check your input",
        "error"
      );
    } finally {
      setSubmittingReview(false);
    }
  };

  return (
    <StorefrontShell>
      <div className="max-w-[1400px] mx-auto px-4 sm:px-8 py-8">
        <Link
          href="/search"
          className="inline-flex items-center gap-1.5 text-xs font-mono uppercase tracking-wider text-[#655E57] hover:text-[#181615]"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Archive &amp; Search
        </Link>

        {loading && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 mt-6">
            <div className="lg:col-span-7 h-[580px] bg-[#EFECE6] animate-pulse" />
            <div className="lg:col-span-5 h-[580px] bg-[#EFECE6] animate-pulse" />
          </div>
        )}

        {error && (
          <div className="mt-8 p-6 border border-[#7C2D26] bg-[#FFF5F2] text-[#7C2D26]">
            <p className="font-mono text-xs uppercase font-semibold">
              Product Not Found
            </p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        {data && !loading && (
          <div className="space-y-16 mt-6">
            {/* Top Product Showcase */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
              {/* Left Gallery */}
              <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-12 gap-4">
                <div className="sm:col-span-2 flex sm:flex-col gap-3 order-2 sm:order-1">
                  {[
                    {
                      url: data.product.image_url,
                      label: "Studio Lookbook",
                    },
                    {
                      url: data.product.secondary_image_url,
                      label: "Drape & Detail",
                    },
                  ].map((img, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => setActiveImage(img.url)}
                      className={`relative aspect-[3/4] w-20 sm:w-full border overflow-hidden ${
                        activeImage === img.url
                          ? "border-[#181615] ring-1 ring-[#181615]"
                          : "border-[#D5CEC2] opacity-75 hover:opacity-100"
                      }`}
                    >
                      <img
                        src={img.url}
                        alt={img.label}
                        className="w-full h-full object-cover"
                      />
                    </button>
                  ))}
                </div>

                <div className="sm:col-span-10 order-1 sm:order-2 aspect-[3/4] border border-[#E6E0D6] bg-[#EFECE6] overflow-hidden relative">
                  <img
                    src={activeImage || data.product.image_url}
                    alt={data.product.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute bottom-3 left-3 bg-[#181615]/85 text-[#FAF8F5] px-3 py-1 text-[11px] font-mono">
                    SKU: {data.product.sku} · {data.product.occasion}
                  </div>
                </div>
              </div>

              {/* Right Specification & Purchase Column */}
              <div className="lg:col-span-5 flex flex-col justify-between space-y-6">
                <div className="space-y-5">
                  <div className="flex items-center justify-between text-xs font-mono uppercase tracking-widest text-[#655E57]">
                    <span>
                      {data.product.brand} · {data.product.category_name}
                    </span>
                    <span className="inline-flex items-center gap-1 text-[#181615]">
                      <Star className="w-3.5 h-3.5 fill-[#7C2D26] text-[#7C2D26]" />
                      {data.product.rating_avg.toFixed(1)} (
                      {data.product.review_count} reviews)
                    </span>
                  </div>

                  <div>
                    <h1 className="font-serif text-3xl sm:text-4xl text-[#181615] leading-tight">
                      {data.product.title}
                    </h1>
                    <p className="text-sm text-[#57514B] mt-1.5">
                      {data.product.subtitle}
                    </p>
                  </div>

                  <div className="flex items-baseline gap-3 pt-1">
                    <span className="font-mono text-2xl font-semibold text-[#181615]">
                      {formatINR(data.product.price)}
                    </span>
                    {data.product.original_price > data.product.price && (
                      <>
                        <span className="font-mono text-sm text-[#8C847B] line-through">
                          {formatINR(data.product.original_price)}
                        </span>
                        <span className="bg-[#7C2D26] text-white px-2 py-0.5 text-[11px] font-mono uppercase">
                          Save {data.product.discount_pct}%
                        </span>
                      </>
                    )}
                  </div>

                  {/* Verified Buyer Fit Consensus Module (THRD-103) */}
                  <div className="p-4 border border-[#D4B895] bg-[#F6EFE4] space-y-2.5">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="uppercase tracking-wider text-[#7C2D26] font-semibold flex items-center gap-1.5">
                        <Ruler className="w-3.5 h-3.5" />
                        Fit Guidance: {data.product.fit_profile}
                      </span>
                      <span className="text-[#655E57]">
                        {data.fit_consensus.total_verified_reviews} Verified
                        Buyers
                      </span>
                    </div>
                    <p className="text-xs text-[#181615] leading-relaxed">
                      {data.product.fit_notes}
                    </p>
                    <div className="grid grid-cols-3 gap-2 pt-1 text-[11px] font-mono">
                      <div className="bg-white p-2 border border-[#E6E0D6]">
                        <span className="text-[#655E57] block">Runs Small</span>
                        <strong className="text-[#7C2D26]">
                          {data.fit_consensus.runs_small_pct}%
                        </strong>
                      </div>
                      <div className="bg-white p-2 border border-[#E6E0D6]">
                        <span className="text-[#655E57] block">
                          True to Size
                        </span>
                        <strong className="text-[#181615]">
                          {data.fit_consensus.true_to_size_pct}%
                        </strong>
                      </div>
                      <div className="bg-white p-2 border border-[#E6E0D6]">
                        <span className="text-[#655E57] block">Runs Large</span>
                        <strong className="text-[#181615]">
                          {data.fit_consensus.runs_large_pct}%
                        </strong>
                      </div>
                    </div>
                  </div>

                  {/* Colour Selector */}
                  <div>
                    <label className="block text-xs font-mono uppercase tracking-wider text-[#655E57] mb-2">
                      Colourway:{" "}
                      <strong className="text-[#181615]">
                        {selectedColor}
                      </strong>
                    </label>
                    <div className="flex flex-wrap gap-2.5">
                      {data.product.available_colors.map((c) => (
                        <button
                          key={c.name}
                          type="button"
                          onClick={() => setSelectedColor(c.name)}
                          className={`inline-flex items-center gap-2 px-3 py-1.5 border text-xs font-mono transition-colors ${
                            selectedColor === c.name
                              ? "border-[#181615] bg-[#181615] text-white"
                              : "border-[#D5CEC2] bg-white text-[#181615] hover:border-[#181615]"
                          }`}
                        >
                          <span
                            className="w-3.5 h-3.5 rounded-full border border-black/20"
                            style={{ backgroundColor: c.hex }}
                          />
                          {c.name}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Size Selector */}
                  <div>
                    <div className="flex items-center justify-between text-xs font-mono uppercase tracking-wider text-[#655E57] mb-2">
                      <span>
                        Select Size:{" "}
                        <strong className="text-[#181615]">
                          {selectedSize}
                        </strong>
                      </span>
                      {activePersona && (
                        <span className="text-[#7C2D26]">
                          Your Persona Size: {activePersona.preferred_size}
                        </span>
                      )}
                    </div>
                    <div className="grid grid-cols-5 gap-2">
                      {data.product.available_sizes.map((sz) => (
                        <button
                          key={sz}
                          type="button"
                          onClick={() => setSelectedSize(sz)}
                          className={`py-2.5 text-xs font-mono border transition-colors ${
                            selectedSize === sz
                              ? "bg-[#181615] text-white border-[#181615] font-semibold"
                              : "bg-white text-[#181615] border-[#D5CEC2] hover:border-[#181615]"
                          }`}
                        >
                          {sz}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Primary Action Buttons */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() =>
                        addToCartOrWishlist({
                          product_id: data.product.id,
                          selected_size: selectedSize,
                          selected_color: selectedColor,
                          item_type: "bag",
                        })
                      }
                      className="sm:col-span-2 bg-[#181615] hover:bg-[#7C2D26] text-white py-3.5 px-6 text-xs font-mono uppercase tracking-widest inline-flex items-center justify-center gap-2 transition-colors"
                    >
                      <ShoppingBag className="w-4 h-4" />
                      Add to Shopping Bag — {formatINR(data.product.price)}
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        addToCartOrWishlist({
                          product_id: data.product.id,
                          selected_size: selectedSize,
                          selected_color: selectedColor,
                          item_type: "wishlist",
                        })
                      }
                      className="border border-[#181615] bg-white hover:bg-[#F3EFE8] text-[#181615] py-3.5 px-4 text-xs font-mono uppercase tracking-wider inline-flex items-center justify-center gap-1.5 transition-colors"
                    >
                      <Heart className="w-4 h-4" />
                      Save
                    </button>
                  </div>

                  {/* Material & Care Specifications */}
                  <div className="pt-5 border-t border-[#E6E0D6] space-y-3 text-xs text-[#57514B]">
                    <div>
                      <strong className="font-mono uppercase text-[#181615] block">
                        Material &amp; Mill Origin
                      </strong>
                      <span>{data.product.fabric}</span>
                    </div>
                    <div>
                      <strong className="font-mono uppercase text-[#181615] block">
                        Editorial Construction Notes
                      </strong>
                      <p className="leading-relaxed mt-0.5">
                        {data.product.description}
                      </p>
                    </div>
                    <div>
                      <strong className="font-mono uppercase text-[#181615] block">
                        Garment Care
                      </strong>
                      <span>{data.product.care_instructions}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Verified Customer Reviews & Live VoC Submission */}
            <section className="pt-12 border-t border-[#E6E0D6] grid grid-cols-1 lg:grid-cols-12 gap-10">
              <div className="lg:col-span-7 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
                      Voice of Customer (Synced with PM Feedback Intelligence)
                    </p>
                    <h2 className="font-serif text-3xl text-[#181615] mt-1">
                      Verified Buyer Reviews ({data.reviews.length})
                    </h2>
                  </div>
                </div>

                <div className="space-y-4 pt-2">
                  {data.reviews.map((rev) => (
                    <div
                      key={rev.id}
                      className="p-5 border border-[#E6E0D6] bg-white space-y-2"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-semibold text-[#181615]">
                            {rev.user_name}
                          </span>
                          <span className="text-[11px] font-mono text-[#655E57] bg-[#F5F1EA] px-2 py-0.5 border border-[#E6E0D6]">
                            {rev.persona_segment}
                          </span>
                          {rev.verified_purchase && (
                            <span className="inline-flex items-center gap-1 text-[11px] font-mono text-[#2E5A3C]">
                              <ShieldCheck className="w-3.5 h-3.5" />
                              Verified
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] font-mono text-[#8C847B]">
                          ID: {rev.id} · {rev.created_at}
                        </span>
                      </div>

                      <div className="flex flex-wrap items-center gap-3 text-xs">
                        <span className="font-mono font-semibold text-[#7C2D26]">
                          {"★".repeat(rev.rating)}
                          {"☆".repeat(5 - rev.rating)}
                        </span>
                        <span className="font-semibold text-[#181615]">
                          {rev.title}
                        </span>
                        <span className="text-[11px] font-mono px-2 py-0.5 bg-[#FAF8F5] border border-[#D5CEC2] text-[#57514B]">
                          Fit: {rev.fit_feedback}
                        </span>
                        {rev.complaint_category !== "None (Praise)" && (
                          <span className="text-[11px] font-mono px-2 py-0.5 bg-[#FFF5F2] border border-[#E8C5BE] text-[#7C2D26]">
                            Topic: {rev.complaint_category}
                          </span>
                        )}
                      </div>

                      <p className="text-xs text-[#57514B] leading-relaxed">
                        {rev.comment_text}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Submit Review Form */}
              <div className="lg:col-span-5">
                <form
                  onSubmit={handleReviewSubmit}
                  className="p-6 border border-[#D5CEC2] bg-[#F5F1EA] space-y-4"
                >
                  <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
                    Live Telemetry Input
                  </p>
                  <h3 className="font-serif text-2xl text-[#181615]">
                    Contribute Fit &amp; Product Feedback
                  </h3>
                  <p className="text-xs text-[#57514B]">
                    Submitting a review fires the `product_reviewed` event and
                    immediately updates the GenAI Customer Feedback Intelligence
                    workspace.
                  </p>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[11px] font-mono uppercase text-[#181615] mb-1">
                        Rating (1-5)
                      </label>
                      <select
                        value={reviewRating}
                        onChange={(e) =>
                          setReviewRating(Number(e.target.value))
                        }
                        className="w-full border border-[#D5CEC2] bg-white px-3 py-2 text-xs"
                      >
                        <option value={5}>5 Stars — Exceptional</option>
                        <option value={4}>4 Stars — Very Good</option>
                        <option value={3}>3 Stars — Mixed / Fit Issue</option>
                        <option value={2}>2 Stars — Disappointed</option>
                        <option value={1}>1 Star — Poor Experience</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-mono uppercase text-[#181615] mb-1">
                        How Did It Fit?
                      </label>
                      <select
                        value={reviewFitFeedback}
                        onChange={(e) => setReviewFitFeedback(e.target.value)}
                        className="w-full border border-[#D5CEC2] bg-white px-3 py-2 text-xs"
                      >
                        <option value="Runs Small">Runs Small</option>
                        <option value="True to Size">True to Size</option>
                        <option value="Runs Large">Runs Large</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-[11px] font-mono uppercase text-[#181615] mb-1">
                      Feedback Category
                    </label>
                    <select
                      value={reviewComplaintCat}
                      onChange={(e) => setReviewComplaintCat(e.target.value)}
                      className="w-full border border-[#D5CEC2] bg-white px-3 py-2 text-xs"
                    >
                      <option value="Size and fit">Size and fit</option>
                      <option value="Search relevance">Search relevance</option>
                      <option value="Product images">Product images</option>
                      <option value="Product quality">Product quality</option>
                      <option value="Pricing">Pricing</option>
                      <option value="Delivery experience">
                        Delivery experience
                      </option>
                      <option value="None (Praise)">None (Praise)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-mono uppercase text-[#181615] mb-1">
                      Review Headline
                    </label>
                    <input
                      type="text"
                      required
                      value={reviewTitle}
                      onChange={(e) => setReviewTitle(e.target.value)}
                      placeholder="e.g., Beautiful drape, size up for comfort"
                      className="w-full border border-[#D5CEC2] bg-white px-3 py-2 text-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-mono uppercase text-[#181615] mb-1">
                      Detailed Review
                    </label>
                    <textarea
                      rows={3}
                      required
                      value={reviewComment}
                      onChange={(e) => setReviewComment(e.target.value)}
                      placeholder="Share specific feedback on fabric, sizing, or search discovery..."
                      className="w-full border border-[#D5CEC2] bg-white px-3 py-2 text-xs"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={submittingReview}
                    className="w-full bg-[#181615] hover:bg-[#7C2D26] text-white py-2.5 text-xs font-mono uppercase tracking-widest transition-colors inline-flex items-center justify-center gap-2"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    {submittingReview
                      ? "Publishing Review..."
                      : "Publish Verified Review"}
                  </button>
                </form>
              </div>
            </section>

            {/* Related Products */}
            <section className="pt-12 border-t border-[#E6E0D6]">
              <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
                Complete the Atelier Silhouette
              </p>
              <h2 className="font-serif text-3xl text-[#181615] mt-1 mb-6">
                Complementary &amp; Related Pieces
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {data.related_products.map((rp) => (
                  <ProductCard key={rp.id} product={rp} />
                ))}
              </div>
            </section>
          </div>
        )}
      </div>
    </StorefrontShell>
  );
}
