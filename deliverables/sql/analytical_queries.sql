-- =============================================================================
-- THREADLINE — Fashion Discovery & Customer Experience Intelligence Platform
-- Production SQL Analytical Queries (PostgreSQL & SQLite 3.35+ Compatible)
-- =============================================================================

-- 1. FULL-JOURNEY CONVERSION FUNNEL (8-Step Session Funnel)
-- Evaluates unique sessions progressing from Homepage -> Order Placed
WITH session_steps AS (
    SELECT
        session_id,
        MAX(CASE WHEN event_name = 'homepage_viewed' THEN 1 ELSE 0 END) AS step_1_homepage,
        MAX(CASE WHEN event_name = 'search_submitted' THEN 1 ELSE 0 END) AS step_2_search,
        MAX(CASE WHEN event_name = 'search_result_clicked' THEN 1 ELSE 0 END) AS step_3_search_click,
        MAX(CASE WHEN event_name = 'product_viewed' THEN 1 ELSE 0 END) AS step_4_pdp_view,
        MAX(CASE WHEN event_name = 'wishlist_added' THEN 1 ELSE 0 END) AS step_5_wishlist,
        MAX(CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END) AS step_6_add_to_cart,
        MAX(CASE WHEN event_name = 'checkout_started' THEN 1 ELSE 0 END) AS step_7_checkout,
        MAX(CASE WHEN event_name = 'order_placed' THEN 1 ELSE 0 END) AS step_8_order
    FROM events
    GROUP BY session_id
)
SELECT
    COUNT(*) AS total_sessions,
    SUM(step_1_homepage) AS homepage_viewed_sessions,
    SUM(step_2_search) AS search_submitted_sessions,
    SUM(step_3_search_click) AS search_result_clicked_sessions,
    SUM(step_4_pdp_view) AS product_viewed_sessions,
    SUM(step_5_wishlist) AS wishlist_added_sessions,
    SUM(step_6_add_to_cart) AS add_to_cart_sessions,
    SUM(step_7_checkout) AS checkout_started_sessions,
    SUM(step_8_order) AS order_placed_sessions,
    ROUND(100.0 * SUM(step_8_order) / NULLIF(SUM(step_1_homepage), 0), 2) AS overall_conversion_rate_pct
FROM session_steps;

-- 2. DAILY ACTIVE USERS (DAU) & SESSION ENGAGEMENT TREND
SELECT
    SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 10) AS activity_date,
    COUNT(DISTINCT user_id) AS dau,
    COUNT(DISTINCT session_id) AS daily_sessions,
    COUNT(*) AS total_events,
    SUM(CASE WHEN event_name = 'order_placed' THEN 1 ELSE 0 END) AS daily_orders
FROM events
GROUP BY SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 10)
ORDER BY activity_date ASC;

-- 3. WEEKLY (WAU) AND MONTHLY ACTIVE USERS (MAU) & STICKINESS RATIO
WITH mau_calc AS (
    SELECT
        SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 7) AS activity_month,
        COUNT(DISTINCT user_id) AS mau,
        COUNT(DISTINCT session_id) AS monthly_sessions
    FROM events
    GROUP BY SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 7)
),
daily_by_month AS (
    SELECT
        SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 7) AS activity_month,
        SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 10) AS activity_date,
        COUNT(DISTINCT user_id) AS dau
    FROM events
    GROUP BY
        SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 7),
        SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 10)
)
SELECT
    m.activity_month,
    m.mau,
    ROUND(AVG(d.dau), 1) AS avg_dau,
    ROUND(AVG(d.dau) * 4.2, 0) AS estimated_wau,
    ROUND(100.0 * AVG(d.dau) / NULLIF(m.mau, 0), 1) AS dau_to_mau_stickiness_pct
FROM mau_calc m
JOIN daily_by_month d ON m.activity_month = d.activity_month
GROUP BY m.activity_month, m.mau
ORDER BY m.activity_month ASC;

-- 4. CUSTOMER COHORT RETENTION MATRIX
SELECT
    u.cohort_month,
    SUBSTR(CAST(e.event_timestamp AS VARCHAR), 1, 7) AS activity_month,
    COUNT(DISTINCT e.user_id) AS retained_users,
    (SELECT COUNT(*) FROM users u2 WHERE u2.cohort_month = u.cohort_month) AS cohort_size,
    ROUND(
        100.0 * COUNT(DISTINCT e.user_id) /
        NULLIF((SELECT COUNT(*) FROM users u2 WHERE u2.cohort_month = u.cohort_month), 0),
        1
    ) AS retention_rate_pct
FROM users u
JOIN events e ON u.id = e.user_id
GROUP BY u.cohort_month, SUBSTR(CAST(e.event_timestamp AS VARCHAR), 1, 7)
ORDER BY u.cohort_month ASC, activity_month ASC;

-- 5. REPEAT PURCHASE & CUSTOMER LIFETIME VALUE (LTV) SEGMENTATION
WITH user_order_summary AS (
    SELECT
        u.id AS user_id,
        u.persona_segment,
        u.acquisition_channel,
        COUNT(o.id) AS total_orders,
        COALESCE(SUM(o.total_amount), 0) AS lifetime_spend
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id AND o.status != 'returned'
    GROUP BY u.id, u.persona_segment, u.acquisition_channel
)
SELECT
    persona_segment,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN total_orders >= 1 THEN 1 ELSE 0 END) AS purchasing_customers,
    SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(
        100.0 * SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN total_orders >= 1 THEN 1 ELSE 0 END), 0),
        1
    ) AS repeat_purchase_rate_pct,
    ROUND(AVG(CASE WHEN total_orders >= 1 THEN lifetime_spend END), 2) AS avg_customer_ltv
FROM user_order_summary
GROUP BY persona_segment
ORDER BY repeat_purchase_rate_pct DESC;

-- 6. PRODUCT CLICK-THROUGH RATE (CTR) & ADD-TO-CART EFFICIENCY
SELECT
    p.id AS product_id,
    p.sku,
    p.title,
    p.brand,
    c.name AS category_name,
    p.price,
    COUNT(DISTINCT CASE WHEN s.clicked_product_id = p.id THEN s.id END) AS search_clicks,
    COUNT(DISTINCT CASE WHEN e.event_name = 'product_viewed' THEN e.id END) AS pdp_views,
    COUNT(DISTINCT CASE WHEN e.event_name = 'add_to_cart' THEN e.id END) AS add_to_carts,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN e.event_name = 'add_to_cart' THEN e.id END) /
        NULLIF(COUNT(DISTINCT CASE WHEN e.event_name = 'product_viewed' THEN e.id END), 0),
        2
    ) AS pdp_to_cart_rate_pct
FROM products p
JOIN categories c ON p.category_id = c.id
LEFT JOIN events e ON e.product_id = p.id
LEFT JOIN searches s ON s.clicked_product_id = p.id
GROUP BY p.id, p.sku, p.title, p.brand, c.name, p.price
ORDER BY pdp_views DESC;

-- 7. SEARCH ABANDONMENT & ZERO-RESULT DIAGNOSTICS
SELECT
    normalized_query,
    COUNT(*) AS total_searches,
    ROUND(AVG(results_count), 1) AS avg_results_returned,
    SUM(CASE WHEN results_count = 0 THEN 1 ELSE 0 END) AS zero_result_count,
    SUM(CASE WHEN clicked_product_id IS NOT NULL THEN 1 ELSE 0 END) AS clicked_count,
    SUM(CASE WHEN search_abandoned = 1 OR search_abandoned = TRUE THEN 1 ELSE 0 END) AS abandoned_count,
    ROUND(100.0 * SUM(CASE WHEN clicked_product_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS search_ctr_pct,
    ROUND(100.0 * SUM(CASE WHEN search_abandoned = 1 OR search_abandoned = TRUE THEN 1 ELSE 0 END) / COUNT(*), 1) AS abandonment_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN converted_to_order = 1 OR converted_to_order = TRUE THEN 1 ELSE 0 END) / COUNT(*), 1) AS search_to_order_cvr_pct
FROM searches
GROUP BY normalized_query
HAVING COUNT(*) >= 2
ORDER BY abandonment_rate_pct DESC, total_searches DESC;

-- 8. CATEGORY-WISE REVENUE, AOV & RETURN EXPOSURE
SELECT
    c.name AS category_name,
    c.parent_department,
    COUNT(DISTINCT o.id) AS orders_containing_category,
    COALESCE(SUM(oi.quantity), 0) AS total_units_sold,
    ROUND(COALESCE(SUM(oi.quantity * oi.unit_price), 0), 2) AS gross_merchandise_value,
    ROUND(AVG(p.price), 2) AS avg_catalog_price,
    ROUND(AVG(p.return_rate_pct), 2) AS avg_category_return_rate_pct
FROM categories c
JOIN products p ON p.category_id = c.id
LEFT JOIN order_items oi ON oi.product_id = p.id
LEFT JOIN orders o ON oi.order_id = o.id
GROUP BY c.name, c.parent_department
ORDER BY gross_merchandise_value DESC;

-- 9. DEVICE-WISE PERFORMANCE & FUNNEL EFFICIENCY
SELECT
    s.device_type,
    COUNT(DISTINCT s.id) AS total_sessions,
    COUNT(DISTINCT s.user_id) AS unique_users,
    ROUND(AVG(s.duration_seconds), 0) AS avg_session_duration_sec,
    COUNT(DISTINCT CASE WHEN e.event_name = 'product_viewed' THEN s.id END) AS pdp_sessions,
    COUNT(DISTINCT CASE WHEN e.event_name = 'add_to_cart' THEN s.id END) AS cart_sessions,
    COUNT(DISTINCT o.id) AS completed_orders,
    ROUND(COALESCE(SUM(o.total_amount), 0), 2) AS total_revenue,
    ROUND(100.0 * COUNT(DISTINCT o.id) / NULLIF(COUNT(DISTINCT s.id), 0), 2) AS session_conversion_rate_pct
FROM sessions s
LEFT JOIN events e ON e.session_id = s.id
LEFT JOIN orders o ON o.session_id = s.id
GROUP BY s.device_type
ORDER BY total_sessions DESC;
