# AGILE CEREMONIES, STAKEHOLDER LOG & RELEASE NOTES
## THREADLINE — Discovery & Customer Experience Squad (Sprint 24)

---

## 1. Sprint 24 Planning Summary

- **Sprint Goal**: Eliminate zero-result dead ends on top 25 colloquial fashion queries (`EXP-SEARCH-001`) and launch Verified Buyer Fit Consensus on all 24 catalog SKUs (`EXP-FIT-002`).
- **Sprint Duration**: 2 Weeks (10 Working Days)
- **Squad Capacity**: 34 Story Points (2 Backend Engineers, 2 Frontend Engineers, 1 Product Designer, 1 PM Intern)
- **Committed Backlog Items** (see `deliverables/jira/jira_backlog_import.csv` for full RICE table):
  1. `RM-001` — Semantic Synonym & Occasion Search Expansion (`IN_PROGRESS`, RICE: `216.0`, 5 pts)
  2. `RM-002` — Verified Buyer Fit Consensus Bar & Size Recommendation (`IN_PROGRESS`, RICE: `138.0`, 5 pts)
  3. `RM-003` — Zero-Result Smart Recovery Carousel & Query Correction (`PLANNED`, RICE: `158.7`, 3 pts)
  4. `RM-004` — Natural Daylight vs Studio Swatch Toggle on PDP (`PLANNED`, RICE: `117.0`, 5 pts)

---

## 2. Stakeholder Feedback Log

| Date | Stakeholder | Role / Department | Feedback / Concern Raised | PM Resolution & Action Taken |
|---|---|---|---|---|
| 2026-11-02 | Meera Krishnan | Head of Merchandising | *"If synonym expansion maps 'haldi outfit' too broadly, we might show dark evening gowns that ruin editorial relevance."* | Restricted occasion synonym mapping for `haldi` specifically to `Marigold`, `Mustard`, `Ivory`, and `Festive` ethnic tags (`search_service.py`). Added A/B switch to compare CTR. |
| 2026-11-05 | Siddharth Verma | VP of Engineering | *"We cannot block checkout or page loads if the Gemini API is rate-limited or if Mixpanel is unreachable."* | Implemented non-blocking Mixpanel adapter with local PostgreSQL/SQLite persistence (`events.py`) and deterministic SQL-backed fallback in `genai_service.py`. |
| 2026-11-09 | Rhea Kapoor | Customer Experience Lead | *"Our support team receives 40+ weekly tickets about linen trousers shrinking or kurtas running tight across the bust. Can PM surface those exact reviews?"* | Built `/pm/feedback` with category filtering (`Size and fit`), CSV/XLSX user research upload, and clickable `review_id` evidence drawer. |
| 2026-11-12 | Arjun Nair | Principal Data Scientist | *"PMs often call an experiment a winner after 30 sessions. Make sure the dashboard flags under-powered tests clearly."* | Added two-proportion Z-test with 95% confidence intervals and explicit `Statistically Supported` vs `Exploratory / Under-powered` badges in `/pm/experiments`. |

---

## 3. Release Notes — `v2.4.0` (Discovery & Intelligence Release)

### Customer Storefront Highlights
- **New**: Live A/B Variant Switcher (`Control` vs `Treatment`) in the top utility bar so reviewers can experience both lexical and synonym-expanded search side by side.
- **New**: Search Autocomplete & Instant Product Previews in the header search bar and `/search` discovery page.
- **New**: Zero-Result Recovery Shelf offering one-click occasion/fabric pills and curated bestsellers when an obscure query returns 0 matches.
- **New**: Verified Buyer **Fit Consensus Meter** (`Runs Small`, `True to Size`, `Runs Large`) on every Product Detail Page (`/products/[id]`), plus live customer review submission.

### Internal PM Workspace Highlights
- **New**: Executive Overview (`/pm`) with weekly acquisition cohort retention heatmap, device performance split, and 1-click Excel KPI Pack export.
- **New**: 8-Step Customer Funnel (`/pm/funnel`) filterable by Device Type, Acquisition Channel, and Experiment Variant.
- **New**: GenAI Customer Feedback Intelligence (`/pm/feedback`) with grounded `review_id` citations, deterministic fallback mode, and live CSV/XLSX research import.
- **New**: Experimentation Centre (`/pm/experiments`) with SHA-256 deterministic user bucketing, two-proportion Z-tests, and interactive hypothesis creation.
- **New**: SQL & Tableau BI Studio (`/pm/sql-tableau`) featuring 9 live runnable analytical SQL queries and 4 downloadable Tableau extracts.

---

## 4. Sprint 23 Retrospective Notes

### What Went Well
- Pairing SQL event telemetry (`events` table) with every storefront interaction gave us immediate visibility into where mobile web shoppers dropped off between `search_submitted` and `product_viewed`.
- Building the deterministic GenAI fallback early meant QA and offline reviewers got identical schema-validated JSON insights with real `review_id` citations even without an API key.

### What Could Be Improved
- Initial seed scripts inserted child telemetry events before flushing parent session records under strict foreign-key enforcement; resolved by enforcing explicit parent flushes in `seed.py` and adding automated pytest assertions (`test_platform.py`).

### Action Items for Sprint 25
- [ ] Owner: **PM Intern + Merchandising** — Audit top 15 SKUs with `runs_small > 50%` and update vendor size-chart grading tables.
- [ ] Owner: **Frontend Lead** — Run `EXP-FIT-002` to 500+ exposed sessions per variant to reach 80% statistical power on return-rate reduction.
