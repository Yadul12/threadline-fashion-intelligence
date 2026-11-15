export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" && window.location.hostname !== "localhost"
    ? ""
    : "http://localhost:8000");

export interface ProductColor {
  name: string;
  hex: string;
}

export interface Product {
  id: string;
  sku: string;
  title: string;
  subtitle: string;
  brand: string;
  category_id: string;
  category_name: string;
  department: string;
  subcategory: string;
  price: number;
  original_price: number;
  discount_pct: number;
  fabric: string;
  fit_profile: string;
  fit_notes: string;
  description: string;
  care_instructions: string;
  occasion: string;
  available_sizes: string[];
  available_colors: ProductColor[];
  primary_color: string;
  image_url: string;
  secondary_image_url: string;
  rating_avg: number;
  review_count: number;
  popularity_score: number;
  return_rate_pct: number;
  is_featured: boolean;
  is_new_arrival: boolean;
  stock_count: number;
}

export interface Category {
  id: string;
  slug: string;
  name: string;
  parent_department: string;
  editorial_tagline: string;
}

export interface DemoPersona {
  id: string;
  full_name: string;
  persona_segment: string;
  preferred_size: string;
  primary_device: string;
  acquisition_channel: string;
}

export interface CartEntry {
  id: string;
  product_id: string;
  selected_size: string;
  selected_color: string;
  quantity: number;
  item_type: "bag" | "wishlist";
  line_total: number;
  product: Product;
}

export interface CartState {
  user_id: string;
  bag_items: CartEntry[];
  wishlist_items: CartEntry[];
  summary: {
    bag_count: number;
    wishlist_count: number;
    subtotal: number;
    tier_discount: number;
    shipping_fee: number;
    free_shipping_threshold: number;
    amount_for_free_shipping: number;
    total_amount: number;
  };
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    let errDetail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      errDetail = body.detail || errDetail;
    } catch {
      // ignore
    }
    throw new Error(errDetail);
  }
  return res.json();
}

export function getExportDownloadUrl(
  dataset:
    | "kpi_report"
    | "customer_feedback"
    | "search_analysis"
    | "experiment_template"
    | "jira_backlog"
    | "tableau_extract",
  format: "xlsx" | "csv" = "xlsx"
): string {
  return `${API_BASE_URL}/api/exports/download?dataset=${dataset}&format=${format}`;
}

export function formatINR(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount || 0);
}
