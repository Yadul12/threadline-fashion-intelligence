import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.main import app, init_db_and_seed
from app.models import ExperimentAssignment, Product, Review


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db_and_seed()
    yield


client = TestClient(app)


def test_health_and_integration_status():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "SYNTHETIC DATASET" in body["synthetic_data_notice"]
    assert "database_engine" in body["integrations"]
    assert body["integrations"]["tableau_views_ready"] is True


def test_database_constraints_enforced():
    """Verify relational constraints: negative price check & unique experiment assignment."""
    db = SessionLocal()
    try:
        # 1. Negative price check constraint should fail
        bad_prod = Product(
            id="prd_bad_price",
            sku="TL-BAD-999",
            title="Invalid Negative Price SKU",
            subtitle="Test",
            brand="Atelier Vance",
            category_id="cat_linen_edit",
            subcategory="Shirts",
            price=-500.0,
            original_price=1000.0,
            discount_pct=10,
            fabric="Linen",
            fit_profile="True to Size",
            fit_notes="Notes",
            description="Desc",
            care_instructions="Wash",
            occasion="Work",
            available_sizes_json='["S"]',
            available_colors_json='[{"name":"Black","hex":"#000"}]',
            primary_color="Black",
            image_url="https://example.com/img.jpg",
            secondary_image_url="https://example.com/img2.jpg",
            search_tags="test",
        )
        db.add(bad_prod)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        # 2. Invalid review rating (> 5) should fail check constraint
        bad_rev = Review(
            id="rev_bad_rating",
            product_id="prd_001",
            user_id="usr_demo_001",
            rating=9,
            title="Out of range rating",
            comment_text="Should fail check constraint",
            sentiment="positive",
            complaint_category="None (Praise)",
            fit_feedback="True to Size",
        )
        db.add(bad_rev)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        # 3. Duplicate (experiment_id, user_id) assignment should fail UniqueConstraint
        dup_assign = ExperimentAssignment(
            id="ea_dup_test",
            experiment_id="exp_001",
            user_id="usr_demo_001",
            variant="control",
        )
        db.add(dup_assign)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    finally:
        db.close()


def test_storefront_bootstrap_and_product_detail():
    resp = client.get("/api/storefront/bootstrap?user_id=usr_demo_001")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["categories"]) == 6
    assert len(data["featured_products"]) >= 4
    assert len(data["new_arrivals"]) >= 4
    assert len(data["recommended_for_user"]) >= 3
    assert data["active_user"]["id"] == "usr_demo_001"

    pdp = client.get("/api/storefront/products/prd_002")
    assert pdp.status_code == 200
    pdp_data = pdp.json()
    assert pdp_data["product"]["sku"] == "TL-LIN-002"
    assert "runs_small_pct" in pdp_data["fit_consensus"]
    assert len(pdp_data["reviews"]) >= 1
    assert len(pdp_data["related_products"]) == 4


def test_search_autocomplete_and_zero_result_vs_treatment_synonym():
    auto = client.get("/api/storefront/autocomplete?q=linen")
    assert auto.status_code == 200
    assert len(auto.json()["matching_products"]) >= 2

    # In Control variant, "haldi guest outfit" has 0 exact keyword matches and triggers zero-result recovery
    ctrl_search = client.get(
        "/api/storefront/search",
        params={"q": "haldi guest outfit", "experiment_variant": "control"},
    )
    assert ctrl_search.status_code == 200
    ctrl_body = ctrl_search.json()
    assert ctrl_body["total_results"] == 0
    assert ctrl_body["zero_result_recovery"] is not None
    assert len(ctrl_body["zero_result_recovery"]["fallback_products"]) == 4

    # In Treatment variant, semantic synonym expansion maps "haldi guest outfit" to occasion dresses!
    treat_search = client.get(
        "/api/storefront/search",
        params={"q": "haldi guest outfit", "experiment_variant": "treatment"},
    )
    assert treat_search.status_code == 200
    treat_body = treat_search.json()
    assert treat_body["synonym_expanded"] is True
    assert treat_body["total_results"] >= 3


def test_search_filters_and_sorting():
    resp = client.get(
        "/api/storefront/search",
        params={
            "category_id": "cat_linen_edit",
            "min_price": 3000,
            "max_price": 7500,
            "size": "S",
            "sort_by": "price_asc",
        },
    )
    assert resp.status_code == 200
    prods = resp.json()["products"]
    assert len(prods) >= 2
    prices = [p["price"] for p in prods]
    assert prices == sorted(prices)
    for p in prods:
        assert p["category_id"] == "cat_linen_edit"
        assert 3000 <= p["price"] <= 7500
        assert "S" in p["available_sizes"]


def test_cart_wishlist_and_checkout_journey():
    test_user = "usr_demo_002"
    # 1. Add item to wishlist
    w_resp = client.post(
        "/api/storefront/cart",
        json={
            "user_id": test_user,
            "session_id": "sess_test_checkout",
            "product_id": "prd_009",
            "selected_size": "L",
            "selected_color": "Tobacco Brown",
            "quantity": 1,
            "item_type": "wishlist",
        },
    )
    assert w_resp.status_code == 200
    w_id = w_resp.json()["cart_item_id"]

    # 2. Move wishlist item to shopping bag
    mv_resp = client.post(f"/api/storefront/cart/{w_id}/move-to-bag")
    assert mv_resp.status_code == 200
    assert mv_resp.json()["summary"]["bag_count"] >= 1

    # 3. Update quantity to 2
    up_resp = client.patch(f"/api/storefront/cart/{w_id}", json={"quantity": 2})
    assert up_resp.status_code == 200
    assert up_resp.json()["summary"]["bag_count"] >= 2

    # 4. Complete checkout simulation
    chk_resp = client.post(
        "/api/storefront/checkout",
        json={
            "user_id": test_user,
            "session_id": "sess_test_checkout",
            "shipping_city": "Mumbai, MH",
            "payment_method": "UPI / Instant Bank Transfer",
            "promo_code": "ATELIER10",
            "experiment_variant": "treatment",
        },
    )
    assert chk_resp.status_code == 200
    ord_data = chk_resp.json()["order"]
    assert ord_data["order_number"].startswith("TL-2026-")
    assert ord_data["discount_amount"] > 0
    assert len(ord_data["items"]) >= 1


def test_event_tracking_and_funnel_calculations():
    ev_resp = client.post(
        "/api/events/track",
        json={
            "event_name": "product_viewed",
            "user_id": "usr_demo_001",
            "session_id": "sess_0001",
            "product_id": "prd_001",
            "device_type": "desktop_web",
            "acquisition_channel": "editorial_newsletter",
            "experiment_variant": "treatment",
            "properties": {"source": "pytest_verification"},
        },
    )
    assert ev_resp.status_code == 200
    ev_body = ev_resp.json()
    assert ev_body["status"] == "recorded"
    assert ev_body["mixpanel_dispatched"] is False  # Honest reporting when MIXPANEL_TOKEN is unset

    funnel_resp = client.get("/api/analytics/funnel")
    assert funnel_resp.status_code == 200
    steps = funnel_resp.json()["steps"]
    assert len(steps) == 8
    step_map = {s["event_name"]: s["sessions"] for s in steps}
    assert step_map["homepage_viewed"] >= step_map["product_viewed"] >= step_map["add_to_cart"] >= step_map["order_placed"]


def test_experiments_deterministic_assignment_and_statistics():
    # Deterministic assignment check: calling twice for the same user returns identical variant
    a1 = client.post(
        "/api/experiments/assign",
        json={"experiment_key": "exp_semantic_size_fit_filters", "user_id": "usr_demo_003"},
    ).json()
    a2 = client.post(
        "/api/experiments/assign",
        json={"experiment_key": "exp_semantic_size_fit_filters", "user_id": "usr_demo_003"},
    ).json()
    assert a1["variant"] == a2["variant"]

    exps_resp = client.get("/api/experiments")
    assert exps_resp.status_code == 200
    exps = exps_resp.json()["experiments"]
    assert len(exps) >= 3

    by_key = {e["key"]: e for e in exps}
    # exp_semantic_size_fit_filters is adequately powered & statistically significant
    exp1 = by_key["exp_semantic_size_fit_filters"]
    assert exp1["is_adequately_powered"] is True
    assert exp1["primary_metric_summary"]["statistically_significant"] is True
    assert "Statistically Supported" in exp1["decision_classification"]

    # exp_editorial_lookbook_bundle is under-powered and flagged as Exploratory
    exp3 = by_key["exp_editorial_lookbook_bundle"]
    assert exp3["is_adequately_powered"] is False
    assert "Exploratory" in exp3["decision_classification"]


def test_genai_feedback_intelligence_and_sql_queries():
    fb_resp = client.get("/api/feedback")
    assert fb_resp.status_code == 200
    fb_data = fb_resp.json()
    assert fb_data["summary"]["total_reviews"] >= 96
    pain_points = fb_data["genai_intelligence"]["recurring_pain_points"]
    assert len(pain_points) >= 3
    for pp in pain_points:
        assert len(pp["supporting_records"]) >= 1
        assert pp["supporting_records"][0]["review_id"].startswith("rev_")

    # Verify all 9 named SQL analytical queries execute cleanly
    for q_key in [
        "conversion_funnel",
        "daily_active_users",
        "wau_mau_stickiness",
        "customer_cohorts",
        "repeat_purchases",
        "product_ctr",
        "search_abandonment",
        "category_revenue",
        "device_performance",
    ]:
        sq = client.get(f"/api/analytics/sql-queries?query_key={q_key}")
        assert sq.status_code == 200
        assert sq.json()["active_query"]["row_count"] >= 1


def test_data_exports_and_research_import():
    for ds in ["kpi_report", "customer_feedback", "search_analysis", "experiment_template", "jira_backlog", "tableau_extract"]:
        xlsx_resp = client.get(f"/api/exports/download?dataset={ds}&format=xlsx")
        assert xlsx_resp.status_code == 200
        assert len(xlsx_resp.content) > 1000

        csv_resp = client.get(f"/api/exports/download?dataset={ds}&format=csv")
        assert csv_resp.status_code == 200
        assert len(csv_resp.content) > 100

    # Test importing a CSV research file
    sample_csv = (
        "sku,rating,title,comment_text,complaint_category,fit_feedback\n"
        "TL-LIN-002,2,Waistband tight in user interview,Participant noted Size S waist measured 65cm with no give.,Size and fit,Runs Small\n"
    ).encode("utf-8")
    imp_resp = client.post(
        "/api/exports/import-feedback",
        files={"file": ("user_research_batch.csv", io.BytesIO(sample_csv), "text/csv")},
    )
    assert imp_resp.status_code == 200
    assert imp_resp.json()["rows_imported"] == 1
