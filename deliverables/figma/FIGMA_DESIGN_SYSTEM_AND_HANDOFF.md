# THREADLINE — Figma Design System & Engineering Handoff Specification

> **Integration Transparency Notice:** No external Figma cloud account is connected in this environment, so we do **not** claim an external Figma cloud URL exists. Instead, this package provides the complete W3C Design Tokens (`design-tokens.json` compatible with Figma Tokens Studio), SVG component sheets (`assets/storefront_and_pm_wireframe_sheet.svg` ready for direct drag-and-drop into Figma), responsive frame specifications, and interaction state documentation.

---

## 1. Visual Direction & Dual-Surface Philosophy

THREADLINE separates its visual language into two distinct, purpose-built environments:

1. **Customer Storefront (`/`, `/search`, `/products/[id]`, `/bag`)**
   - **Aesthetic:** Editorial fashion house & contemporary garment archive.
   - **Palette:** Warm archival paper (`#FAF8F5`), deep charcoal ink (`#181615`), warm stone (`#655E57`), and restrained oxblood burgundy (`#7C2D26`).
   - **Typography:** High-contrast editorial serif (`Cormorant Garamond`) paired with humanist sans (`Plus Jakarta Sans`) and tabular monospace (`JetBrains Mono`) for SKUs, prices, and GSM weights.
   - **Anti-Patterns Strictly Avoided:** Zero purple/blue AI gradients, zero glowing neon borders, zero glassmorphism blobs, zero fake notification popups.

2. **Product Manager Intelligence Workspace (`/pm/*`)**
   - **Aesthetic:** High-density institutional product analytics (inspired by Linear, Mixpanel, and Stripe Sigma).
   - **Layout:** Fixed 256px dark navigation sidebar (`#141413`) with a 12-column analytical canvas (`#F4F3F0`) and 1px hairline borders (`#E2E0DC`).

---

## 2. Responsive Frame Specifications

| Frame Name | Viewport Width | Grid System | Key Components |
| :--- | :--- | :--- | :--- |
| `01_Storefront_Desktop` | `1440px × 2400px` | 12 cols, `24px` gutter, `32px` margin | Telemetry Bar, Editorial Header, Split Hero, 3-Up & 4-Up Product Grid |
| `02_Storefront_Mobile` | `390px × 1800px` | 4 cols, `16px` gutter, `16px` margin | Sticky Search Header, Collapsible Filter Drawer, 1-Up Product Feed |
| `03_Search_Discovery_AB` | `1440px × 1600px` | 3-col Sidebar + 9-col Results | Sticky Treatment Fit Ribbon, Zero-Result Recovery Panel |
| `04_PDP_Fit_Spectrum` | `1440px × 1900px` | 7-col Gallery + 5-col Buy Box | Verified Buyer Fit Consensus Bar (`THRD-103`), Live VoC Review Form |
| `05_PM_Workspace_Shell` | `1440px × 1024px` | `256px` Rail + Fluid `1184px` Canvas | 7 KPI Strip, Recharts Funnel/Cohort Charts, SQL & Tableau Inspector |

---

## 3. Core Reusable Component Anatomy & States

### A. `ProductCard` (`frontend/src/components/storefront/ProductCard.tsx`)
- **Aspect Ratio:** `3:4` vertical editorial portrait container (`#EFECE6` placeholder skeleton).
- **Variants:**
  - `variant="control"`: Displays image, New Season / Discount tags, brand, title, fabric composition, price, and quick-add size button.
  - `variant="treatment"`: Adds the bottom-docked **Verified Buyer Fit Callout Bar** (`Fit: Runs Small - Size Up` in `#FFF5F2` terracotta tint or `Fit: True to Size` in `#FAF8F5`) + real-time availability for the active persona's preferred size.
- **Interaction States:** Default (`border-[#E6E0D6]`), Hover (`border-[#181615]`, `scale-[1.02]` image transition), Loading (`animate-pulse` skeleton).

### B. `VerifiedFitSpectrum` (`frontend/src/app/products/[id]/page.tsx`)
- Displays aggregated SQL percentages for `Runs Small`, `True to Size`, and `Runs Large` alongside specific tailor notes (e.g., *"Structured non-stretch waistband runs 1.5 cm narrower than standard sizing"*).

### C. `ExperimentVerdictBadge` (`frontend/src/app/pm/experiments/page.tsx`)
- **States:**
  - `Statistically Supported Winner (p < 0.05)`: Forest green border (`#2E5A3C`) on `#F4F9F5` when `p_value < 0.05` AND `total_exposed >= target_sample_size`.
  - `Exploratory — Under-Powered Sample Size`: Warm amber-terracotta border (`#D4B895`) on `#FFF9F2` when sample size is below target MDE threshold.
  - `Inconclusive — Null Hypothesis Not Rejected`: Neutral slate border when `p_value >= 0.05`.
