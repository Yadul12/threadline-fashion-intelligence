# THREADLINE — Tableau Business Intelligence Specification & Setup Guide

> **Transparency Note**: Tableau Server / Tableau Cloud is not connected via cloud credentials in this local repository. Instead, THREADLINE ships:
> 1. **Four PostgreSQL / SQLite BI Views** (`backend/migrations/002_tableau_views.sql` and `deliverables/sql/tableau_views.sql`)
> 2. **Materialized CSV & Multi-Sheet XLSX Extracts** (`deliverables/tableau/extracts/`) automatically refreshed on backend boot and downloadable anytime via the PM Workspace (`/pm/sql-tableau` or `GET /api/exports/tableau-workbook-data.xlsx`)
> 3. **A Tableau Desktop `.twb` Workbook (`THREADLINE_Discovery_Intelligence.twb`)** wired directly to the local `./extracts/vw_tableau_*.csv` files.

---

## 1. Connecting Tableau Desktop or Tableau Public

### Option A: Open the Bundled `.twb` File Directly
1. Open **Tableau Desktop** (2022.1 or newer).
2. Open `deliverables/tableau/THREADLINE_Discovery_Intelligence.twb`.
3. If prompted for extract locations, point to `deliverables/tableau/extracts/`.

### Option B: Live PostgreSQL Connection
1. Open **Tableau Desktop** -> **Connect To a Server** -> **PostgreSQL**.
2. Enter your database credentials from `.env` (`Server: localhost`, `Port: 5432`, `Database: threadline`, `Username: postgres`).
3. Run `deliverables/sql/tableau_views.sql` against your database if not already initialized.
4. Drag any of the 4 BI views onto the canvas:
   - `vw_tableau_daily_funnel`
   - `vw_tableau_search_intelligence`
   - `vw_tableau_category_merchandising`
   - `vw_tableau_feedback_intelligence`

### Option C: Multi-Sheet Excel Extract (`THREADLINE_Tableau_BI_Extracts.xlsx`)
1. Open **Tableau Desktop** or **Tableau Public** -> **Connect To a File** -> **Microsoft Excel**.
2. Select `deliverables/tableau/extracts/THREADLINE_Tableau_BI_Extracts.xlsx` (or click **Download Multi-Sheet XLSX** in `/pm/sql-tableau`).

---

## 2. BI View Data Dictionary & Field Definitions

### View 1: `vw_tableau_daily_funnel`
Daily session-grain conversion funnel segmented by device and acquisition channel.

| Field Name | Data Type | Role | Description |
|---|---|---|---|
| `activity_date` | `DATE` | Dimension | Session start calendar date |
| `device_type` | `VARCHAR` | Dimension | `mobile_web`, `ios_app`, `android_app`, `desktop` |
| `acquisition_channel` | `VARCHAR` | Dimension | `organic_search`, `instagram_editorial`, `paid_search`, `direct`, `crm_newsletter` |
| `total_sessions` | `INTEGER` | Measure | Count of distinct `session_id` |
| `active_users` | `INTEGER` | Measure | Count of distinct `user_id` |
| `homepage_sessions` | `INTEGER` | Measure | Sessions firing `homepage_viewed` |
| `search_sessions` | `INTEGER` | Measure | Sessions firing `search_submitted` |
| `search_click_sessions` | `INTEGER` | Measure | Sessions firing `search_result_clicked` |
| `pdp_sessions` | `INTEGER` | Measure | Sessions firing `product_viewed` |
| `wishlist_sessions` | `INTEGER` | Measure | Sessions firing `wishlist_added` |
| `atc_sessions` | `INTEGER` | Measure | Sessions firing `add_to_cart` |
| `checkout_sessions` | `INTEGER` | Measure | Sessions firing `checkout_started` |
| `order_sessions` | `INTEGER` | Measure | Sessions firing `order_placed` |
| `gross_revenue_inr` | `NUMERIC` | Measure | Total completed order revenue (INR) |

### View 2: `vw_tableau_search_intelligence`
Query-level search volume, zero-result incidence, click-through rate, and A/B variant attribution.

| Field Name | Data Type | Role | Description |
|---|---|---|---|
| `search_date` | `DATE` | Dimension | Date query was submitted |
| `normalized_query` | `VARCHAR` | Dimension | Lowercased, trimmed search query |
| `experiment_variant` | `VARCHAR` | Dimension | `control` (strict lexical) vs `treatment` (synonym & attribute recovery) |
| `device_type` | `VARCHAR` | Dimension | User's device platform |
| `search_volume` | `INTEGER` | Measure | Number of search submissions |
| `avg_results_returned` | `NUMERIC` | Measure | Mean catalog items returned |
| `zero_result_searches` | `INTEGER` | Measure | Count of searches returning `0` items |
| `clicked_searches` | `INTEGER` | Measure | Count of searches with >=1 PDP click |
| `abandoned_searches` | `INTEGER` | Measure | Count of searches with 0 PDP clicks |
| `search_ctr_pct` | `NUMERIC` | Measure | `clicked_searches / search_volume * 100` |
| `abandonment_rate_pct` | `NUMERIC` | Measure | `abandoned_searches / search_volume * 100` |

### View 3: `vw_tableau_category_merchandising`
SKU-level discovery, add-to-bag, purchase velocity, and review rating metrics.

| Field Name | Data Type | Role | Description |
|---|---|---|---|
| `product_id` | `VARCHAR` | Dimension | Primary SKU identifier (e.g., `PRD-001`) |
| `sku` | `VARCHAR` | Dimension | Warehouse SKU code |
| `product_title` | `VARCHAR` | Dimension | Full product title |
| `brand` | `VARCHAR` | Dimension | Brand label (`Atelier Threadline`, `Kora Studio`, etc.) |
| `category_name` | `VARCHAR` | Dimension | Parent category (`Linen & Resort`, `Contemporary Ethnic`, etc.) |
| `selling_price` | `INTEGER` | Measure | Current selling price (INR) |
| `mrp` | `INTEGER` | Measure | Original MRP (INR) |
| `discount_pct` | `INTEGER` | Measure | Markdown percentage |
| `fabric` | `VARCHAR` | Dimension | Primary fabric composition |
| `fit_type` | `VARCHAR` | Dimension | Fit cut (`Relaxed Fit`, `Tailored Fit`, `Architectural`) |
| `avg_rating` | `NUMERIC` | Measure | Catalog rating (1.0 - 5.0) |
| `pdp_views` | `INTEGER` | Measure | Distinct sessions viewing PDP |
| `wishlist_adds` | `INTEGER` | Measure | Distinct sessions adding to wishlist |
| `add_to_carts` | `INTEGER` | Measure | Distinct sessions adding to shopping bag |
| `units_sold` | `INTEGER` | Measure | Total units ordered |
| `realized_revenue_inr` | `NUMERIC` | Measure | Realized order item revenue (INR) |

### View 4: `vw_tableau_feedback_intelligence`
Review-level customer sentiment, complaint taxonomy, and fit feedback joined with SKU attributes.

| Field Name | Data Type | Role | Description |
|---|---|---|---|
| `review_id` | `INTEGER` | Dimension | Unique review ID used for GenAI evidence citation |
| `review_date` | `DATE` | Dimension | Date review was submitted |
| `product_id` | `VARCHAR` | Dimension | Reviewed SKU ID |
| `product_title` | `VARCHAR` | Dimension | Reviewed SKU title |
| `brand` | `VARCHAR` | Dimension | Brand name |
| `category_name` | `VARCHAR` | Dimension | Category name |
| `rating` | `INTEGER` | Measure | Star rating (`1` to `5`) |
| `sentiment` | `VARCHAR` | Dimension | `positive`, `neutral`, `negative` |
| `complaint_category` | `VARCHAR` | Dimension | `Size and fit`, `Search relevance`, `Product images`, `Product quality`, `Delivery experience`, `Pricing`, `Checkout experience`, `None` |
| `fit_feedback` | `VARCHAR` | Dimension | `runs_small`, `true_to_size`, `runs_large` |
| `verified_purchase` | `BOOLEAN` | Dimension | Verified buyer indicator |
| `size_purchased` | `VARCHAR` | Dimension | Size purchased (`XS`, `S`, `M`, `L`, `XL`) |

---

## 3. Recommended Tableau Calculated Fields

Copy these formulas into Tableau Desktop when building custom worksheets:

```tableau
// 1. Session Conversion Rate (CVR %)
SUM([order_sessions]) / ZN(SUM([total_sessions]))

// 2. Search Click-Through Rate (CTR %)
SUM([clicked_searches]) / ZN(SUM([search_volume]))

// 3. Zero-Result Search Rate (%)
SUM([zero_result_searches]) / ZN(SUM([search_volume]))

// 4. PDP-to-Bag Rate (%)
SUM([atc_sessions]) / ZN(SUM([pdp_sessions]))

// 5. Bag-to-Order Completion Rate (%)
SUM([order_sessions]) / ZN(SUM([atc_sessions]))

// 6. Negative Review Incidence (%)
SUM(IF [sentiment] = "negative" THEN 1 ELSE 0 END) / COUNT([review_id])
```
