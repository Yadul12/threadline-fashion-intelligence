"use client";

import React from "react";
import Link from "next/link";
import { Heart, Plus, Ruler, Star } from "lucide-react";
import { formatINR, Product } from "@/lib/api";
import { useThreadline } from "@/lib/store";

export function ProductCard({
  product,
  onProductClick,
}: {
  product: Product;
  onProductClick?: (product: Product) => void;
}) {
  const { activePersona, experimentVariant, addToCartOrWishlist } =
    useThreadline();

  const preferredSize = activePersona?.preferred_size || "M";
  const selectedSize = product.available_sizes.includes(preferredSize)
    ? preferredSize
    : product.available_sizes[0] || "M";

  const runsSmall = product.fit_profile.toLowerCase().includes("runs small");

  return (
    <div className="group flex flex-col border border-[#E6E0D6] bg-white hover:border-[#181615] transition-colors">
      <div className="relative aspect-[3/4] w-full overflow-hidden bg-[#EFECE6]">
        <Link
          href={`/products/${product.id}`}
          onClick={() => onProductClick?.(product)}
          className="block w-full h-full"
        >
          <img
            src={product.image_url}
            alt={product.title}
            loading="lazy"
            className="w-full h-full object-cover object-center group-hover:scale-[1.02] transition-transform duration-500"
          />
        </Link>

        {/* Top Badges */}
        <div className="absolute top-3 left-3 flex flex-col gap-1.5">
          {product.is_new_arrival && (
            <span className="bg-[#181615] text-[#FAF8F5] px-2.5 py-0.5 text-[10px] font-mono uppercase tracking-widest">
              New Season
            </span>
          )}
          {product.discount_pct > 0 && (
            <span className="bg-[#7C2D26] text-white px-2.5 py-0.5 text-[10px] font-mono uppercase tracking-widest">
              -{product.discount_pct}%
            </span>
          )}
        </div>

        {/* Wishlist Quick Action */}
        <button
          type="button"
          onClick={() =>
            addToCartOrWishlist({
              product_id: product.id,
              selected_size: selectedSize,
              selected_color: product.primary_color,
              item_type: "wishlist",
            })
          }
          title="Save to Wishlist"
          className="absolute top-3 right-3 w-8 h-8 bg-white/90 hover:bg-[#181615] text-[#181615] hover:text-white flex items-center justify-center border border-[#E6E0D6] transition-colors"
        >
          <Heart className="w-4 h-4" />
        </button>

        {/* A/B Treatment Feature: Upfront Verified Buyer Fit Profile Callout Badge */}
        {experimentVariant === "treatment" && (
          <div
            className={`absolute bottom-0 inset-x-0 px-3 py-1.5 text-[11px] font-mono flex items-center justify-between border-t ${
              runsSmall
                ? "bg-[#FFF5F2]/95 text-[#7C2D26] border-[#E8C5BE]"
                : "bg-[#FAF8F5]/95 text-[#2E4033] border-[#D5CEC2]"
            }`}
          >
            <span className="inline-flex items-center gap-1 font-medium">
              <Ruler className="w-3 h-3" />
              Fit: {product.fit_profile}
            </span>
            <span>
              {product.available_sizes.includes(preferredSize)
                ? `Size ${preferredSize} In Stock`
                : `Sizes: ${product.available_sizes.join(", ")}`}
            </span>
          </div>
        )}
      </div>

      {/* Card Body */}
      <div className="p-4 flex-1 flex flex-col justify-between gap-3">
        <div>
          <div className="flex items-center justify-between gap-2 text-[11px] font-mono uppercase tracking-wider text-[#655E57]">
            <span>{product.brand}</span>
            <span className="inline-flex items-center gap-1 text-[#181615]">
              <Star className="w-3 h-3 fill-[#7C2D26] text-[#7C2D26]" />
              {product.rating_avg.toFixed(1)} ({product.review_count})
            </span>
          </div>

          <Link
            href={`/products/${product.id}`}
            onClick={() => onProductClick?.(product)}
            className="block mt-1 font-serif text-lg leading-snug text-[#181615] group-hover:text-[#7C2D26] transition-colors"
          >
            {product.title}
          </Link>

          <p className="text-xs text-[#655E57] mt-1 line-clamp-1">
            {product.fabric}
          </p>
        </div>

        <div className="pt-2 border-t border-[#EFECE6] flex items-center justify-between gap-2">
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-sm font-semibold text-[#181615]">
              {formatINR(product.price)}
            </span>
            {product.original_price > product.price && (
              <span className="font-mono text-xs text-[#8C847B] line-through">
                {formatINR(product.original_price)}
              </span>
            )}
          </div>

          <button
            type="button"
            onClick={() =>
              addToCartOrWishlist({
                product_id: product.id,
                selected_size: selectedSize,
                selected_color: product.primary_color,
                item_type: "bag",
              })
            }
            className="inline-flex items-center gap-1 text-[11px] font-mono uppercase tracking-wider px-2.5 py-1.5 border border-[#181615] text-[#181615] hover:bg-[#181615] hover:text-white transition-colors"
          >
            <Plus className="w-3 h-3" />
            Add ({selectedSize})
          </button>
        </div>
      </div>
    </div>
  );
}
