import json
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    CartItem,
    Category,
    ExperimentAssignment,
    Order,
    OrderItem,
    Product,
    Review,
    SearchRecord,
    User,
)
from app.schemas import (
    CartItemCreateRequest,
    CartQuantityUpdateRequest,
    CheckoutCreateRequest,
    EventTrackRequest,
    ReviewCreateRequest,
    SearchClickRequest,
)
from app.services.analytics_service import ensure_user_and_session, track_event
from app.services.search_service import (
    execute_product_search,
    get_autocomplete_suggestions,
    serialize_product,
)

router = APIRouter(prefix="/api/storefront", tags=["Customer Storefront"])


@router.get("/bootstrap")
def get_storefront_bootstrap(
    user_id: str = Query(default="usr_demo_001"),
    db: Session = Depends(get_db),
):
    """Return categories, featured products, new arrivals, personalized recommendations, and demo personas."""
    categories = db.query(Category).order_by(Category.display_order).all()
    products = db.query(Product).all()
    demo_users = (
        db.query(User)
        .filter(User.id.in_(["usr_demo_001", "usr_demo_002", "usr_demo_003", "usr_demo_004"]))
        .all()
    )
    active_user = db.query(User).filter(User.id == user_id).first() or (demo_users[0] if demo_users else None)

    featured = [serialize_product(p) for p in products if p.is_featured][:6]
    new_arrivals = [serialize_product(p) for p in products if p.is_new_arrival][:6]

    # Personalized recommendations based on user's preferred size and persona
    pref_size = active_user.preferred_size if active_user else "M"
    persona = active_user.persona_segment if active_user else "Fit-Conscious Minimalist"

    rec_candidates = []
    for p in products:
        sizes = json.loads(p.available_sizes_json)
        if pref_size in sizes:
            score = p.popularity_score
            if persona == "Fit-Conscious Minimalist" and p.fit_profile == "True to Size":
                score += 15
            elif persona == "Occasion Explorer" and "Evening" in p.occasion:
                score += 15
            elif persona == "Value Trend-Seeker" and p.discount_pct >= 15:
                score += 15
            elif persona == "Editorial Curator" and p.is_featured:
                score += 15
            rec_candidates.append((score, p))

    rec_candidates.sort(key=lambda x: x[0], reverse=True)
    recommendations = [serialize_product(item[1]) for item in rec_candidates[:4]]

    return {
        "categories": [
            {
                "id": c.id,
                "slug": c.slug,
                "name": c.name,
                "parent_department": c.parent_department,
                "editorial_tagline": c.editorial_tagline,
            }
            for c in categories
        ],
        "featured_products": featured,
        "new_arrivals": new_arrivals,
        "recommended_for_user": recommendations,
        "active_user": {
            "id": active_user.id,
            "full_name": active_user.full_name,
            "persona_segment": active_user.persona_segment,
            "preferred_size": active_user.preferred_size,
            "city_tier": active_user.city_tier,
        }
        if active_user
        else None,
        "demo_personas": [
            {
                "id": u.id,
                "full_name": u.full_name,
                "persona_segment": u.persona_segment,
                "preferred_size": u.preferred_size,
                "primary_device": u.primary_device,
                "acquisition_channel": u.acquisition_channel,
            }
            for u in demo_users
        ],
    }


@router.get("/autocomplete")
def search_autocomplete(
    q: str = Query(default=""),
    db: Session = Depends(get_db),
):
    return get_autocomplete_suggestions(db, q)


@router.get("/search")
def search_products(
    q: Optional[str] = Query(default=None),
    category_id: Optional[str] = Query(default=None),
    brand: Optional[str] = Query(default=None),
    min_price: Optional[float] = Query(default=None),
    max_price: Optional[float] = Query(default=None),
    size: Optional[str] = Query(default=None),
    color: Optional[str] = Query(default=None),
    fit_profile: Optional[str] = Query(default=None),
    sort_by: str = Query(default="relevance"),
    experiment_variant: str = Query(default="control"),
    user_id: str = Query(default="usr_demo_001"),
    session_id: str = Query(default="sess_live_001"),
    record_search: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    return execute_product_search(
        db=db,
        q=q,
        category_id=category_id,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        size=size,
        color=color,
        fit_profile=fit_profile,
        sort_by=sort_by,
        experiment_variant=experiment_variant,
        user_id=user_id,
        session_id=session_id,
        record_search=record_search,
    )


@router.post("/search/click")
def record_search_result_click(
    req: SearchClickRequest,
    db: Session = Depends(get_db),
):
    srch = db.query(SearchRecord).filter(SearchRecord.id == req.search_id).first()
    if srch:
        srch.clicked_product_id = req.product_id
        srch.click_position = req.click_position
        srch.search_abandoned = False
        db.commit()

    track_event(
        db,
        EventTrackRequest(
            event_name="search_result_clicked",
            user_id=req.user_id,
            session_id=req.session_id,
            product_id=req.product_id,
            experiment_variant=req.experiment_variant,
            properties={"search_id": req.search_id, "click_position": req.click_position},
        ),
    )
    return {"status": "recorded", "search_id": req.search_id, "product_id": req.product_id}


@router.get("/products/{product_id}")
def get_product_detail(
    product_id: str,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")

    reviews = (
        db.query(Review)
        .filter(Review.product_id == product.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    fit_breakdown = {"Runs Small": 0, "True to Size": 0, "Runs Large": 0}
    for r in reviews:
        fit_breakdown[r.fit_feedback] = fit_breakdown.get(r.fit_feedback, 0) + 1
    total_revs = max(1, len(reviews))

    # Related products (same category or complementary occasion)
    related_candidates = (
        db.query(Product)
        .filter(Product.id != product.id)
        .all()
    )
    related_scored = []
    for rp in related_candidates:
        s = 0
        if rp.category_id == product.category_id:
            s += 30
        if rp.occasion == product.occasion:
            s += 20
        if rp.subcategory != product.subcategory:
            s += 10
        related_scored.append((s + rp.popularity_score * 0.1, rp))
    related_scored.sort(key=lambda x: x[0], reverse=True)

    return {
        "product": serialize_product(product),
        "fit_consensus": {
            "runs_small_pct": round(100.0 * fit_breakdown.get("Runs Small", 0) / total_revs, 0),
            "true_to_size_pct": round(100.0 * fit_breakdown.get("True to Size", 0) / total_revs, 0),
            "runs_large_pct": round(100.0 * fit_breakdown.get("Runs Large", 0) / total_revs, 0),
            "total_verified_reviews": len(reviews),
        },
        "reviews": [
            {
                "id": r.id,
                "user_name": r.user.full_name if r.user else "Verified Buyer",
                "persona_segment": r.user.persona_segment if r.user else "",
                "rating": r.rating,
                "title": r.title,
                "comment_text": r.comment_text,
                "sentiment": r.sentiment,
                "complaint_category": r.complaint_category,
                "fit_feedback": r.fit_feedback,
                "verified_purchase": r.verified_purchase,
                "helpful_votes": r.helpful_votes,
                "created_at": r.created_at.strftime("%Y-%m-%d"),
            }
            for r in reviews
        ],
        "related_products": [serialize_product(item[1]) for item in related_scored[:4]],
    }


@router.post("/products/{product_id}/reviews")
def submit_product_review(
    product_id: str,
    req: ReviewCreateRequest,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    user, _ = ensure_user_and_session(db, user_id=req.user_id, session_id=req.session_id)
    sentiment = "positive" if req.rating >= 4 else ("negative" if req.rating <= 2 else "neutral")

    new_rev = Review(
        id=f"rev_live_{uuid.uuid4().hex[:7]}",
        product_id=product.id,
        user_id=user.id,
        order_id=None,
        rating=req.rating,
        title=req.title,
        comment_text=req.comment_text,
        sentiment=sentiment,
        complaint_category=req.complaint_category,
        fit_feedback=req.fit_feedback,
        verified_purchase=True,
        helpful_votes=0,
        created_at=datetime.utcnow(),
    )
    db.add(new_rev)
    db.flush()

    # Recompute product rating_avg & review_count
    all_revs = db.query(Review).filter(Review.product_id == product.id).all()
    product.review_count = len(all_revs)
    product.rating_avg = round(sum(r.rating for r in all_revs) / max(1, len(all_revs)), 2)
    db.commit()

    track_event(
        db,
        EventTrackRequest(
            event_name="product_reviewed",
            user_id=req.user_id,
            session_id=req.session_id,
            product_id=product.id,
            properties={
                "rating": req.rating,
                "complaint_category": req.complaint_category,
                "fit_feedback": req.fit_feedback,
            },
        ),
    )

    return {
        "status": "created",
        "review_id": new_rev.id,
        "updated_rating_avg": product.rating_avg,
        "updated_review_count": product.review_count,
    }


@router.get("/cart")
def get_user_cart_and_wishlist(
    user_id: str = Query(default="usr_demo_001"),
    db: Session = Depends(get_db),
):
    items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .order_by(CartItem.created_at.desc())
        .all()
    )

    bag_items = []
    wishlist_items = []
    subtotal = 0.0

    for it in items:
        if not it.product:
            continue
        p_data = serialize_product(it.product)
        line_total = round(it.product.price * it.quantity, 2)
        entry = {
            "id": it.id,
            "product_id": it.product_id,
            "selected_size": it.selected_size,
            "selected_color": it.selected_color,
            "quantity": it.quantity,
            "item_type": it.item_type,
            "line_total": line_total,
            "product": p_data,
        }
        if it.item_type == "wishlist":
            wishlist_items.append(entry)
        else:
            bag_items.append(entry)
            subtotal += line_total

    shipping_fee = 0.0 if (subtotal == 0 or subtotal >= 5000.0) else 250.0
    tier_discount = round(subtotal * 0.05, 2) if subtotal >= 8000.0 else 0.0
    total_amount = round(subtotal - tier_discount + shipping_fee, 2)

    return {
        "user_id": user_id,
        "bag_items": bag_items,
        "wishlist_items": wishlist_items,
        "summary": {
            "bag_count": sum(i["quantity"] for i in bag_items),
            "wishlist_count": len(wishlist_items),
            "subtotal": round(subtotal, 2),
            "tier_discount": tier_discount,
            "shipping_fee": shipping_fee,
            "free_shipping_threshold": 5000.0,
            "amount_for_free_shipping": max(0.0, round(5000.0 - subtotal, 2)),
            "total_amount": total_amount,
        },
    }


@router.post("/cart")
def add_item_to_cart_or_wishlist(
    req: CartItemCreateRequest,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == req.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    ensure_user_and_session(
        db,
        user_id=req.user_id,
        session_id=req.session_id,
        experiment_variant=req.experiment_variant,
    )

    existing = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == req.user_id,
            CartItem.product_id == req.product_id,
            CartItem.selected_size == req.selected_size,
            CartItem.selected_color == req.selected_color,
            CartItem.item_type == req.item_type,
        )
        .first()
    )
    if existing:
        existing.quantity += req.quantity
        db.commit()
        item_id = existing.id
    else:
        new_item = CartItem(
            id=f"crt_{uuid.uuid4().hex[:8]}",
            user_id=req.user_id,
            session_id=req.session_id,
            product_id=req.product_id,
            selected_size=req.selected_size,
            selected_color=req.selected_color,
            quantity=req.quantity,
            item_type=req.item_type,
            created_at=datetime.utcnow(),
        )
        db.add(new_item)
        db.commit()
        item_id = new_item.id

    ev_name = "wishlist_added" if req.item_type == "wishlist" else "add_to_cart"
    track_event(
        db,
        EventTrackRequest(
            event_name=ev_name,
            user_id=req.user_id,
            session_id=req.session_id,
            product_id=product.id,
            experiment_variant=req.experiment_variant,
            properties={
                "selected_size": req.selected_size,
                "selected_color": req.selected_color,
                "quantity": req.quantity,
            },
        ),
    )

    # Also update experiment assignment if user is in an experiment and added to bag
    if req.item_type == "bag":
        exp_assigns = (
            db.query(ExperimentAssignment)
            .filter(ExperimentAssignment.user_id == req.user_id)
            .all()
        )
        for ea in exp_assigns:
            ea.added_to_cart = True
        db.commit()

    return {"status": "added", "cart_item_id": item_id, "cart": get_user_cart_and_wishlist(req.user_id, db)}


@router.patch("/cart/{cart_item_id}")
def update_cart_item_quantity(
    cart_item_id: str,
    req: CartQuantityUpdateRequest,
    db: Session = Depends(get_db),
):
    item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    item.quantity = req.quantity
    db.commit()
    return get_user_cart_and_wishlist(item.user_id, db)


@router.post("/cart/{cart_item_id}/move-to-bag")
def move_wishlist_item_to_bag(
    cart_item_id: str,
    db: Session = Depends(get_db),
):
    item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    item.item_type = "bag"
    db.commit()

    track_event(
        db,
        EventTrackRequest(
            event_name="add_to_cart",
            user_id=item.user_id,
            session_id=item.session_id,
            product_id=item.product_id,
            properties={"source": "wishlist_move", "selected_size": item.selected_size},
        ),
    )
    return get_user_cart_and_wishlist(item.user_id, db)


@router.delete("/cart/{cart_item_id}")
def remove_cart_item(
    cart_item_id: str,
    db: Session = Depends(get_db),
):
    item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    uid = item.user_id
    db.delete(item)
    db.commit()
    return get_user_cart_and_wishlist(uid, db)


@router.post("/checkout")
def simulate_checkout_and_place_order(
    req: CheckoutCreateRequest,
    db: Session = Depends(get_db),
):
    user, sess = ensure_user_and_session(
        db,
        user_id=req.user_id,
        session_id=req.session_id,
        experiment_variant=req.experiment_variant,
    )

    bag_items = (
        db.query(CartItem)
        .filter(CartItem.user_id == req.user_id, CartItem.item_type == "bag")
        .all()
    )
    if not bag_items:
        raise HTTPException(status_code=400, detail="Shopping bag is empty")

    # Track checkout_started
    first_prod = bag_items[0].product
    track_event(
        db,
        EventTrackRequest(
            event_name="checkout_started",
            user_id=user.id,
            session_id=sess.id,
            product_id=first_prod.id if first_prod else None,
            experiment_variant=req.experiment_variant,
            properties={"items_count": len(bag_items), "shipping_city": req.shipping_city},
        ),
    )

    subtotal = sum((it.product.price * it.quantity) for it in bag_items if it.product)
    promo_discount = round(subtotal * 0.10, 2) if (req.promo_code and req.promo_code.strip().upper() == "ATELIER10") else (
        round(subtotal * 0.05, 2) if subtotal >= 8000.0 else 0.0
    )
    shipping_fee = 0.0 if subtotal >= 5000.0 else 250.0
    total_amount = round(subtotal - promo_discount + shipping_fee, 2)

    order_id = f"ord_live_{uuid.uuid4().hex[:7]}"
    order_number = f"TL-2026-{uuid.uuid4().hex[:5].upper()}"

    new_order = Order(
        id=order_id,
        order_number=order_number,
        user_id=user.id,
        session_id=sess.id,
        status="confirmed",
        subtotal=round(subtotal, 2),
        discount_amount=promo_discount,
        shipping_fee=shipping_fee,
        total_amount=total_amount,
        payment_method=req.payment_method,
        shipping_city=req.shipping_city,
        attribution_search_id=req.attribution_search_id,
        experiment_variant=req.experiment_variant,
        created_at=datetime.utcnow(),
    )
    db.add(new_order)
    db.flush()

    ordered_items_summary = []
    for it in bag_items:
        if not it.product:
            continue
        oi = OrderItem(
            id=f"oi_live_{uuid.uuid4().hex[:7]}",
            order_id=order_id,
            product_id=it.product_id,
            selected_size=it.selected_size,
            selected_color=it.selected_color,
            quantity=it.quantity,
            unit_price=it.product.price,
        )
        db.add(oi)
        ordered_items_summary.append(
            {
                "product_id": it.product_id,
                "title": it.product.title,
                "brand": it.product.brand,
                "selected_size": it.selected_size,
                "selected_color": it.selected_color,
                "quantity": it.quantity,
                "unit_price": it.product.price,
                "image_url": it.product.image_url,
            }
        )
        db.delete(it)

    sess.converted = True
    exp_assigns = (
        db.query(ExperimentAssignment)
        .filter(ExperimentAssignment.user_id == user.id)
        .all()
    )
    for ea in exp_assigns:
        ea.added_to_cart = True
        ea.order_completed = True
        ea.order_revenue = round(ea.order_revenue + total_amount, 2)

    db.commit()

    track_event(
        db,
        EventTrackRequest(
            event_name="order_placed",
            user_id=user.id,
            session_id=sess.id,
            product_id=first_prod.id if first_prod else None,
            price=total_amount,
            experiment_variant=req.experiment_variant,
            properties={
                "order_id": order_id,
                "order_number": order_number,
                "total_amount": total_amount,
                "items_count": len(ordered_items_summary),
            },
        ),
    )

    return {
        "status": "confirmed",
        "order": {
            "id": order_id,
            "order_number": order_number,
            "created_at": new_order.created_at.strftime("%Y-%m-%d %H:%M UTC"),
            "shipping_city": req.shipping_city,
            "payment_method": req.payment_method,
            "subtotal": round(subtotal, 2),
            "discount_amount": promo_discount,
            "shipping_fee": shipping_fee,
            "total_amount": total_amount,
            "items": ordered_items_summary,
        },
    }
