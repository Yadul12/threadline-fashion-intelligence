"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import {
  API_BASE_URL,
  apiFetch,
  CartState,
  Category,
  DemoPersona,
} from "./api";

interface ToastMessage {
  id: string;
  title: string;
  detail?: string;
  tone?: "default" | "accent" | "error";
}

interface ThreadlineContextValue {
  userId: string;
  setUserId: (id: string) => void;
  activePersona: DemoPersona | null;
  personas: DemoPersona[];
  categories: Category[];
  sessionId: string;
  experimentVariant: "control" | "treatment";
  setExperimentVariant: (v: "control" | "treatment") => void;
  cart: CartState | null;
  refreshCart: () => Promise<void>;
  addToCartOrWishlist: (params: {
    product_id: string;
    selected_size: string;
    selected_color: string;
    quantity?: number;
    item_type: "bag" | "wishlist";
  }) => Promise<void>;
  trackEvent: (
    eventName: string,
    props?: {
      product_id?: string;
      category?: string;
      price?: number;
      brand?: string;
      properties?: Record<string, unknown>;
    }
  ) => Promise<void>;
  liveEventCount: number;
  lastTrackedEvent: string | null;
  toasts: ToastMessage[];
  pushToast: (title: string, detail?: string, tone?: "default" | "accent" | "error") => void;
  dismissToast: (id: string) => void;
}

const ThreadlineContext = createContext<ThreadlineContextValue | null>(null);

export function ThreadlineProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [userId, setUserIdState] = useState<string>("usr_demo_001");
  const [sessionId, setSessionId] = useState<string>("sess_live_init");
  const [experimentVariant, setExperimentVariantState] = useState<
    "control" | "treatment"
  >("treatment");
  const [personas, setPersonas] = useState<DemoPersona[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [cart, setCart] = useState<CartState | null>(null);
  const [liveEventCount, setLiveEventCount] = useState<number>(0);
  const [lastTrackedEvent, setLastTrackedEvent] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const pushToast = useCallback(
    (
      title: string,
      detail?: string,
      tone: "default" | "accent" | "error" = "default"
    ) => {
      const id = Math.random().toString(36).slice(2, 9);
      setToasts((prev) => [...prev.slice(-3), { id, title, detail, tone }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 4200);
    },
    []
  );

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  useEffect(() => {
    const storedSession =
      typeof window !== "undefined"
        ? sessionStorage.getItem("tl_session_id")
        : null;
    if (storedSession) {
      setSessionId(storedSession);
    } else if (typeof window !== "undefined") {
      const generated = `sess_live_${Math.random().toString(36).slice(2, 8)}`;
      sessionStorage.setItem("tl_session_id", generated);
      setSessionId(generated);
    }
  }, []);

  const refreshCart = useCallback(async () => {
    try {
      const data = await apiFetch<CartState>(
        `/api/storefront/cart?user_id=${encodeURIComponent(userId)}`
      );
      setCart(data);
    } catch {
      // ignore initial offline error if backend is starting
    }
  }, [userId]);

  useEffect(() => {
    let active = true;
    async function loadBootstrap() {
      try {
        const data = await apiFetch<{
          categories: Category[];
          demo_personas: DemoPersona[];
        }>(`/api/storefront/bootstrap?user_id=${encodeURIComponent(userId)}`);
        if (!active) return;
        setCategories(data.categories || []);
        setPersonas(data.demo_personas || []);
      } catch {
        // ignore
      }
    }
    loadBootstrap();
    refreshCart();
    return () => {
      active = false;
    };
  }, [userId, refreshCart]);

  const activePersona =
    personas.find((p) => p.id === userId) || personas[0] || null;

  const setUserId = useCallback(
    (id: string) => {
      setUserIdState(id);
      pushToast(
        "Switched Active Customer Persona",
        `Now browsing as ${id} — personalized recommendations & bag updated.`
      );
    },
    [pushToast]
  );

  const setExperimentVariant = useCallback(
    (v: "control" | "treatment") => {
      setExperimentVariantState(v);
      pushToast(
        `Experiment Variant: ${v.toUpperCase()}`,
        v === "treatment"
          ? "Treatment active: Semantic synonym search + sticky Size & Fit filter bar enabled."
          : "Control active: Standard keyword matching without fit callout badges.",
        "accent"
      );
    },
    [pushToast]
  );

  const trackEvent = useCallback(
    async (
      eventName: string,
      props?: {
        product_id?: string;
        category?: string;
        price?: number;
        brand?: string;
        properties?: Record<string, unknown>;
      }
    ) => {
      try {
        await fetch(`${API_BASE_URL}/api/events/track`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            event_name: eventName,
            user_id: userId,
            session_id: sessionId,
            product_id: props?.product_id || null,
            category: props?.category || null,
            price: props?.price ?? null,
            brand: props?.brand || null,
            device_type: activePersona?.primary_device || "desktop_web",
            acquisition_channel:
              activePersona?.acquisition_channel || "editorial_newsletter",
            experiment_variant: experimentVariant,
            properties: props?.properties || {},
          }),
        });
        setLiveEventCount((c) => c + 1);
        setLastTrackedEvent(eventName);
      } catch {
        // non-blocking
      }
    },
    [userId, sessionId, activePersona, experimentVariant]
  );

  const addToCartOrWishlist = useCallback(
    async (params: {
      product_id: string;
      selected_size: string;
      selected_color: string;
      quantity?: number;
      item_type: "bag" | "wishlist";
    }) => {
      try {
        const res = await apiFetch<{ cart: CartState }>(`/api/storefront/cart`, {
          method: "POST",
          body: JSON.stringify({
            user_id: userId,
            session_id: sessionId,
            product_id: params.product_id,
            selected_size: params.selected_size,
            selected_color: params.selected_color,
            quantity: params.quantity || 1,
            item_type: params.item_type,
            experiment_variant: experimentVariant,
          }),
        });
        setCart(res.cart);
        setLiveEventCount((c) => c + 1);
        setLastTrackedEvent(
          params.item_type === "wishlist" ? "wishlist_added" : "add_to_cart"
        );
        pushToast(
          params.item_type === "wishlist"
            ? "Saved to Personal Curation"
            : "Added to Shopping Bag",
          `Size ${params.selected_size} · ${params.selected_color} (Event '${
            params.item_type === "wishlist" ? "wishlist_added" : "add_to_cart"
          }' logged)`,
          "accent"
        );
      } catch (err) {
        pushToast(
          "Could not update bag",
          err instanceof Error ? err.message : "Request failed",
          "error"
        );
      }
    },
    [userId, sessionId, experimentVariant, pushToast]
  );

  return (
    <ThreadlineContext.Provider
      value={{
        userId,
        setUserId,
        activePersona,
        personas,
        categories,
        sessionId,
        experimentVariant,
        setExperimentVariant,
        cart,
        refreshCart,
        addToCartOrWishlist,
        trackEvent,
        liveEventCount,
        lastTrackedEvent,
        toasts,
        pushToast,
        dismissToast,
      }}
    >
      {children}
    </ThreadlineContext.Provider>
  );
}

export function useThreadline() {
  const ctx = useContext(ThreadlineContext);
  if (!ctx) {
    throw new Error("useThreadline must be used inside ThreadlineProvider");
  }
  return ctx;
}
