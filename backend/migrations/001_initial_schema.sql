-- =============================================================================
-- THREADLINE — Fashion Discovery & Customer Experience Intelligence Platform
-- Migration 001: Initial Relational Schema, Constraints & Indexes (PostgreSQL)
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    persona_segment VARCHAR(80) NOT NULL, -- 'Fit-Conscious Minimalist', 'Occasion Explorer', 'Value Trend-Seeker', 'Editorial Curator'
    preferred_size VARCHAR(16) NOT NULL,
    acquisition_channel VARCHAR(64) NOT NULL, -- 'organic_search', 'paid_social_ig', 'editorial_newsletter', 'direct', 'influencer_referral'
    primary_device VARCHAR(32) NOT NULL, -- 'mobile_ios', 'mobile_android', 'desktop_web'
    city_tier VARCHAR(32) NOT NULL, -- 'Metro Tier-1', 'Tier-2 Growth', 'Tier-3 Emerging'
    cohort_month VARCHAR(7) NOT NULL, -- YYYY-MM
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_cohort_month ON users(cohort_month);
CREATE INDEX IF NOT EXISTS idx_users_acquisition_channel ON users(acquisition_channel);
CREATE INDEX IF NOT EXISTS idx_users_persona_segment ON users(persona_segment);

CREATE TABLE IF NOT EXISTS categories (
    id VARCHAR(64) PRIMARY KEY,
    slug VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    parent_department VARCHAR(80) NOT NULL, -- 'Womenswear', 'Menswear', 'Accessories', 'Footwear'
    editorial_tagline VARCHAR(255) NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(64) PRIMARY KEY,
    sku VARCHAR(64) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    subtitle VARCHAR(255) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    category_id VARCHAR(64) NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    subcategory VARCHAR(80) NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    original_price NUMERIC(10, 2) NOT NULL CHECK (original_price >= price),
    discount_pct INTEGER NOT NULL DEFAULT 0 CHECK (discount_pct >= 0 AND discount_pct <= 90),
    fabric VARCHAR(120) NOT NULL, -- e.g. '100% European Flax Linen', 'Heavyweight Organic Cotton Twill'
    fit_profile VARCHAR(80) NOT NULL, -- 'Relaxed Tailored', 'True to Size', 'Runs Small - Size Up', 'Oversized Architectural'
    fit_notes TEXT NOT NULL,
    description TEXT NOT NULL,
    care_instructions VARCHAR(255) NOT NULL,
    occasion VARCHAR(80) NOT NULL, -- 'Work & Atelier', 'Weekend Resort', 'Evening Editorial', 'Elevated Everyday'
    available_sizes_json TEXT NOT NULL, -- JSON array e.g. ["XS", "S", "M", "L", "XL"]
    available_colors_json TEXT NOT NULL, -- JSON array of {name, hex}
    primary_color VARCHAR(64) NOT NULL,
    image_url TEXT NOT NULL,
    secondary_image_url TEXT NOT NULL,
    rating_avg NUMERIC(3, 2) NOT NULL DEFAULT 0.0,
    review_count INTEGER NOT NULL DEFAULT 0,
    popularity_score INTEGER NOT NULL DEFAULT 50,
    return_rate_pct NUMERIC(5, 2) NOT NULL DEFAULT 8.5,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    is_new_arrival BOOLEAN NOT NULL DEFAULT FALSE,
    stock_count INTEGER NOT NULL DEFAULT 25 CHECK (stock_count >= 0),
    search_tags TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_primary_color ON products(primary_color);

CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_type VARCHAR(32) NOT NULL,
    acquisition_channel VARCHAR(64) NOT NULL,
    experiment_variant VARCHAR(32) NOT NULL DEFAULT 'control',
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    duration_seconds INTEGER NOT NULL DEFAULT 0,
    converted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_sessions_device_type ON sessions(device_type);

CREATE TABLE IF NOT EXISTS searches (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query_text VARCHAR(255) NOT NULL,
    normalized_query VARCHAR(255) NOT NULL,
    filters_json TEXT NOT NULL DEFAULT '{}',
    results_count INTEGER NOT NULL DEFAULT 0,
    clicked_product_id VARCHAR(64) REFERENCES products(id) ON DELETE SET NULL,
    click_position INTEGER,
    converted_to_bag BOOLEAN NOT NULL DEFAULT FALSE,
    converted_to_order BOOLEAN NOT NULL DEFAULT FALSE,
    search_abandoned BOOLEAN NOT NULL DEFAULT FALSE,
    experiment_variant VARCHAR(32) NOT NULL DEFAULT 'control',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_searches_normalized_query ON searches(normalized_query);
CREATE INDEX IF NOT EXISTS idx_searches_results_count ON searches(results_count);
CREATE INDEX IF NOT EXISTS idx_searches_created_at ON searches(created_at);
CREATE INDEX IF NOT EXISTS idx_searches_session_id ON searches(session_id);

CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(64) PRIMARY KEY,
    event_name VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(64) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    product_id VARCHAR(64) REFERENCES products(id) ON DELETE SET NULL,
    category VARCHAR(80),
    price NUMERIC(10, 2),
    brand VARCHAR(100),
    device_type VARCHAR(32) NOT NULL,
    acquisition_channel VARCHAR(64) NOT NULL,
    experiment_variant VARCHAR(32),
    properties_json TEXT NOT NULL DEFAULT '{}',
    mixpanel_dispatched BOOLEAN NOT NULL DEFAULT FALSE,
    event_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_event_name ON events(event_name);
CREATE INDEX IF NOT EXISTS idx_events_user_session ON events(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_events_product_id ON events(product_id);

CREATE TABLE IF NOT EXISTS carts (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(64) NOT NULL,
    product_id VARCHAR(64) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    selected_size VARCHAR(16) NOT NULL,
    selected_color VARCHAR(64) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    item_type VARCHAR(24) NOT NULL DEFAULT 'bag', -- 'bag' or 'wishlist'
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_carts_user_type ON carts(user_id, item_type);

CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(64) PRIMARY KEY,
    order_number VARCHAR(32) NOT NULL UNIQUE,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(64) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    status VARCHAR(32) NOT NULL DEFAULT 'confirmed', -- 'confirmed', 'shipped', 'delivered', 'returned'
    subtotal NUMERIC(10, 2) NOT NULL,
    discount_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    shipping_fee NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(10, 2) NOT NULL,
    payment_method VARCHAR(64) NOT NULL,
    shipping_city VARCHAR(100) NOT NULL,
    attribution_search_id VARCHAR(64) REFERENCES searches(id) ON DELETE SET NULL,
    experiment_variant VARCHAR(32) NOT NULL DEFAULT 'control',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);

CREATE TABLE IF NOT EXISTS order_items (
    id VARCHAR(64) PRIMARY KEY,
    order_id VARCHAR(64) NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id VARCHAR(64) NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    selected_size VARCHAR(16) NOT NULL,
    selected_color VARCHAR(64) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);

CREATE TABLE IF NOT EXISTS reviews (
    id VARCHAR(64) PRIMARY KEY,
    product_id VARCHAR(64) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_id VARCHAR(64) REFERENCES orders(id) ON DELETE SET NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(200) NOT NULL,
    comment_text TEXT NOT NULL,
    sentiment VARCHAR(24) NOT NULL, -- 'positive', 'neutral', 'negative'
    complaint_category VARCHAR(64) NOT NULL, -- 'Size and fit', 'Search relevance', 'Product quality', 'Product images', 'Pricing', 'Delivery experience', 'Checkout experience', 'None (Praise)'
    fit_feedback VARCHAR(32) NOT NULL, -- 'Runs Small', 'True to Size', 'Runs Large'
    verified_purchase BOOLEAN NOT NULL DEFAULT TRUE,
    helpful_votes INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_complaint_category ON reviews(complaint_category);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment);
CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at);

CREATE TABLE IF NOT EXISTS experiments (
    id VARCHAR(64) PRIMARY KEY,
    key VARCHAR(80) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    problem_statement TEXT NOT NULL,
    hypothesis TEXT NOT NULL,
    primary_metric VARCHAR(80) NOT NULL,
    secondary_metrics_json TEXT NOT NULL,
    control_description TEXT NOT NULL,
    treatment_description TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'running', -- 'running', 'completed', 'draft'
    traffic_allocation_pct INTEGER NOT NULL DEFAULT 100,
    target_sample_size INTEGER NOT NULL DEFAULT 400,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    owner VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS experiment_assignments (
    id VARCHAR(64) PRIMARY KEY,
    experiment_id VARCHAR(64) NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(64) REFERENCES sessions(id) ON DELETE SET NULL,
    variant VARCHAR(32) NOT NULL, -- 'control', 'treatment'
    exposed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    search_submitted BOOLEAN NOT NULL DEFAULT FALSE,
    search_clicked BOOLEAN NOT NULL DEFAULT FALSE,
    product_viewed BOOLEAN NOT NULL DEFAULT FALSE,
    added_to_cart BOOLEAN NOT NULL DEFAULT FALSE,
    order_completed BOOLEAN NOT NULL DEFAULT FALSE,
    order_revenue NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    UNIQUE(experiment_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_exp_assign_exp_variant ON experiment_assignments(experiment_id, variant);

CREATE TABLE IF NOT EXISTS roadmap_items (
    id VARCHAR(64) PRIMARY KEY,
    jira_key VARCHAR(24) NOT NULL UNIQUE,
    epic_name VARCHAR(120) NOT NULL,
    title VARCHAR(200) NOT NULL,
    problem_evidence TEXT NOT NULL,
    user_story TEXT NOT NULL,
    acceptance_criteria_json TEXT NOT NULL,
    reach_score INTEGER NOT NULL,        -- Users impacted per quarter
    impact_score NUMERIC(3, 2) NOT NULL, -- 0.25, 0.5, 1.0, 2.0, 3.0
    confidence_pct INTEGER NOT NULL,     -- 50 to 100
    effort_person_weeks NUMERIC(4, 1) NOT NULL,
    rice_score NUMERIC(10, 2) NOT NULL,
    customer_impact VARCHAR(32) NOT NULL, -- 'Critical', 'High', 'Medium'
    business_impact VARCHAR(120) NOT NULL,
    status VARCHAR(32) NOT NULL,          -- 'In Progress', 'Next Sprint', 'Planned Q1', 'Shipped', 'Discovery'
    sprint VARCHAR(40) NOT NULL,
    owner VARCHAR(80) NOT NULL
);
