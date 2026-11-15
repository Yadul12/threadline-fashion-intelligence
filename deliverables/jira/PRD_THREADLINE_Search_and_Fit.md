# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Initiative: Semantic Synonym Search Recovery & Verified Fit Guidance (H2-2026)

| Metadata | Details |
|---|---|
| **Document Owner** | Product Management Intern — Discovery & CX Squad |
| **Engineering Lead** | Staff Full-Stack & Search Ranking Lead |
| **Design Partner** | Principal Product Designer — Editorial Storefront |
| **Data Science Partner** | Consumer Experimentation & Merchandising Analytics |
| **Status** | `IN EXPERIMENTATION (EXP-SEARCH-001)` & `IN PROGRESS (EXP-FIT-002)` |
| **Target Release** | Sprint 24 / Q3-2026 |

---

## 1. Executive Summary & Problem Statement

THREADLINE is a curated contemporary fashion marketplace carrying 6 core departments (*Linen & Resort*, *Contemporary Ethnic*, *Tailored Workwear*, *Architectural Denim*, *Artisanal Footwear*, and *Minimalist Accessories*).

Analysis of 620 customer sessions, 480 search logs, and 96 verified buyer reviews uncovered two high-severity customer friction points hurting conversion:

1. **Zero-Result & Low-Recall Search Dead Ends (`EXP-SEARCH-001`)**:
   - **Data Evidence**: Shoppers frequently search colloquial or synonym terms that do not lexically match our editorial catalog taxonomy—such as `"haldi outfit"`, `"sangeet wear"`, `"shaadi guest"`, `"oversized blazer"`, `"white sneakers"`, or `"office pants"`.
   - Under our baseline lexical search (`control`), these queries return **0 products**, resulting in a **72%+ search abandonment rate** on colloquial queries and lost high-intent GMV.
2. **Pre-Purchase Size & Fit Uncertainty (`EXP-FIT-002`)**:
   - **Data Evidence**: Across negative and neutral customer reviews (`sentiment IN ('negative', 'neutral')`), **`Size and fit`** is the #1 complaint category (`review_id` citations `#4`, `#9`, `#17`, `#28`, `#41`), followed by **`Product images`** studio lighting discrepancies (`review_id` citations `#12`, `#23`, `#39`).
   - Structured silhouettes (e.g., *Raw Indigo Barrel-Leg Jeans*, *Sculpted Bustier Midi Dress*, *Handloom Tissue Silk Kurta Set*) run snug across the ribcage or waist (`fit_feedback = 'runs_small'`), causing shoppers to hesitate on the PDP or order the wrong size.

---

## 2. Objectives & Key Results (OKRs)

| Metric | Baseline (Control) | Target (Treatment) | Guardrail Metric |
|---|---|---|---|
| **Zero-Result Search Rate** | ~29.5% on natural-language queries | **< 8.0%** | Average Search Latency < 150ms |
| **Search Click-Through Rate (CTR)** | 51.2% | **>= 64.0% (+12.8pp)** | Post-Click Bounce Rate <= Baseline |
| **PDP-to-Bag Rate (Structured SKUs)** | 34.0% | **>= 41.0% (+7.0pp)** | Gross Margin / Return Rate |
| **End-to-End Session Conversion** | 21.8% | **>= 25.5%** | Average Order Value (AOV) >= ₹5,800 |

---

## 3. Functional Requirements & User Stories

### Epic 1: `EPIC-SEARCH` — Search Synonym & Occasion Intent Recovery

#### User Story `TL-101` (RICE Score: 216.0 — P0)
> *"As a customer searching with colloquial or occasion terms (e.g., 'haldi outfit', 'office pants', 'oversized blazer'), I want relevant products to appear even when exact keywords don't match product titles so that I don't hit a zero-result dead end."*

**Measurable Acceptance Criteria:**
1. Query normalization maps 15+ core Indian occasion and style synonyms (`haldi`, `sangeet`, `mehendi`, `shaadi`, `office pants`, `linen shirt`, `white sneakers`, `oversized blazer`, `kurti`, `chappal`, `tote`) to canonical catalog tokens and occasion tags.
2. When `treatment` variant is active (`EXP-SEARCH-001`), queries for `"haldi outfit"` or `"oversized blazer"` return `>= 2` relevant products and display a transparent banner: *"Showing expanded occasion & fabric matches for '<query>'"*.
3. When a query still yields 0 exact matches, the storefront renders a **Zero-Result Recovery Shelf** with clickable remedy pills and 4 curated high-rating fallback products instead of an empty page.
4. Every search submission logs `search_submitted` with `experiment_variant`, `results_count`, and `zero_results` flag to PostgreSQL and Mixpanel.

#### User Story `TL-102` (RICE Score: 158.7 — P0)
> *"As a customer browsing a category with a specific size and budget in mind, I want sticky multi-facet filter pills (Category, Size, Color, Fit, Price) and instant sort controls so that I can narrow down suitable products in under 2 clicks."*

**Measurable Acceptance Criteria:**
1. Search & Discovery page (`/search`) supports simultaneous filtering by `category`, `brand`, `size` (`XS`–`XL`), `color`, `fit`, `occasion`, and `max_price`.
2. Active filters appear as removable chips above the product grid with a single-click `Clear all` action.
3. Applying any filter dispatches a structured `filter_applied` telemetry event containing `filter_type`, `filter_value`, and `results_count`.

---

### Epic 2: `EPIC-FIT` — PDP Fit Confidence & Verified Buyer Consensus

#### User Story `TL-103` (RICE Score: 138.0 — P1)
> *"As a shopper uncertain whether a tailored blazer or handloom kurta runs small, I want to see aggregated verified-buyer fit consensus ('Runs Small / True to Size / Runs Large') directly above the size selector so that I can pick the right size with confidence."*

**Measurable Acceptance Criteria:**
1. Product Detail API (`GET /api/storefront/products/{product_id}`) computes real-time `fit_consensus` percentages (`runs_small`, `true_to_size`, `runs_large`) from verified reviews for that SKU.
2. PDP renders a horizontal distribution bar above the size selector showing exact percentage breakdown and a tailored sizing callout when `runs_small >= 40%`.
3. Customers can submit new verified reviews on the PDP specifying their `size_purchased` and `fit_feedback`, which immediately recalculates the SKU's consensus and logs `product_reviewed`.

---

## 4. Experimentation & Rollout Plan

- **Assignment Mechanism**: Deterministic `SHA-256(experiment_id + ":" + user_id)` modulo 100 (`50% Control / 50% Treatment`) implemented in `backend/app/services/experiment_service.py`.
- **Statistical Decision Rule**: Two-tailed two-proportion Z-test (`alpha = 0.05`, 95% confidence interval). Results with `p < 0.05` and `>= 100` exposed users per arm are marked **`Statistically Supported`**; under-powered tests are marked **`Exploratory / Under-powered`** in `/pm/experiments`.
