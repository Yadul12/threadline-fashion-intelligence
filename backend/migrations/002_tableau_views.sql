-- =============================================================================
-- THREADLINE — Fashion Discovery & Customer Experience Intelligence Platform
-- Migration 002: Tableau-Ready Analytical Views
-- =============================================================================

-- 1. Daily Funnel & Engagement View for Tableau
CREATE VIEW IF NOT EXISTS vw_tableau_daily_funnel AS
SELECT
    SUBSTR( CAST(event_timestamp AS VARCHAR), 1, 10 ) AS activity_date,
    device_type,
    acquisition_channel,
    COALESCE(experiment_variant, 'control') AS experiment_variant,
    COUNT(DISTINCT user_id) AS active_users,
    COUNT(DISTINCT session_id) AS total_sessions,
    COUNT(DISTINCT CASE WHEN event_name = 'homepage_viewed' THEN session_id END) AS homepage_sessions,
    COUNT(DISTINCT CASE WHEN event_name = 'search_submitted' THEN session_id END) AS search_sessions,
    COUNT(DISTINCT CASE WHEN event_name = 'search_result_clicked' THEN session_id END) AS search_clicked_sessions,
    COUNT(DISTINCT CASE WHEN event_name = 'product_viewed' THEN session_id END) AS pdp_viewed_sessions,
    COUNT(DISTINCT CASE WHEN event_name = 'wishlist_added' THEN session_id END) AS wishlist_sessions,
    COUNT(DISTINCT CASE WHEN event_name = 'add_to_cart' THEN session_id END) AS cart_sessions,
    COUNT(DISTINCT CASE WHEN event_name = 'checkout_started' THEN session_id END) AS checkout_sessions,
    COUNT(DISTINCT CASE WHEN event_name = 'order_placed' THEN session_id END) AS converted_sessions
FROM events
GROUP BY
    SUBSTR( CAST(event_timestamp AS VARCHAR), 1, 10 ),
    device_type,
    acquisition_channel,
    COALESCE(experiment_variant, 'control');

-- 2. Search Discovery & Relevance View for Tableau
CREATE VIEW IF NOT EXISTS vw_tableau_search_intelligence AS
SELECT
    normalized_query,
    experiment_variant,
    COUNT(*) AS search_volume,
    ROUND(AVG(results_count), 1) AS avg_results_count,
    SUM(CASE WHEN results_count = 0 THEN 1 ELSE 0 END) AS zero_result_searches,
    SUM(CASE WHEN clicked_product_id IS NOT NULL THEN 1 ELSE 0 END) AS clicked_searches,
    SUM(CASE WHEN search_abandoned = 1 OR search_abandoned = TRUE THEN 1 ELSE 0 END) AS abandoned_searches,
    SUM(CASE WHEN converted_to_bag = 1 OR converted_to_bag = TRUE THEN 1 ELSE 0 END) AS bag_conversions,
    SUM(CASE WHEN converted_to_order = 1 OR converted_to_order = TRUE THEN 1 ELSE 0 END) AS order_conversions,
    ROUND(100.0 * SUM(CASE WHEN clicked_product_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS search_ctr_pct,
    ROUND(100.0 * SUM(CASE WHEN converted_to_order = 1 OR converted_to_order = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS search_cvr_pct
FROM searches
GROUP BY normalized_query, experiment_variant;

-- 3. Category & Product Merchandising Performance View for Tableau
CREATE VIEW IF NOT EXISTS vw_tableau_category_merchandising AS
SELECT
    c.name AS category_name,
    c.parent_department,
    p.id AS product_id,
    p.sku,
    p.title AS product_title,
    p.brand,
    p.fabric,
    p.fit_profile,
    p.price,
    p.rating_avg,
    p.return_rate_pct,
    COUNT(DISTINCT CASE WHEN e.event_name = 'product_viewed' THEN e.id END) AS pdp_views,
    COUNT(DISTINCT CASE WHEN e.event_name = 'add_to_cart' THEN e.id END) AS add_to_carts,
    COALESCE(SUM(oi.quantity), 0) AS units_sold,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS gross_revenue
FROM products p
JOIN categories c ON p.category_id = c.id
LEFT JOIN events e ON e.product_id = p.id
LEFT JOIN order_items oi ON oi.product_id = p.id
GROUP BY
    c.name, c.parent_department, p.id, p.sku, p.title, p.brand,
    p.fabric, p.fit_profile, p.price, p.rating_avg, p.return_rate_pct;

-- 4. Customer Feedback & Complaint Intelligence View for Tableau
CREATE VIEW IF NOT EXISTS vw_tableau_feedback_intelligence AS
SELECT
    r.id AS review_id,
    SUBSTR( CAST(r.created_at AS VARCHAR), 1, 10 ) AS review_date,
    r.rating,
    r.sentiment,
    r.complaint_category,
    r.fit_feedback,
    r.verified_purchase,
    p.id AS product_id,
    p.title AS product_title,
    p.brand,
    p.fit_profile,
    c.name AS category_name,
    u.persona_segment,
    u.city_tier
FROM reviews r
JOIN products p ON r.product_id = p.id
JOIN categories c ON p.category_id = c.id
JOIN users u ON r.user_id = u.id;
