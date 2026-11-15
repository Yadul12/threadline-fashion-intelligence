from datetime import datetime
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    full_name = Column(String(150), nullable=False)
    persona_segment = Column(String(80), nullable=False)
    preferred_size = Column(String(16), nullable=False)
    acquisition_channel = Column(String(64), nullable=False)
    primary_device = Column(String(32), nullable=False)
    city_tier = Column(String(32), nullable=False)
    cohort_month = Column(String(7), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_users_cohort_month", "cohort_month"),
        Index("idx_users_acquisition_channel", "acquisition_channel"),
        Index("idx_users_persona_segment", "persona_segment"),
    )


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(64), primary_key=True)
    slug = Column(String(64), nullable=False, unique=True)
    name = Column(String(120), nullable=False)
    parent_department = Column(String(80), nullable=False)
    editorial_tagline = Column(String(255), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(String(64), primary_key=True)
    sku = Column(String(64), nullable=False, unique=True)
    title = Column(String(200), nullable=False)
    subtitle = Column(String(255), nullable=False)
    brand = Column(String(100), nullable=False)
    category_id = Column(String(64), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    subcategory = Column(String(80), nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=False)
    discount_pct = Column(Integer, nullable=False, default=0)
    fabric = Column(String(120), nullable=False)
    fit_profile = Column(String(80), nullable=False)
    fit_notes = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    care_instructions = Column(String(255), nullable=False)
    occasion = Column(String(80), nullable=False)
    available_sizes_json = Column(Text, nullable=False)
    available_colors_json = Column(Text, nullable=False)
    primary_color = Column(String(64), nullable=False)
    image_url = Column(Text, nullable=False)
    secondary_image_url = Column(Text, nullable=False)
    rating_avg = Column(Float, nullable=False, default=0.0)
    review_count = Column(Integer, nullable=False, default=0)
    popularity_score = Column(Integer, nullable=False, default=50)
    return_rate_pct = Column(Float, nullable=False, default=8.5)
    is_featured = Column(Boolean, nullable=False, default=False)
    is_new_arrival = Column(Boolean, nullable=False, default=False)
    stock_count = Column(Integer, nullable=False, default=25)
    search_tags = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    reviews = relationship("Review", back_populates="product")

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price_positive"),
        CheckConstraint("original_price >= price", name="ck_products_orig_price_gte_price"),
        CheckConstraint("discount_pct >= 0 AND discount_pct <= 90", name="ck_products_discount_range"),
        CheckConstraint("stock_count >= 0", name="ck_products_stock_nonnegative"),
        Index("idx_products_category_id", "category_id"),
        Index("idx_products_brand", "brand"),
        Index("idx_products_price", "price"),
        Index("idx_products_primary_color", "primary_color"),
    )


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_type = Column(String(32), nullable=False)
    acquisition_channel = Column(String(64), nullable=False)
    experiment_variant = Column(String(32), nullable=False, default="control")
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=False, default=0)
    converted = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("idx_sessions_user_id", "user_id"),
        Index("idx_sessions_started_at", "started_at"),
        Index("idx_sessions_device_type", "device_type"),
    )


class SearchRecord(Base):
    __tablename__ = "searches"

    id = Column(String(64), primary_key=True)
    session_id = Column(String(64), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    query_text = Column(String(255), nullable=False)
    normalized_query = Column(String(255), nullable=False)
    filters_json = Column(Text, nullable=False, default="{}")
    results_count = Column(Integer, nullable=False, default=0)
    clicked_product_id = Column(String(64), ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    click_position = Column(Integer, nullable=True)
    converted_to_bag = Column(Boolean, nullable=False, default=False)
    converted_to_order = Column(Boolean, nullable=False, default=False)
    search_abandoned = Column(Boolean, nullable=False, default=False)
    experiment_variant = Column(String(32), nullable=False, default="control")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_searches_normalized_query", "normalized_query"),
        Index("idx_searches_results_count", "results_count"),
        Index("idx_searches_created_at", "created_at"),
        Index("idx_searches_session_id", "session_id"),
    )


class EventRecord(Base):
    __tablename__ = "events"

    id = Column(String(64), primary_key=True)
    event_name = Column(String(64), nullable=False)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(64), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String(64), ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(80), nullable=True)
    price = Column(Float, nullable=True)
    brand = Column(String(100), nullable=True)
    device_type = Column(String(32), nullable=False)
    acquisition_channel = Column(String(64), nullable=False)
    experiment_variant = Column(String(32), nullable=True)
    properties_json = Column(Text, nullable=False, default="{}")
    mixpanel_dispatched = Column(Boolean, nullable=False, default=False)
    event_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_events_event_name", "event_name"),
        Index("idx_events_user_session", "user_id", "session_id"),
        Index("idx_events_timestamp", "event_timestamp"),
        Index("idx_events_product_id", "product_id"),
    )


class CartItem(Base):
    __tablename__ = "carts"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(64), nullable=False)
    product_id = Column(String(64), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    selected_size = Column(String(16), nullable=False)
    selected_color = Column(String(64), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    item_type = Column(String(24), nullable=False, default="bag")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    product = relationship("Product")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_carts_quantity_positive"),
        Index("idx_carts_user_type", "user_id", "item_type"),
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(64), primary_key=True)
    order_number = Column(String(32), nullable=False, unique=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(64), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(32), nullable=False, default="confirmed")
    subtotal = Column(Float, nullable=False)
    discount_amount = Column(Float, nullable=False, default=0.0)
    shipping_fee = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(64), nullable=False)
    shipping_city = Column(String(100), nullable=False)
    attribution_search_id = Column(String(64), ForeignKey("searches.id", ondelete="SET NULL"), nullable=True)
    experiment_variant = Column(String(32), nullable=False, default="control")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_orders_user_id", "user_id"),
        Index("idx_orders_created_at", "created_at"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(64), primary_key=True)
    order_id = Column(String(64), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String(64), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    selected_size = Column(String(16), nullable=False)
    selected_color = Column(String(64), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        Index("idx_order_items_order_id", "order_id"),
        Index("idx_order_items_product_id", "product_id"),
    )


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(64), primary_key=True)
    product_id = Column(String(64), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(String(64), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    rating = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    comment_text = Column(Text, nullable=False)
    sentiment = Column(String(24), nullable=False)
    complaint_category = Column(String(64), nullable=False)
    fit_feedback = Column(String(32), nullable=False)
    verified_purchase = Column(Boolean, nullable=False, default=True)
    helpful_votes = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    product = relationship("Product", back_populates="reviews")
    user = relationship("User")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),
        Index("idx_reviews_product_id", "product_id"),
        Index("idx_reviews_complaint_category", "complaint_category"),
        Index("idx_reviews_sentiment", "sentiment"),
        Index("idx_reviews_created_at", "created_at"),
    )


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String(64), primary_key=True)
    key = Column(String(80), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    problem_statement = Column(Text, nullable=False)
    hypothesis = Column(Text, nullable=False)
    primary_metric = Column(String(80), nullable=False)
    secondary_metrics_json = Column(Text, nullable=False)
    control_description = Column(Text, nullable=False)
    treatment_description = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="running")
    traffic_allocation_pct = Column(Integer, nullable=False, default=100)
    target_sample_size = Column(Integer, nullable=False, default=400)
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    owner = Column(String(100), nullable=False)

    assignments = relationship("ExperimentAssignment", back_populates="experiment", cascade="all, delete-orphan")


class ExperimentAssignment(Base):
    __tablename__ = "experiment_assignments"

    id = Column(String(64), primary_key=True)
    experiment_id = Column(String(64), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(64), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    variant = Column(String(32), nullable=False)
    exposed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    search_submitted = Column(Boolean, nullable=False, default=False)
    search_clicked = Column(Boolean, nullable=False, default=False)
    product_viewed = Column(Boolean, nullable=False, default=False)
    added_to_cart = Column(Boolean, nullable=False, default=False)
    order_completed = Column(Boolean, nullable=False, default=False)
    order_revenue = Column(Float, nullable=False, default=0.0)

    experiment = relationship("Experiment", back_populates="assignments")

    __table_args__ = (
        UniqueConstraint("experiment_id", "user_id", name="uq_experiment_user"),
        Index("idx_exp_assign_exp_variant", "experiment_id", "variant"),
    )


class RoadmapItem(Base):
    __tablename__ = "roadmap_items"

    id = Column(String(64), primary_key=True)
    jira_key = Column(String(24), nullable=False, unique=True)
    epic_name = Column(String(120), nullable=False)
    title = Column(String(200), nullable=False)
    problem_evidence = Column(Text, nullable=False)
    user_story = Column(Text, nullable=False)
    acceptance_criteria_json = Column(Text, nullable=False)
    reach_score = Column(Integer, nullable=False)
    impact_score = Column(Float, nullable=False)
    confidence_pct = Column(Integer, nullable=False)
    effort_person_weeks = Column(Float, nullable=False)
    rice_score = Column(Float, nullable=False)
    customer_impact = Column(String(32), nullable=False)
    business_impact = Column(String(120), nullable=False)
    status = Column(String(32), nullable=False)
    sprint = Column(String(40), nullable=False)
    owner = Column(String(80), nullable=False)
