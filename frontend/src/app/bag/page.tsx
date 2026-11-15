"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  CheckCircle2,
  Heart,
  Minus,
  Plus,
  ShieldCheck,
  ShoppingBag,
  Trash2,
  Truck,
} from "lucide-react";
import { StorefrontShell } from "@/components/storefront/StorefrontShell";
import { apiFetch, formatINR } from "@/lib/api";
import { useThreadline } from "@/lib/store";

interface OrderConfirmation {
  id: string;
  order_number: string;
  created_at: string;
  shipping_city: string;
  payment_method: string;
  subtotal: number;
  discount_amount: number;
  shipping_fee: number;
  total_amount: number;
  items: Array<{
    product_id: string;
    title: string;
    brand: string;
    selected_size: string;
    selected_color: string;
    quantity: number;
    unit_price: number;
    image_url: string;
  }>;
}

export default function ShoppingBagAndWishlistPage() {
  const {
    userId,
    sessionId,
    experimentVariant,
    cart,
    refreshCart,
    pushToast,
  } = useThreadline();

  const [shippingCity, setShippingCity] = useState<string>("Bengaluru, KA");
  const [paymentMethod, setPaymentMethod] = useState<string>(
    "UPI / Instant Bank Transfer"
  );
  const [promoCode, setPromoCode] = useState<string>("ATELIER10");
  const [placingOrder, setPlacingOrder] = useState<boolean>(false);
  const [confirmedOrder, setConfirmedOrder] =
    useState<OrderConfirmation | null>(null);

  const updateQty = async (cartItemId: string, nextQty: number) => {
    if (nextQty < 1) return;
    try {
      await apiFetch(`/api/storefront/cart/${cartItemId}`, {
        method: "PATCH",
        body: JSON.stringify({ quantity: nextQty }),
      });
      await refreshCart();
    } catch (err) {
      pushToast(
        "Update failed",
        err instanceof Error ? err.message : "Error",
        "error"
      );
    }
  };

  const removeItem = async (cartItemId: string) => {
    try {
      await apiFetch(`/api/storefront/cart/${cartItemId}`, {
        method: "DELETE",
      });
      await refreshCart();
      pushToast("Item Removed", "Your bag and curation have been updated.");
    } catch (err) {
      pushToast(
        "Remove failed",
        err instanceof Error ? err.message : "Error",
        "error"
      );
    }
  };

  const moveWishlistToBag = async (cartItemId: string) => {
    try {
      await apiFetch(`/api/storefront/cart/${cartItemId}/move-to-bag`, {
        method: "POST",
      });
      await refreshCart();
      pushToast(
        "Moved to Shopping Bag",
        "Event 'add_to_cart' tracked from Wishlist.",
        "accent"
      );
    } catch (err) {
      pushToast(
        "Move failed",
        err instanceof Error ? err.message : "Error",
        "error"
      );
    }
  };

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    setPlacingOrder(true);
    try {
      const res = await apiFetch<{ order: OrderConfirmation }>(
        `/api/storefront/checkout`,
        {
          method: "POST",
          body: JSON.stringify({
            user_id: userId,
            session_id: sessionId,
            shipping_city: shippingCity,
            payment_method: paymentMethod,
            promo_code: promoCode.trim() || null,
            experiment_variant: experimentVariant,
          }),
        }
      );
      setConfirmedOrder(res.order);
      await refreshCart();
      pushToast(
        `Order ${res.order.order_number} Confirmed`,
        "Events 'checkout_started' & 'order_placed' recorded in Funnel & Experiment tables.",
        "accent"
      );
    } catch (err) {
      pushToast(
        "Checkout Error",
        err instanceof Error ? err.message : "Could not place order",
        "error"
      );
    } finally {
      setPlacingOrder(false);
    }
  };

  const bagItems = cart?.bag_items || [];
  const wishlistItems = cart?.wishlist_items || [];
  const summary = cart?.summary;

  return (
    <StorefrontShell>
      <div className="max-w-[1400px] mx-auto px-4 sm:px-8 py-10">
        {/* Order Confirmation Banner */}
        {confirmedOrder && (
          <div className="mb-12 p-8 border-2 border-[#2E5A3C] bg-[#F4F9F5] space-y-6">
            <div className="flex flex-wrap items-start justify-between gap-4 border-b border-[#CFE2D4] pb-5">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-7 h-7 text-[#2E5A3C] shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-mono uppercase tracking-widest text-[#2E5A3C] font-semibold">
                    Order Confirmed · Funnel Step 8 (`order_placed`) Logged
                  </p>
                  <h2 className="font-serif text-3xl text-[#181615] mt-1">
                    Thank you. Order #{confirmedOrder.order_number} is prepared.
                  </h2>
                  <p className="text-xs text-[#57514B] mt-1">
                    Dispatched to {confirmedOrder.shipping_city} via{" "}
                    {confirmedOrder.payment_method} ·{" "}
                    {confirmedOrder.created_at}
                  </p>
                </div>
              </div>

              <div className="text-right font-mono">
                <span className="text-xs text-[#655E57] block">
                  Total Paid
                </span>
                <strong className="text-2xl text-[#181615]">
                  {formatINR(confirmedOrder.total_amount)}
                </strong>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {confirmedOrder.items.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 p-3 bg-white border border-[#D5CEC2]"
                >
                  <img
                    src={item.image_url}
                    alt={item.title}
                    className="w-14 h-20 object-cover"
                  />
                  <div className="text-xs">
                    <p className="font-mono text-[#655E57]">{item.brand}</p>
                    <p className="font-medium text-[#181615]">{item.title}</p>
                    <p className="font-mono text-[#57514B] mt-0.5">
                      Size {item.selected_size} · {item.selected_color} ×{" "}
                      {item.quantity}
                    </p>
                    <p className="font-mono font-semibold text-[#181615] mt-0.5">
                      {formatINR(item.unit_price * item.quantity)}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <Link
                href="/pm/funnel"
                className="bg-[#181615] text-white px-4 py-2 text-xs font-mono uppercase tracking-wider hover:bg-[#7C2D26]"
              >
                Inspect Updated Conversion Funnel in PM Workspace →
              </Link>
              <Link
                href="/search"
                className="text-xs font-mono uppercase tracking-wider text-[#181615] underline"
              >
                Continue Browsing Archive
              </Link>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          {/* Left Column: Shopping Bag Items & Wishlist */}
          <div className="lg:col-span-7 space-y-12">
            {/* Shopping Bag Section */}
            <section>
              <div className="pb-4 border-b border-[#E6E0D6] flex items-center justify-between">
                <div>
                  <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
                    Checkout Journey
                  </p>
                  <h1 className="font-serif text-3xl text-[#181615] mt-1">
                    Shopping Bag ({summary?.bag_count || 0} Pieces)
                  </h1>
                </div>
              </div>

              {/* Free Shipping Threshold Progress Bar (Roadmap THRD-106) */}
              {summary && (
                <div className="my-4 p-3.5 border border-[#D5CEC2] bg-[#F5F1EA] flex items-center justify-between gap-4 text-xs">
                  <div className="flex items-center gap-2">
                    <Truck className="w-4 h-4 text-[#7C2D26] shrink-0" />
                    {summary.amount_for_free_shipping === 0 ? (
                      <span className="text-[#181615] font-medium">
                        Complimentary Express Atelier Delivery unlocked (Orders
                        above ₹5,000).
                      </span>
                    ) : (
                      <span>
                        Add{" "}
                        <strong className="font-mono">
                          {formatINR(summary.amount_for_free_shipping)}
                        </strong>{" "}
                        more for complimentary Express Delivery.
                      </span>
                    )}
                  </div>
                  <span className="font-mono text-[11px] text-[#7C2D26]">
                    THRD-106
                  </span>
                </div>
              )}

              {bagItems.length === 0 ? (
                <div className="p-10 border border-[#E6E0D6] bg-white text-center space-y-3">
                  <ShoppingBag className="w-8 h-8 text-[#8C847B] mx-auto" />
                  <p className="font-serif text-2xl text-[#181615]">
                    Your Shopping Bag is Empty
                  </p>
                  <p className="text-xs text-[#655E57]">
                    Explore our Linen Tailoring or move saved items from your
                    Wishlist below.
                  </p>
                  <Link
                    href="/search"
                    className="inline-flex items-center gap-1.5 bg-[#181615] text-white px-5 py-2.5 text-xs font-mono uppercase tracking-wider mt-2"
                  >
                    Explore Archive
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              ) : (
                <div className="divide-y divide-[#E6E0D6] border border-[#E6E0D6] bg-white">
                  {bagItems.map((entry) => (
                    <div
                      key={entry.id}
                      className="p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                    >
                      <div className="flex items-start gap-4">
                        <Link href={`/products/${entry.product_id}`}>
                          <img
                            src={entry.product.image_url}
                            alt={entry.product.title}
                            className="w-20 h-28 object-cover bg-[#EFECE6] border border-[#E6E0D6]"
                          />
                        </Link>
                        <div className="space-y-1">
                          <p className="text-[11px] font-mono uppercase text-[#655E57]">
                            {entry.product.brand} · {entry.product.sku}
                          </p>
                          <Link
                            href={`/products/${entry.product_id}`}
                            className="font-serif text-xl text-[#181615] hover:text-[#7C2D26]"
                          >
                            {entry.product.title}
                          </Link>
                          <p className="text-xs font-mono text-[#57514B]">
                            Size: <strong>{entry.selected_size}</strong> ·
                            Colour: <strong>{entry.selected_color}</strong>
                          </p>
                          <p className="text-[11px] font-mono text-[#7C2D26]">
                            Fit Profile: {entry.product.fit_profile}
                          </p>
                        </div>
                      </div>

                      <div className="flex sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto gap-3">
                        <span className="font-mono text-base font-semibold text-[#181615]">
                          {formatINR(entry.line_total)}
                        </span>

                        <div className="flex items-center gap-2">
                          <div className="inline-flex items-center border border-[#D5CEC2]">
                            <button
                              type="button"
                              onClick={() =>
                                updateQty(entry.id, entry.quantity - 1)
                              }
                              className="p-1.5 text-[#181615] hover:bg-[#F5F1EA]"
                            >
                              <Minus className="w-3 h-3" />
                            </button>
                            <span className="px-3 text-xs font-mono">
                              {entry.quantity}
                            </span>
                            <button
                              type="button"
                              onClick={() =>
                                updateQty(entry.id, entry.quantity + 1)
                              }
                              className="p-1.5 text-[#181615] hover:bg-[#F5F1EA]"
                            >
                              <Plus className="w-3 h-3" />
                            </button>
                          </div>

                          <button
                            type="button"
                            onClick={() => removeItem(entry.id)}
                            className="p-1.5 text-[#8C847B] hover:text-[#7C2D26]"
                            title="Remove Item"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* Wishlist Section */}
            <section>
              <div className="pb-4 border-b border-[#E6E0D6] flex items-center justify-between">
                <div>
                  <p className="text-[11px] font-mono uppercase tracking-widest text-[#655E57] flex items-center gap-1.5">
                    <Heart className="w-3.5 h-3.5 text-[#7C2D26]" />
                    Saved Curation
                  </p>
                  <h2 className="font-serif text-2xl text-[#181615] mt-1">
                    Wishlist ({wishlistItems.length} Saved Pieces)
                  </h2>
                </div>
              </div>

              {wishlistItems.length === 0 ? (
                <p className="text-xs text-[#655E57] py-6">
                  No pieces saved in your Wishlist yet. Click the heart icon on
                  any product card to curate your shortlist.
                </p>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
                  {wishlistItems.map((w) => (
                    <div
                      key={w.id}
                      className="p-4 border border-[#E6E0D6] bg-white flex items-center justify-between gap-3"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <img
                          src={w.product.image_url}
                          alt={w.product.title}
                          className="w-16 h-22 object-cover shrink-0"
                        />
                        <div className="min-w-0">
                          <p className="text-[11px] font-mono text-[#655E57] truncate">
                            {w.product.brand}
                          </p>
                          <Link
                            href={`/products/${w.product_id}`}
                            className="font-serif text-base text-[#181615] truncate block hover:text-[#7C2D26]"
                          >
                            {w.product.title}
                          </Link>
                          <p className="text-xs font-mono text-[#181615] mt-0.5">
                            {formatINR(w.product.price)} · Size{" "}
                            {w.selected_size}
                          </p>
                          <div className="flex items-center gap-2 mt-2">
                            <button
                              type="button"
                              onClick={() => moveWishlistToBag(w.id)}
                              className="px-2.5 py-1 bg-[#181615] text-white text-[10px] font-mono uppercase tracking-wider hover:bg-[#7C2D26]"
                            >
                              Move to Bag
                            </button>
                            <button
                              type="button"
                              onClick={() => removeItem(w.id)}
                              className="text-[11px] font-mono text-[#8C847B] hover:text-[#7C2D26]"
                            >
                              Remove
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>

          {/* Right Column: Checkout Simulation */}
          <div className="lg:col-span-5">
            <form
              onSubmit={handleCheckout}
              className="p-6 sm:p-8 border border-[#181615] bg-white space-y-6 sticky top-28"
            >
              <div>
                <p className="text-[11px] font-mono uppercase tracking-widest text-[#7C2D26]">
                  Simulated Order &amp; Funnel Telemetry
                </p>
                <h2 className="font-serif text-2xl text-[#181615] mt-1">
                  Order Summary &amp; Checkout
                </h2>
              </div>

              <div className="space-y-3 text-xs border-y border-[#E6E0D6] py-4 font-mono">
                <div className="flex justify-between">
                  <span className="text-[#655E57]">Bag Subtotal</span>
                  <span>{formatINR(summary?.subtotal || 0)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#655E57]">
                    Tier / Promo Privilege (ATELIER10 = 10% Off)
                  </span>
                  <span className="text-[#2E5A3C]">
                    -
                    {formatINR(
                      promoCode.trim().toUpperCase() === "ATELIER10"
                        ? Math.round((summary?.subtotal || 0) * 0.1)
                        : summary?.tier_discount || 0
                    )}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#655E57]">Express Courier Fee</span>
                  <span>
                    {summary?.shipping_fee === 0
                      ? "COMPLIMENTARY"
                      : formatINR(summary?.shipping_fee || 0)}
                  </span>
                </div>
                <div className="flex justify-between text-base font-semibold pt-2 border-t border-[#E6E0D6] text-[#181615]">
                  <span>Estimated Total</span>
                  <span>
                    {formatINR(
                      Math.max(
                        0,
                        (summary?.subtotal || 0) -
                          (promoCode.trim().toUpperCase() === "ATELIER10"
                            ? Math.round((summary?.subtotal || 0) * 0.1)
                            : summary?.tier_discount || 0) +
                          (summary?.shipping_fee || 0)
                      )
                    )}
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-[11px] font-mono uppercase text-[#181615] mb-1">
                    Destination City &amp; Tier ETA
                  </label>
                  <select
                    value={shippingCity}
                    onChange={(e) => setShippingCity(e.target.value)}
                    className="w-full border border-[#D5CEC2] bg-[#FAF8F5] px-3 py-2 text-xs"
                  >
                    <option value="Bengaluru, KA">
                      Bengaluru, KA (Metro Tier-1 · 48hr Express)
                    </option>
                    <option value="Mumbai, MH">
                      Mumbai, MH (Metro Tier-1 · 48hr Express)
                    </option>
                    <option value="New Delhi, DL">
                      New Delhi, DL (Metro Tier-1 · 48hr Express)
                    </option>
                    <option value="Jaipur, RJ">
                      Jaipur, RJ (Tier-2 Growth · 3-4 Business Days)
                    </option>
                    <option value="Pune, MH">
                      Pune, MH (Tier-2 Growth · 2-3 Business Days)
                    </option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-mono uppercase text-[#181615] mb-1">
                    Payment Method (Demo Simulation)
                  </label>
                  <select
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-full border border-[#D5CEC2] bg-[#FAF8F5] px-3 py-2 text-xs"
                  >
                    <option value="UPI / Instant Bank Transfer">
                      UPI / Instant Bank Transfer
                    </option>
                    <option value="Credit Card (Visa / Mastercard)">
                      Credit Card (Visa / Mastercard)
                    </option>
                    <option value="NetBanking">NetBanking</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-mono uppercase text-[#181615] mb-1">
                    Privilege Code (Try ATELIER10)
                  </label>
                  <input
                    type="text"
                    value={promoCode}
                    onChange={(e) => setPromoCode(e.target.value)}
                    className="w-full border border-[#D5CEC2] bg-[#FAF8F5] px-3 py-2 text-xs font-mono uppercase"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={placingOrder || bagItems.length === 0}
                className="w-full bg-[#7C2D26] hover:bg-[#9E3B33] disabled:bg-[#C7BFB5] text-white py-3.5 text-xs font-mono uppercase tracking-widest transition-colors"
              >
                {placingOrder
                  ? "Confirming Order..."
                  : "Complete Simulated Purchase"}
              </button>

              <p className="text-[11px] text-[#655E57] flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-[#2E5A3C] shrink-0" />
                No real payment gateway required. Fires `checkout_started` &amp;
                `order_placed` events directly into PostgreSQL &amp; Mixpanel.
              </p>
            </form>
          </div>
        </div>
      </div>
    </StorefrontShell>
  );
}
