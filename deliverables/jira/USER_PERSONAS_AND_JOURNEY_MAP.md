# USER PERSONAS & CUSTOMER JOURNEY MAP
## THREADLINE — Fashion Discovery & CX Intelligence

---

## 1. Evidence-Backed User Personas

### Persona 1: Ananya Rao — The Occasion-Driven Contemporary Shopper
- **Demographics**: 26, Product Designer in Bengaluru | Devices: `ios_app` & `mobile_web` | Channel: `instagram_editorial`
- **Shopping Pattern**: Browses THREADLINE ahead of weddings, festive gatherings, and resort weekends. Searches by **vibe and occasion** rather than technical garment names (e.g., *"haldi outfit"*, *"sangeet wear"*, *"vacation dress"*).
- **Core Frustrations**:
  - Typing *"haldi outfit"* on standard fashion marketplaces yields 0 results because products are cataloged under *"Marigold Chanderi Pleated Kurta"* or *"Crushed Tissue Anarkali"*.
  - Studio flash photography makes sheer silk or ivory linen look opaque when it actually requires a lining (`review_id #12`, `#23`).
- **Product Features Built for Ananya**:
  - Occasion synonym expansion engine (`EXP-SEARCH-001` treatment).
  - Curated occasion pills on `/search` (`Festive`, `Resort`, `Evening`, `Workwear`).
  - Zero-result fallback carousels so she never hits a dead end.

---

### Persona 2: Rohan Mehta — The Time-Poor Workwear & Basics Buyer
- **Demographics**: 31, Management Consultant in Mumbai | Devices: `desktop` & `ios_app` | Channel: `organic_search` & `direct`
- **Shopping Pattern**: High AOV (₹6,500+), low browsing patience. Knows his exact size (`L` or `32`) and fabric preference (`100% European Linen` or `Merino Wool`).
- **Core Frustrations**:
  - Clicking into 6 different product pages only to discover Size `L` is out of stock or that `"Relaxed Fit"` actually fits boxy (`review_id #4`, `#17`).
  - Having to re-apply size and price filters every time he tweaks his search query.
- **Product Features Built for Rohan**:
  - Persistent multi-facet filtering (`category + size + fit + max_price`) with URL state synchronization.
  - Verified buyer **Fit Consensus Meter** (`Runs Small / True to Size / Runs Large`) directly above the PDP size selector.

---

### Persona 3: Vikramaditya Sen — Internal Senior PM (Discovery & Merchandising)
- **Role**: Product Manager overseeing Search, Recommendations, and Conversion Funnel at THREADLINE.
- **Workflow Needs**:
  - Needs a unified workspace (`/pm`) that connects **quantitative funnel drop-offs** (`/pm/funnel`, `/pm/search`) with **qualitative customer review evidence** (`/pm/feedback`) and **statistical A/B test outcomes** (`/pm/experiments`).
  - Refuses to trust black-box AI summaries that invent quotes or hide sample sizes; requires clickable `review_id` citations and explicit `p-value` + 95% CI badges.

---

## 2. End-to-End Customer Journey Map

```
+-------------------+--------------------+--------------------+--------------------+--------------------+
| JOURNEY STAGE     | 1. DISCOVERY       | 2. SEARCH & FILTER | 3. PDP EVALUATION  | 4. BAG & CHECKOUT  |
+-------------------+--------------------+--------------------+--------------------+--------------------+
| Customer Action   | Lands on `/` from  | Searches "haldi    | Inspects fabric,   | Adds SKU to Bag,   |
|                   | Instagram or       | outfit" or applies | reviews, and       | checks free-ship   |
|                   | Organic Search     | Size M + Linen     | selects Size M     | threshold, orders  |
+-------------------+--------------------+--------------------+--------------------+--------------------+
| Telemetry Event   | `homepage_viewed`  | `search_submitted` | `product_viewed`   | `add_to_cart`      |
| Logged            |                    | `filter_applied`   | `wishlist_added`   | `checkout_started` |
|                   |                    | `search_result_    |                    | `order_placed`     |
|                   |                    |  clicked`          |                    |                    |
+-------------------+--------------------+--------------------+--------------------+--------------------+
| Key Customer      | Overwhelmed by     | Zero results on    | Uncertainty if     | Unexpected         |
| Pain Point        | generic promo      | colloquial terms;  | handloom silk or   | shipping charges   |
|                   | banners            | losing filter      | denim runs small   | or slow checkout   |
|                   |                    | context            | (`Size and fit`)   |                    |
+-------------------+--------------------+--------------------+--------------------+--------------------+
| THREADLINE        | Editorial story    | Synonym & occasion | Verified Buyer Fit | Free shipping      |
| Product Solution  | blocks + live      | query expansion +  | Consensus bar +    | tracker (₹2,999+)  |
|                   | A/B switcher       | Zero-Result shelf  | fabric care specs  | + 1-click demo pay |
+-------------------+--------------------+--------------------+--------------------+--------------------+
| Primary KPI       | Bounce Rate &      | Search CTR (%) &   | PDP-to-Bag Rate    | Bag Completion &   |
| Measured in `/pm` | Session Depth      | Zero-Result %      | (%) & Wishlist %   | Order CVR (%)      |
+-------------------+--------------------+--------------------+--------------------+--------------------+
```
