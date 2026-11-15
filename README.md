# THREADLINE — Fashion Discovery & Customer Experience Intelligence Platform

An end-to-end **Customer Fashion Storefront** and **Internal Product Manager Intelligence Workspace** built to solve real e-commerce discovery, search relevance, and size/fit confidence problems through behavioral analytics, controlled A/B experimentation, SQL/Tableau BI, and grounded GenAI synthesis.

---

## 1. Architecture & Dual-Application Surface

THREADLINE consists of two tightly connected applications backed by a single relational database and live event telemetry pipeline:

### A. Customer Storefront (`/`, `/search`, `/products/[id]`, `/bag`)
- **Editorial Fashion Aesthetic**: Warm alabaster canvas (`#FAF8F5`), deep espresso ink (`#181615`), terracotta burgundy accents (`#7C2D26`), `Cormorant Garamond` editorial headings, and `Plus Jakarta Sans` UI controls.
- **Search & Discovery Engine (`/search`)**:
  - Real-time autocomplete suggestions & product previews.
  - Multi-facet filtering by **Category**, **Brand**, **Size (`XS`–`XL`)**, **Color**, **Fit**, **Occasion**, and **Price Range**, plus sorting by **Relevance**, **Popularity**, **Price**, **Rating**, and **Discount**.
  - **Live A/B Search Experiment (`EXP-SEARCH-001`)**: Toggle between **Control** (strict lexical matching) and **Treatment** (colloquial & occasion synonym expansion—try searching `"haldi outfit"`, `"sangeet wear"`, `"oversized blazer"`, or `"white sneakers"` in both variants).
  - **Zero-Result Recovery**: Displays actionable recovery pills and curated high-rating alternatives when a query yields zero matches.
- **Product Detail Page (`/products/[id]`)**:
  - High-resolution editorial gallery, fabric & care metadata, size & color selectors, and related products.
  - **Verified Buyer Fit Consensus**: Real-time distribution of `Runs Small`, `True to Size`, and `Runs Large` aggregated from verified reviews.
  - **Interactive Review Submission**: Submit a verified review with fit feedback and watch the SKU's consensus and PM Feedback Intelligence update immediately.
- **Shopping Journey (`/bag`)**:
  - Persistent Wishlist and Shopping Bag, free-shipping threshold meter (`₹2,999`), promo code simulation (`THREAD10`, `FIRST15`), and instant demo checkout creating real `orders` and `order_items` records.

### B. Product Manager Workspace (`/pm/*`)
- **Executive Overview (`/pm`)**: Active users (DAU/WAU/MAU), session conversion rate, search volume, add-to-bag rate, gross revenue, weekly cohort retention matrix, device performance breakdown, and 1-click **Excel KPI Pack (`.xlsx`)** export.
- **Customer Funnel Analytics (`/pm/funnel`)**: 8-step session conversion funnel (`homepage_viewed` -> `search_submitted` -> `search_result_clicked` -> `product_viewed` -> `wishlist_added` -> `add_to_cart` -> `checkout_started` -> `order_placed`) sliceable by **Device Type**, **Acquisition Channel**, and **A/B Variant**.
- **Search Intelligence (`/pm/search`)**: Top search queries, zero-result search leakage table, search CTR vs abandonment scatter, and one-click storefront query testing.
- **Customer Feedback Intelligence (`/pm/feedback`)**:
  - Sentiment & complaint taxonomy breakdown (`Size and fit`, `Search relevance`, `Product images`, `Product quality`, etc.).
  - **GenAI Synthesis with Traceable Evidence**: Summarizes customer pain points and recommends product fixes where every single insight links to the exact supporting `review_id` records.
  - **CSV / XLSX Research Import**: Upload external customer survey or review files (or load the built-in sample survey batch) to dynamically enrich the dataset.
- **Experimentation Centre (`/pm/experiments`)**:
  - Deterministic `SHA-256` user bucketing (`Control` vs `Treatment`).
  - **Two-Proportion Z-Test Statistical Engine**: Computes conversion lift, 95% confidence intervals, two-tailed `p-values`, sample size targets, and explicit **`Statistically Supported`** vs **`Exploratory / Under-powered`** badges.
  - Create new experiments and hypotheses directly from the UI.
- **Product Roadmap & Agile Hub (`/pm/roadmap`)**:
  - Interactive **RICE Prioritization Table** (`(Reach * Impact * Confidence) / Effort`) with status filters, new feature creation modal, **Jira CSV Export**, and embedded PRD / Personas / Sprint Retrospective viewer.
- **SQL & Tableau BI Studio (`/pm/sql-tableau`)**:
  - Run 9 production analytical SQL queries live against the database and inspect the 4 Tableau BI views (`vw_tableau_*`) with CSV/XLSX downloads.

---

## 2. Technology Stack & Integration Transparency

| Layer | Technology | Status & Fallback Behavior |
|---|---|---|
| **Frontend** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, Recharts, Lucide Icons | Fully implemented & production-build verified (`npm run build`). |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, OpenPyXL | Fully implemented & verified via `pytest` (10/10 passing). |
| **Database** | PostgreSQL (`DATABASE_URL`) with SQLite Local Fallback | Full PostgreSQL DDL migrations (`backend/migrations/`). Automatically uses PostgreSQL when `DATABASE_URL` is reachable, or seamlessly falls back to local relational SQLite (`threadline.db` with `PRAGMA foreign_keys=ON`) and reports `database_mode` honestly. |
| **Product Analytics** | Mixpanel HTTP Ingestion + Relational SQL Event Store | Dual-writes events to Mixpanel when `MIXPANEL_TOKEN` is set in `.env`; always persists events to the `events` SQL table and reports honest status (`local_sql_adapter` when unset). |
| **GenAI Intelligence** | Google Gemini API (`google-genai` SDK, `gemini-2.5-flash`) | Uses live Gemini structured synthesis when `GEMINI_API_KEY` is configured; automatically falls back to a deterministic SQL evidence engine with zero hallucinated quotes or IDs when unset. |
| **BI & Operations** | Tableau `.twb` + Extracts, Jira CSV, Excel `.xlsx`, Figma Tokens & SVG | All files generated and committed under `deliverables/`. |

---

## 3. Repository Structure

```text
threadline-fashion-intelligence/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point & health status
│   │   ├── config.py                # Environment configuration (.env)
│   │   ├── database.py              # PostgreSQL / SQLite engine & session management
│   │   ├── models.py                # 13 relational SQLAlchemy models + indexes
│   │   ├── schemas.py               # Pydantic request/response contracts
│   │   ├── seed.py                  # Deterministic seed data + deliverables generator
│   │   ├── routers/                 # storefront, events, analytics, feedback, experiments, roadmap, exports
│   │   └── services/                # analytics, search, experiment (Z-test), genai, export (XLSX/CSV)
│   ├── migrations/
│   │   ├── 001_initial_schema.sql   # PostgreSQL DDL schema & indexes
│   │   └── 002_tableau_views.sql    # 4 Tableau BI SQL views
│   ├── tests/
│   │   └── test_platform.py         # End-to-end automated pytest suite (10 tests)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                     # Storefront (/, /search, /products/[id], /bag) & PM (/pm/*)
│   │   ├── components/storefront/   # StorefrontShell, ProductCard
│   │   └── lib/                     # Typed API client (api.ts) & session/AB store (store.tsx)
│   ├── package.json
│   └── Dockerfile
├── deliverables/
│   ├── sql/                         # schema_postgresql.sql, tableau_views.sql, analytical_queries.sql
│   ├── tableau/                     # THREADLINE_Discovery_Intelligence.twb, setup spec, CSV/XLSX extracts
│   ├── jira/                        # jira_backlog_import.csv, PRD, Personas & Journey Map, Agile Ceremonies
│   └── figma/                       # design-tokens.json, FIGMA_DESIGN_SYSTEM_AND_HANDOFF.md, SVG wireframes
├── docker-compose.yml               # Full-stack PostgreSQL 16 + FastAPI + Next.js orchestration
└── .env.example
```

---

## 4. Quickstart Instructions

### Option 1: Local Development (Zero Docker Required)

1. **Start the FastAPI Backend** (automatically seeds `threadline.db` and generates `deliverables/` extracts on first startup):
   ```powershell
   cd backend
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   - Backend API & Swagger Docs: `http://localhost:8000/docs`
   - Health & Integration Status: `http://localhost:8000/api/health`

2. **Start the Next.js Frontend**:
   ```powershell
   cd frontend
   npm run dev
   ```
   - Customer Storefront: `http://localhost:3000`
   - Internal PM Workspace: `http://localhost:3000/pm`

3. **Run the Automated Test Suite**:
   ```powershell
   cd backend
   .\.venv\Scripts\pytest.exe -v
   ```

### Option 2: Docker Compose (PostgreSQL 16 + Backend + Frontend)

```bash
cp .env.example .env
docker compose up --build
```

---

## 5. Deployment Guide (Vercel + Render/Railway + Neon/Supabase PostgreSQL)

1. **Database (PostgreSQL)**:
   - Provision a managed PostgreSQL instance (e.g., Neon, Supabase, or Railway).
   - Set `DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:5432/<dbname>`.
2. **Backend (FastAPI on Render / Railway / Fly.io)**:
   - Deploy `backend/` using `backend/Dockerfile` or start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
   - Configure optional environment variables: `GEMINI_API_KEY`, `MIXPANEL_TOKEN`, `CORS_ORIGINS`.
3. **Frontend (Vercel)**:
   - Import the repository into Vercel with Root Directory set to `frontend`.
   - Set environment variable `NEXT_PUBLIC_API_URL=https://<your-fastapi-backend-domain>/api`.
