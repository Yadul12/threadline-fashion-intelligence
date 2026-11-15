from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EventTrackRequest(BaseModel):
    event_name: str = Field(..., description="Canonical event name e.g. product_viewed")
    user_id: str = Field(default="usr_demo_001")
    session_id: str = Field(default="sess_live_001")
    product_id: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None
    device_type: str = Field(default="desktop_web")
    acquisition_channel: str = Field(default="direct")
    experiment_variant: Optional[str] = "control"
    properties: Dict[str, Any] = Field(default_factory=dict)


class CartItemCreateRequest(BaseModel):
    user_id: str = Field(default="usr_demo_001")
    session_id: str = Field(default="sess_live_001")
    product_id: str
    selected_size: str
    selected_color: str
    quantity: int = Field(default=1, ge=1)
    item_type: str = Field(default="bag")  # 'bag' or 'wishlist'
    experiment_variant: str = Field(default="control")


class CartQuantityUpdateRequest(BaseModel):
    quantity: int = Field(..., ge=1, le=20)


class CheckoutCreateRequest(BaseModel):
    user_id: str = Field(default="usr_demo_001")
    session_id: str = Field(default="sess_live_001")
    shipping_city: str = Field(default="Bengaluru, KA")
    payment_method: str = Field(default="UPI / Instant Bank Transfer")
    promo_code: Optional[str] = None
    experiment_variant: str = Field(default="control")
    attribution_search_id: Optional[str] = None


class ReviewCreateRequest(BaseModel):
    user_id: str = Field(default="usr_demo_001")
    session_id: str = Field(default="sess_live_001")
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=3, max_length=200)
    comment_text: str = Field(..., min_length=10)
    complaint_category: str = Field(default="Size and fit")
    fit_feedback: str = Field(default="True to Size")


class SearchClickRequest(BaseModel):
    search_id: str
    product_id: str
    click_position: int = Field(default=1, ge=1)
    user_id: str = Field(default="usr_demo_001")
    session_id: str = Field(default="sess_live_001")
    experiment_variant: str = Field(default="control")


class ExperimentCreateRequest(BaseModel):
    key: str = Field(..., min_length=3, max_length=80)
    name: str = Field(..., min_length=5, max_length=200)
    problem_statement: str
    hypothesis: str
    primary_metric: str = Field(default="add_to_cart_rate")
    secondary_metrics: List[str] = Field(default_factory=lambda: ["search_ctr", "purchase_conversion"])
    control_description: str
    treatment_description: str
    traffic_allocation_pct: int = Field(default=100, ge=10, le=100)
    target_sample_size: int = Field(default=400, ge=50)
    owner: str = Field(default="Product Discovery Squad")


class ExperimentAssignRequest(BaseModel):
    experiment_key: str
    user_id: str
    session_id: Optional[str] = None


class RoadmapItemCreateRequest(BaseModel):
    jira_key: str
    epic_name: str
    title: str
    problem_evidence: str
    user_story: str
    acceptance_criteria: List[str]
    reach_score: int = Field(..., ge=10)
    impact_score: float = Field(..., ge=0.25, le=3.0)
    confidence_pct: int = Field(..., ge=10, le=100)
    effort_person_weeks: float = Field(..., gt=0.1)
    customer_impact: str = Field(default="High")
    business_impact: str
    status: str = Field(default="Planned Q1")
    sprint: str = Field(default="Sprint 15")
    owner: str = Field(default="Discovery PM")


class RoadmapRiceUpdateRequest(BaseModel):
    reach_score: int = Field(..., ge=10)
    impact_score: float = Field(..., ge=0.25, le=3.0)
    confidence_pct: int = Field(..., ge=10, le=100)
    effort_person_weeks: float = Field(..., gt=0.1)
    status: Optional[str] = None


class GenAIAnalyzeRequest(BaseModel):
    category_filter: Optional[str] = None
    complaint_filter: Optional[str] = None
    custom_question: Optional[str] = None
