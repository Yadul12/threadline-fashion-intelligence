import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models import Category, Product, SearchRecord
from app.services.analytics_service import SYNONYM_MAP, ensure_user_and_session


def serialize_product(p: Product) -> Dict[str, Any]:
    return {
        "id": p.id,
        "sku": p.sku,
        "title": p.title,
        "subtitle": p.subtitle,
        "brand": p.brand,
        "category_id": p.category_id,
        "category_name": p.category.name if p.category else "",
        "department": p.category.parent_department if p.category else "",
        "subcategory": p.subcategory,
        "price": p.price,
        "original_price": p.original_price,
        "discount_pct": p.discount_pct,
        "fabric": p.fabric,
        "fit_profile": p.fit_profile,
        "fit_notes": p.fit_notes,
        "description": p.description,
        "care_instructions": p.care_instructions,
        "occasion": p.occasion,
        "available_sizes": json.loads(p.available_sizes_json),
        "available_colors": json.loads(p.available_colors_json),
        "primary_color": p.primary_color,
        "image_url": p.image_url,
        "secondary_image_url": p.secondary_image_url,
        "rating_avg": p.rating_avg,
        "review_count": p.review_count,
        "popularity_score": p.popularity_score,
        "return_rate_pct": p.return_rate_pct,
        "is_featured": p.is_featured,
        "is_new_arrival": p.is_new_arrival,
        "stock_count": p.stock_count,
    }


def get_autocomplete_suggestions(db: Session, prefix: str) -> Dict[str, Any]:
    q = (prefix or "").strip().lower()
    products = db.query(Product).all()
    categories = db.query(Category).order_by(Category.display_order).all()

    popular_searches = [
        "linen blazer",
        "wide leg trouser",
        "occasion dress",
        "silk midi dress",
        "merino cardigan",
        "selvedge denim",
        "leather loafers",
        "breathable summer office wear",
        "haldi guest outfit",
    ]

    if not q:
        return {
            "query": "",
            "suggested_queries": popular_searches[:6],
            "matching_categories": [{"id": c.id, "name": c.name, "slug": c.slug} for c in categories[:4]],
            "matching_products": [serialize_product(p) for p in products[:4]],
        }

    matched_queries = [s for s in popular_searches if q in s.lower()]
    for syn_k in SYNONYM_MAP:
        if q in syn_k and syn_k not in matched_queries:
            matched_queries.append(syn_k)

    matched_cats = [
        {"id": c.id, "name": c.name, "slug": c.slug}
        for c in categories
        if q in c.name.lower() or q in c.parent_department.lower()
    ]

    matched_prods = []
    for p in products:
        searchable = f"{p.title} {p.subtitle} {p.brand} {p.subcategory} {p.fabric} {p.search_tags}".lower()
        if q in searchable:
            matched_prods.append(serialize_product(p))

    return {
        "query": prefix,
        "suggested_queries": matched_queries[:6],
        "matching_categories": matched_cats[:4],
        "matching_products": matched_prods[:5],
    }


def execute_product_search(
    db: Session,
    q: Optional[str] = None,
    category_id: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    size: Optional[str] = None,
    color: Optional[str] = None,
    fit_profile: Optional[str] = None,
    sort_by: str = "relevance",
    experiment_variant: str = "control",
    user_id: str = "usr_demo_001",
    session_id: str = "sess_live_001",
    record_search: bool = True,
) -> Dict[str, Any]:
    all_products = db.query(Product).all()
    raw_query = (q or "").strip()
    norm_query = raw_query.lower()

    synonym_tokens: List[str] = []
    synonym_expanded = False
    if norm_query and experiment_variant == "treatment":
        for phrase, mapped_tokens in SYNONYM_MAP.items():
            if norm_query in phrase or phrase in norm_query:
                synonym_tokens.extend([t.lower() for t in mapped_tokens])
                synonym_expanded = True

    scored_results: List[tuple[float, Product]] = []
    for p in all_products:
        # Apply structured facet filters first
        if category_id and category_id != "all" and p.category_id != category_id:
            continue
        if brand and brand != "all" and p.brand.lower() != brand.lower():
            continue
        if min_price is not None and p.price < min_price:
            continue
        if max_price is not None and p.price > max_price:
            continue
        if size and size != "all":
            sizes_list = json.loads(p.available_sizes_json)
            if size not in sizes_list:
                continue
        if color and color != "all":
            colors_list = [c["name"].lower() for c in json.loads(p.available_colors_json)]
            if color.lower() not in " ".join(colors_list) and color.lower() not in p.primary_color.lower():
                continue
        if fit_profile and fit_profile != "all":
            if fit_profile.lower() not in p.fit_profile.lower():
                continue

        # Score relevance against query
        if not norm_query:
            score = float(p.popularity_score)
            scored_results.append((score, p))
            continue

        haystack_title = f"{p.title} {p.subtitle} {p.brand} {p.subcategory}".lower()
        haystack_full = f"{haystack_title} {p.fabric} {p.occasion} {p.search_tags} {p.primary_color}".lower()

        query_words = [w for w in norm_query.split() if len(w) >= 2]
        score = 0.0

        if norm_query in haystack_title:
            score += 100.0
        elif norm_query in haystack_full:
            score += 75.0

        matched_words = sum(1 for w in query_words if w in haystack_full)
        if query_words and matched_words == len(query_words):
            score += 60.0
        elif matched_words > 0 and len(query_words) <= 2:
            score += 25.0 * matched_words

        # In Treatment variant, semantic synonym expansion matches occasion/fabric tokens
        if score == 0.0 and synonym_expanded and synonym_tokens:
            syn_hits = sum(1 for t in synonym_tokens if t in haystack_full)
            if syn_hits >= 1:
                score += 40.0 + (syn_hits * 10.0)

        # In Treatment variant, boost True to Size or high-rated items slightly for relevance quality
        if score > 0 and experiment_variant == "treatment":
            score += (p.rating_avg * 3.0)

        if score > 0:
            scored_results.append((score, p))

    # Sorting
    if sort_by == "price_asc":
        scored_results.sort(key=lambda item: item[1].price)
    elif sort_by == "price_desc":
        scored_results.sort(key=lambda item: item[1].price, reverse=True)
    elif sort_by == "popularity":
        scored_results.sort(key=lambda item: item[1].popularity_score, reverse=True)
    elif sort_by == "rating":
        scored_results.sort(key=lambda item: item[1].rating_avg, reverse=True)
    else:
        scored_results.sort(key=lambda item: (item[0], item[1].popularity_score), reverse=True)

    final_products = [serialize_product(item[1]) for item in scored_results]

    # Log search record if requested and query or filter is present
    search_id = None
    if record_search and (raw_query or category_id or size or brand or fit_profile):
        ensure_user_and_session(db, user_id=user_id, session_id=session_id, experiment_variant=experiment_variant)
        search_id = f"srch_live_{uuid.uuid4().hex[:8]}"
        srch = SearchRecord(
            id=search_id,
            session_id=session_id,
            user_id=user_id,
            query_text=raw_query or f"[filter:{category_id or size or brand or fit_profile}]",
            normalized_query=norm_query or "filtered_browse",
            filters_json=json.dumps(
                {
                    "category_id": category_id,
                    "brand": brand,
                    "size": size,
                    "color": color,
                    "fit_profile": fit_profile,
                    "min_price": min_price,
                    "max_price": max_price,
                }
            ),
            results_count=len(final_products),
            clicked_product_id=None,
            click_position=None,
            converted_to_bag=False,
            converted_to_order=False,
            search_abandoned=(len(final_products) == 0),
            experiment_variant=experiment_variant,
            created_at=datetime.utcnow(),
        )
        db.add(srch)
        db.commit()

    # Zero-result recovery recommendations
    zero_result_recovery = None
    if len(final_products) == 0:
        fallback_prods = sorted(all_products, key=lambda x: x.popularity_score, reverse=True)[:4]
        zero_result_recovery = {
            "message": f"No exact catalog matches for \"{raw_query}\" with current filters.",
            "tip": (
                "Switch to the Treatment A/B Variant ('Semantic Search + Fit Bar') to test automatic "
                "occasion & fabric synonym expansion, or explore our curated bestseller edit below."
            ),
            "suggested_queries": ["linen blazer", "occasion dress", "wide leg trouser", "merino cardigan", "leather loafers"],
            "fallback_products": [serialize_product(fp) for fp in fallback_prods],
        }

    # Available filter facets from catalog
    brands = sorted({p.brand for p in all_products})
    fit_profiles = sorted({p.fit_profile for p in all_products})
    colors = sorted({p.primary_color for p in all_products})

    return {
        "search_id": search_id,
        "query": raw_query,
        "experiment_variant": experiment_variant,
        "synonym_expanded": synonym_expanded,
        "expanded_tokens": synonym_tokens[:6] if synonym_expanded else [],
        "total_results": len(final_products),
        "products": final_products,
        "zero_result_recovery": zero_result_recovery,
        "available_facets": {
            "brands": brands,
            "fit_profiles": fit_profiles,
            "colors": colors,
            "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        },
    }
