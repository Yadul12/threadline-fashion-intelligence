import json
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import (
    Category,
    Product,
    User,
    SessionModel,
    SearchRecord,
    EventRecord,
    CartItem,
    Order,
    OrderItem,
    Review,
    Experiment,
    ExperimentAssignment,
    RoadmapItem,
)

SYNTHETIC_DATASET_NOTICE = (
    "SYNTHETIC DATASET: All customer profiles, browsing sessions, search logs, orders, "
    "reviews, and experiment exposures in THREADLINE are synthetically generated for "
    "product management portfolio demonstration."
)


CATEGORIES_DATA = [
    {
        "id": "cat_linen_edit",
        "slug": "linen-tailoring",
        "name": "Linen & Breathable Tailoring",
        "parent_department": "Womenswear",
        "editorial_tagline": "European flax and airy suiting engineered for warm-weather architecture.",
        "display_order": 1,
    },
    {
        "id": "cat_occasion_dresses",
        "slug": "contemporary-occasion",
        "name": "Contemporary Occasion & Evening",
        "parent_department": "Womenswear",
        "editorial_tagline": "Fluid drapery, bias-cut silhouettes, and understated evening statement pieces.",
        "display_order": 2,
    },
    {
        "id": "cat_mens_atelier",
        "slug": "mens-relaxed-sartorial",
        "name": "Menswear Relaxed Sartorial",
        "parent_department": "Menswear",
        "editorial_tagline": "Unstructured blazers, camp-collar shirts, and pleated trousers with ease.",
        "display_order": 3,
    },
    {
        "id": "cat_knitwear_separates",
        "slug": "architectural-knitwear",
        "name": "Architectural Knitwear & Separates",
        "parent_department": "Womenswear",
        "editorial_tagline": "Fine-gauge merino, ribbed columns, and trans-seasonal layering staples.",
        "display_order": 4,
    },
    {
        "id": "cat_denim_utility",
        "slug": "selvedge-denim-utility",
        "name": "Raw & Selvedge Denim Utility",
        "parent_department": "Menswear",
        "editorial_tagline": "Japanese 13oz selvedge denim, chore jackets, and garment-dyed cotton twill.",
        "display_order": 5,
    },
    {
        "id": "cat_leather_goods",
        "slug": "artisanal-leather-footwear",
        "name": "Artisanal Leather Footwear & Bags",
        "parent_department": "Footwear & Accessories",
        "editorial_tagline": "Vegetable-tanned calfskin loafers, sculptural totes, and Goodyear-welted boots.",
        "display_order": 6,
    },
]


PRODUCTS_DATA = [
    {
        "id": "prd_001",
        "sku": "TL-LIN-001",
        "title": "Valence Belted European Linen Blazer",
        "subtitle": "Single-breasted unlined jacket in 100% Normandy flax",
        "brand": "Atelier Vance",
        "category_id": "cat_linen_edit",
        "subcategory": "Blazers",
        "price": 6890.0,
        "original_price": 8490.0,
        "discount_pct": 19,
        "fabric": "100% European Flax Linen (185 GSM)",
        "fit_profile": "Relaxed Tailored",
        "fit_notes": "Cut for a slightly dropped shoulder. Take your normal size for an editorial drape, or size down for a closer shoulder line.",
        "description": "Tailored from breathable Normandy flax linen, the Valence Blazer balances sharp notched lapels with an unlined interior bound in cotton chambray. Features horn buttons and a removable self-tie waist belt.",
        "care_instructions": "Dry clean recommended or cold gentle machine wash; steam while damp.",
        "occasion": "Work & Atelier",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": [{"name": "Oatmeal Melange", "hex": "#DDD5C7"}, {"name": "Espresso", "hex": "#3B2F2F"}, {"name": "Terracotta Clay", "hex": "#9E3B33"}],
        "primary_color": "Oatmeal Melange",
        "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1548624313-0396c75e4b1a?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 96,
        "return_rate_pct": 6.4,
        "is_featured": True,
        "is_new_arrival": False,
        "stock_count": 38,
        "search_tags": "linen blazer jacket women workwear summer officewear beige oatmeal tailored coat",
    },
    {
        "id": "prd_002",
        "sku": "TL-LIN-002",
        "title": "Solstice High-Waist Pleated Linen Trouser",
        "subtitle": "Wide-leg tailored trouser with double front knife pleats",
        "brand": "Atelier Vance",
        "category_id": "cat_linen_edit",
        "subcategory": "Trousers",
        "price": 4490.0,
        "original_price": 5290.0,
        "discount_pct": 15,
        "fabric": "100% European Flax Linen",
        "fit_profile": "Runs Small - Size Up",
        "fit_notes": "Structured non-stretch waistband runs 1.5 cm narrower than standard sizing. 68% of verified buyers recommend sizing up one size.",
        "description": "Engineered with a high-rise waist and sweeping wide leg, the Solstice Trouser offers full-length movement and breathable comfort. Lined to the knee in lightweight cupro to prevent sheer transparency.",
        "care_instructions": "Cold delicate wash, line dry in shade.",
        "occasion": "Work & Atelier",
        "sizes": ["XS", "S", "M", "L"],
        "colors": [{"name": "Warm Ivory", "hex": "#F4EFE6"}, {"name": "Charcoal Slate", "hex": "#2F3134"}, {"name": "Olive Moss", "hex": "#555D42"}],
        "primary_color": "Warm Ivory",
        "image_url": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 94,
        "return_rate_pct": 18.2,
        "is_featured": True,
        "is_new_arrival": True,
        "stock_count": 29,
        "search_tags": "wide leg trouser linen pants women high waist ivory white formal pants office wear",
    },
    {
        "id": "prd_003",
        "sku": "TL-LIN-003",
        "title": "Aerin Poplin & Linen Popover Shirt",
        "subtitle": "Mandarin collar relaxed tunic shirt with mother-of-pearl placket",
        "brand": "Kora & Loom",
        "category_id": "cat_linen_edit",
        "subcategory": "Shirts",
        "price": 3290.0,
        "original_price": 3290.0,
        "discount_pct": 0,
        "fabric": "65% Belgian Linen, 35% Long-Staple Organic Cotton",
        "fit_profile": "True to Size",
        "fit_notes": "True to standard measurements with relaxed chest ease and curved gusseted hem.",
        "description": "Woven in small batches, the Aerin Popover blends the crispness of cotton poplin with the slub texture of Belgian linen. Designed for effortless tucking or wearing loose over tailored shorts.",
        "care_instructions": "Machine wash cold at 30C, warm iron.",
        "occasion": "Elevated Everyday",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": [{"name": "Ecru Sand", "hex": "#E6DEC8"}, {"name": "Burgundy Wine", "hex": "#7C2D26"}, {"name": "Powder Sky", "hex": "#C7D6E2"}],
        "primary_color": "Ecru Sand",
        "image_url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1603252109303-2751441dd157?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 91,
        "return_rate_pct": 5.1,
        "is_featured": False,
        "is_new_arrival": True,
        "stock_count": 52,
        "search_tags": "linen shirt women cotton tunic mandarin collar summer top breathable officewear",
    },
    {
        "id": "prd_004",
        "sku": "TL-LIN-004",
        "title": "Cannes Asymmetric Linen Waistcoat",
        "subtitle": "Five-button tailored vest with adjustable cinch back",
        "brand": "Soraia Studio",
        "category_id": "cat_linen_edit",
        "subcategory": "Waistcoats",
        "price": 3890.0,
        "original_price": 4590.0,
        "discount_pct": 15,
        "fabric": "100% Heavyweight Linen Twill",
        "fit_profile": "Runs Small - Size Up",
        "fit_notes": "Close-fitting bust dart construction. Customers with D+ cup or broader ribcage should size up.",
        "description": "An architectural take on classic menswear suiting, the Cannes Waistcoat features an asymmetric split hem and horn buckle strap at the back for custom waist suppression.",
        "care_instructions": "Dry clean only.",
        "occasion": "Evening Editorial",
        "sizes": ["XS", "S", "M", "L"],
        "colors": [{"name": "Obsidian Black", "hex": "#1B1B1B"}, {"name": "Flax Natural", "hex": "#D8CEBE"}],
        "primary_color": "Obsidian Black",
        "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 84,
        "return_rate_pct": 14.8,
        "is_featured": False,
        "is_new_arrival": False,
        "stock_count": 19,
        "search_tags": "waistcoat vest linen black sleeveless top women suiting",
    },
    {
        "id": "prd_005",
        "sku": "TL-OCC-001",
        "title": "Seraphina Bias-Cut Mulberry Silk Midi Dress",
        "subtitle": "Cowl-neck liquid drape dress cut on a 45-degree bias",
        "brand": "Soraia Studio",
        "category_id": "cat_occasion_dresses",
        "subcategory": "Midi Dresses",
        "price": 8990.0,
        "original_price": 10990.0,
        "discount_pct": 18,
        "fabric": "100% 22-Momme Mulberry Silk Satin",
        "fit_profile": "Runs Small - Size Up",
        "fit_notes": "Bias cut skims the hip closely without elastane. If between sizes in hip measurement, size up.",
        "description": "Cut on a true 45-degree bias from luminous 22-momme mulberry silk, the Seraphina Midi Dress skims the silhouette with fluid grace. Features adjustable rouleau shoulder straps and an internal French-seamed finish.",
        "care_instructions": "Specialist silk dry clean only.",
        "occasion": "Evening Editorial",
        "sizes": ["XS", "S", "M", "L"],
        "colors": [{"name": "Oxblood Burgundy", "hex": "#6E221E"}, {"name": "Champagne Gold", "hex": "#E3D3B6"}, {"name": "Midnight Ink", "hex": "#19202B"}],
        "primary_color": "Oxblood Burgundy",
        "image_url": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 97,
        "return_rate_pct": 16.5,
        "is_featured": True,
        "is_new_arrival": True,
        "stock_count": 22,
        "search_tags": "occasion dress silk midi dress burgundy party cocktail evening gown slip dress wedding guest",
    },
    {
        "id": "prd_006",
        "sku": "TL-OCC-002",
        "title": "Mirabel Pleated Architectural Column Gown",
        "subtitle": "Micro-pleated crinkle crepe gown with capelet sleeve",
        "brand": "Méridian Paris",
        "category_id": "cat_occasion_dresses",
        "subcategory": "Maxi Dresses",
        "price": 11490.0,
        "original_price": 13990.0,
        "discount_pct": 18,
        "fabric": "100% Recycled Japanese Triacetate Crepe",
        "fit_profile": "True to Size",
        "fit_notes": "Accordion micro-pleating expands naturally while maintaining vertical structure. Length is 142cm (best for 5'4\" and above).",
        "description": "Designed for gallery openings and destination celebrations, the Mirabel Column Gown pairs sculptural heat-set micro-pleats with an asymmetric draped shoulder capelet. Wrinkle-resistant for effortless travel.",
        "care_instructions": "Do not iron pleats; hand wash cold and roll dry.",
        "occasion": "Evening Editorial",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": [{"name": "Terracotta Rust", "hex": "#9E3B33"}, {"name": "Emerald Cypress", "hex": "#214234"}],
        "primary_color": "Terracotta Rust",
        "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 89,
        "return_rate_pct": 9.2,
        "is_featured": True,
        "is_new_arrival": False,
        "stock_count": 16,
        "search_tags": "pleated dress maxi gown occasion dress terracotta evening festive wedding guest",
    },
    {
        "id": "prd_007",
        "sku": "TL-OCC-003",
        "title": "Celeste Draped Cupro Wrap Midi Dress",
        "subtitle": "Kimono-sleeve wrap dress in matte sandwashed cupro",
        "brand": "Soraia Studio",
        "category_id": "cat_occasion_dresses",
        "subcategory": "Midi Dresses",
        "price": 6290.0,
        "original_price": 7490.0,
        "discount_pct": 16,
        "fabric": "100% Bemberg Sandwashed Cupro",
        "fit_profile": "True to Size",
        "fit_notes": "Wrap waist adjusts up to 5cm in either direction; hidden snap button at neckline prevents gaping.",
        "description": "Crafted from plant-derived Bemberg cupro with a peach-skin matte finish, the Celeste Wrap Dress resolves common wrap-dress frustrations with a secure internal stay button and generous overlap.",
        "care_instructions": "Gentle cold machine wash in garment bag.",
        "occasion": "Weekend Resort",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": [{"name": "Deep Fig", "hex": "#4E2E3A"}, {"name": "Sage Celadon", "hex": "#9CAF9E"}],
        "primary_color": "Deep Fig",
        "image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 86,
        "return_rate_pct": 6.8,
        "is_featured": False,
        "is_new_arrival": True,
        "stock_count": 31,
        "search_tags": "wrap dress midi dress occasion dress cupro dinner outfit",
    },
    {
        "id": "prd_008",
        "sku": "TL-OCC-004",
        "title": "Nocturne Structured Poplin Poise Midi",
        "subtitle": "Corset-seamed bodice with voluminous A-line poplin skirt",
        "brand": "Méridian Paris",
        "category_id": "cat_occasion_dresses",
        "subcategory": "Midi Dresses",
        "price": 7490.0,
        "original_price": 7490.0,
        "discount_pct": 0,
        "fabric": "97% Organic Cotton Poplin, 3% Elastane",
        "fit_profile": "Runs Small - Size Up",
        "fit_notes": "Boned bodice has minimal give; size up if between ribcage measurements.",
        "description": "Combining couture-inspired vertical seamwork through the torso with a dramatic, deep-pocketed poplin skirt, the Nocturne Midi transitions from daytime garden receptions to evening cocktails.",
        "care_instructions": "Dry clean or cold hand wash.",
        "occasion": "Evening Editorial",
        "sizes": ["XS", "S", "M", "L"],
        "colors": [{"name": "Espresso Noir", "hex": "#231F20"}, {"name": "Alabaster", "hex": "#F5F2EB"}],
        "primary_color": "Espresso Noir",
        "image_url": "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 82,
        "return_rate_pct": 13.4,
        "is_featured": False,
        "is_new_arrival": False,
        "stock_count": 24,
        "search_tags": "black dress poplin midi dress occasion dress party corset A-line",
    },
    {
        "id": "prd_009",
        "sku": "TL-MEN-001",
        "title": "Como Camp-Collar Slub Linen Shirt",
        "subtitle": "Relaxed boxy-fit resort shirt with tonal corozo buttons",
        "brand": "Veranda Collective",
        "category_id": "cat_mens_atelier",
        "subcategory": "Shirts",
        "price": 3690.0,
        "original_price": 4290.0,
        "discount_pct": 14,
        "fabric": "100% Italian Slub Linen (170 GSM)",
        "fit_profile": "Relaxed Tailored",
        "fit_notes": "Boxy vintage-inspired block with straight hem and side vents. True to size.",
        "description": "Cut from garment-washed Italian slub linen that softens with every wear, the Como Camp-Collar Shirt features a one-piece collar construction that lies cleanly open or buttoned.",
        "care_instructions": "Machine wash cold, hang dry.",
        "occasion": "Weekend Resort",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": [{"name": "Tobacco Brown", "hex": "#6D4C3D"}, {"name": "Salt White", "hex": "#F6F5F0"}, {"name": "Aegean Slate", "hex": "#4B6071"}],
        "primary_color": "Tobacco Brown",
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 95,
        "return_rate_pct": 4.9,
        "is_featured": True,
        "is_new_arrival": True,
        "stock_count": 46,
        "search_tags": "linen shirt men camp collar brown casual resort shirt summer",
    },
    {
        "id": "prd_010",
        "sku": "TL-MEN-002",
        "title": "Brera Unstructured Hopsack Travel Blazer",
        "subtitle": "Half-canvas breathable wool-linen jacket with patch pockets",
        "brand": "Veranda Collective",
        "category_id": "cat_mens_atelier",
        "subcategory": "Blazers",
        "price": 9490.0,
        "original_price": 11990.0,
        "discount_pct": 21,
        "fabric": "55% Virgin Wool, 45% Flax Linen Hopsack",
        "fit_profile": "True to Size",
        "fit_notes": "Natural unpadded shoulder with tailored waist taper. Order your regular chest size.",
        "description": "The Brera Hopsack Blazer eliminates heavy shoulder pads and stiff fusing in favor of an open-weave wool-linen hopsack that resists creasing in transit while breathing effortlessly in warm climates.",
        "care_instructions": "Dry clean only; brush after wear.",
        "occasion": "Work & Atelier",
        "sizes": ["S", "M", "L", "XL"],
        "colors": [{"name": "Navy Indigo", "hex": "#222B3A"}, {"name": "Sandstone Taupe", "hex": "#B7A996"}],
        "primary_color": "Navy Indigo",
        "image_url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1593032465175-481ac7f401a0?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 88,
        "return_rate_pct": 7.6,
        "is_featured": False,
        "is_new_arrival": False,
        "stock_count": 21,
        "search_tags": "oversized blazer men unstructured jacket navy wool linen formal suit",
    },
    {
        "id": "prd_011",
        "sku": "TL-MEN-003",
        "title": "Luca Gurkha-Waist Tapered Cotton Trouser",
        "subtitle": "Extended double-buckle waistband trouser in brushed cavalry twill",
        "brand": "Veranda Collective",
        "category_id": "cat_mens_atelier",
        "subcategory": "Trousers",
        "price": 4990.0,
        "original_price": 5990.0,
        "discount_pct": 17,
        "fabric": "100% Combed Organic Cotton Cavalry Twill (280 GSM)",
        "fit_profile": "Runs Small - Size Up",
        "fit_notes": "High-rise Gurkha waistband sits at the natural navel rather than hip bone. Size up if you prefer wearing trousers lower on the waist.",
        "description": "Inspired by classic sartorial tailoring, the Luca Gurkha Trouser removes the need for a belt via dual solid-brass side adjusters and deep forward pleats that narrow to a clean 19cm hem.",
        "care_instructions": "Machine wash cold inside out.",
        "occasion": "Work & Atelier",
        "sizes": ["S", "M", "L", "XL"],
        "colors": [{"name": "Khaki Parchment", "hex": "#C8B99E"}, {"name": "Dark Olive", "hex": "#3E4735"}, {"name": "Charcoal", "hex": "#333538"}],
        "primary_color": "Khaki Parchment",
        "image_url": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 90,
        "return_rate_pct": 15.6,
        "is_featured": False,
        "is_new_arrival": True,
        "stock_count": 33,
        "search_tags": "gurkha trouser men pleated pants chino khaki formal wide leg trouser",
    },
    {
        "id": "prd_012",
        "sku": "TL-MEN-004",
        "title": "Vespera Fine-Knit Silk-Cotton Polo",
        "subtitle": "16-gauge full-fashioned knit polo withJohnny collar",
        "brand": "Aurelia Knit",
        "category_id": "cat_mens_atelier",
        "subcategory": "Knitwear",
        "price": 4190.0,
        "original_price": 4190.0,
        "discount_pct": 0,
        "fabric": "70% Supima Cotton, 30% Mulberry Silk",
        "fit_profile": "True to Size",
        "fit_notes": "Ribbed hem and cuffs hug softly without clinging. True to size.",
        "description": "Knitted on 16-gauge machines for a smooth, luminous handfeel, the Vespera Polo elevates smart-casual dressing under a blazer or paired with pleated linen trousers.",
        "care_instructions": "Hand wash cold, dry flat.",
        "occasion": "Elevated Everyday",
        "sizes": ["S", "M", "L", "XL"],
        "colors": [{"name": "Espresso", "hex": "#382C26"}, {"name": "Cream Ecru", "hex": "#EFECE4"}],
        "primary_color": "Espresso",
        "image_url": "https://images.unsplash.com/photo-1626497764746-6dc36546b388?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 85,
        "return_rate_pct": 5.3,
        "is_featured": False,
        "is_new_arrival": False,
        "stock_count": 40,
        "search_tags": "knit polo men silk cotton t-shirt smart casual brown",
    },
    {
        "id": "prd_013",
        "sku": "TL-KNT-001",
        "title": "Alma Extra-Fine Merino Ribbed Cardigan",
        "subtitle": "Sculptural bell-sleeve cardigan in 19.5-micron Australian merino",
        "brand": "Aurelia Knit",
        "category_id": "cat_knitwear_separates",
        "subcategory": "Knitwear",
        "price": 5490.0,
        "original_price": 6490.0,
        "discount_pct": 15,
        "fabric": "100% RWS-Certified Extra-Fine Merino Wool",
        "fit_profile": "True to Size",
        "fit_notes": "Engineered varicose rib knit molds comfortably to the torso and springs back after wear.",
        "description": "Spun from non-mulesed 19.5-micron merino wool, the Alma Cardigan features architectural two-way tonal buttons that can be fastened asymmetrically for a draped waist.",
        "care_instructions": "Cold wool cycle or hand wash; dry flat.",
        "occasion": "Work & Atelier",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": [{"name": "Claret Burgundy", "hex": "#7C2D26"}, {"name": "Heather Grey", "hex": "#8D8F92"}, {"name": "Camel Hair", "hex": "#C19A6B"}],
        "primary_color": "Claret Burgundy",
        "image_url": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 93,
        "return_rate_pct": 6.1,
        "is_featured": True,
        "is_new_arrival": True,
        "stock_count": 37,
        "search_tags": "merino cardigan sweater knitwear women burgundy wool layering",
    },
    {
        "id": "prd_014",
        "sku": "TL-KNT-002",
        "title": "Sloane Milano-Knit Column Midi Skirt",
        "subtitle": "Dense double-faced knit skirt with concealed back vent",
        "brand": "Aurelia Knit",
        "category_id": "cat_knitwear_separates",
        "subcategory": "Skirts",
        "price": 4690.0,
        "original_price": 5490.0,
        "discount_pct": 15,
        "fabric": "72% Ecovero Viscose, 28% PBT Stretch Filament",
        "fit_profile": "True to Size",
        "fit_notes": "Dense Milano stitch prevents bagging at the knees or seat even after 10+ hours of sitting.",
        "description": "Designed to solve the common issue of knit skirts losing shape, the Sloane Column Skirt uses a high-tension Milano stitch with an encased elastic waist that lies completely flat under sweaters.",
        "care_instructions": "Machine wash cold gentle, dry flat.",
        "occasion": "Work & Atelier",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": [{"name": "Espresso", "hex": "#332824"}, {"name": "Warm Bone", "hex": "#E8E2D5"}],
        "primary_color": "Espresso",
        "image_url": "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1551163943-3f6a855d1153?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 83,
        "return_rate_pct": 5.8,
        "is_featured": False,
        "is_new_arrival": False,
        "stock_count": 28,
        "search_tags": "pleated midi skirt knit skirt column skirt women office wear brown",
    },
    {
        "id": "prd_015",
        "sku": "TL-KNT-003",
        "title": "Marais Oversized Cashmere-Blend Crewneck",
        "subtitle": "Saddle-shoulder relaxed pullover in recycled cashmere and merino",
        "brand": "Aurelia Knit",
        "category_id": "cat_knitwear_separates",
        "subcategory": "Knitwear",
        "price": 7990.0,
        "original_price": 9490.0,
        "discount_pct": 16,
        "fabric": "70% Recycled Cashmere, 30% Extra-Fine Merino",
        "fit_profile": "Oversized Architectural",
        "fit_notes": "Intentionally oversized cocoon silhouette. Size down one size if you prefer a classic neat fit.",
        "description": "Spun in Biella, Italy from post-consumer cashmere fibers blended with virgin merino for tensile strength and low pilling, the Marais Crewneck features deep rib trims and saddle shoulder detailing.",
        "care_instructions": "Hand wash cold with wool detergent.",
        "occasion": "Elevated Everyday",
        "sizes": ["XS", "S", "M", "L"],
        "colors": [{"name": "Oatmeal Heather", "hex": "#DCD4C6"}, {"name": "Charcoal", "hex": "#36383A"}],
        "primary_color": "Oatmeal Heather",
        "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1578587018452-892bacefd3f2?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 87,
        "return_rate_pct": 8.4,
        "is_featured": False,
        "is_new_arrival": True,
        "stock_count": 20,
        "search_tags": "cashmere sweater oversized pullover women knitwear oatmeal",
    },
    {
        "id": "prd_016",
        "sku": "TL-KNT-004",
        "title": "Helena Mock-Neck Sleeveless Knit Shell",
        "subtitle": "Seamless tubular-knit tank for under-blazer layering",
        "brand": "Kora & Loom",
        "category_id": "cat_knitwear_separates",
        "subcategory": "Tops",
        "price": 2490.0,
        "original_price": 2890.0,
        "discount_pct": 14,
        "fabric": "85% Organic Combed Cotton, 15% Silk",
        "fit_profile": "True to Size",
        "fit_notes": "Armholes are cut high to conceal bra straps completely. True to size.",
        "description": "An essential architectural foundation piece, the Helena Knit Shell is knitted on seamless circular looms with a clean mock neck and bra-friendly shoulder coverage.",
        "care_instructions": "Machine wash cold gentle.",
        "occasion": "Work & Atelier",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": [{"name": "Ivory Chalk", "hex": "#F4F1EA"}, {"name": "Black Ink", "hex": "#1B1B1B"}, {"name": "Terracotta", "hex": "#9E3B33"}],
        "primary_color": "Ivory Chalk",
        "image_url": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 88,
        "return_rate_pct": 4.2,
        "is_featured": False,
        "is_new_arrival": False,
        "stock_count": 64,
        "search_tags": "sleeveless knit tank top mock neck layering women office wear",
    },
    {
        "id": "prd_017",
        "sku": "TL-DEN-001",
        "title": "Okayama 13.5oz Selvedge Straight Jean",
        "subtitle": "Rope-dyed indigo red-line selvedge denim with mid-high rise",
        "brand": "Noma Hardware",
        "category_id": "cat_denim_utility",
        "subcategory": "Jeans",
        "price": 6490.0,
        "original_price": 7490.0,
        "discount_pct": 13,
        "fabric": "100% Japanese Shuttle-Loomed Selvedge Cotton (13.5 oz)",
        "fit_profile": "Runs Small - Size Up",
        "fit_notes": "Rigid 100% cotton selvedge has zero synthetic stretch and feels snug on first wear before molding to the wearer over 5-7 wears. Size up if between waist sizes.",
        "description": "Woven on vintage Toyoda shuttle looms in Kojima, Japan, our Straight Jean features copper rivets, a vegetable-tanned waist patch, and classic red-line selvedge outseams that look sharp cuffed.",
        "care_instructions": "Spot clean or cold soak inside out; never tumble dry.",
        "occasion": "Elevated Everyday",
        "sizes": ["S", "M", "L", "XL"],
        "colors": [{"name": "Raw Rinse Indigo", "hex": "#1E2A38"}, {"name": "Washed Ecru", "hex": "#E5DFD2"}],
        "primary_color": "Raw Rinse Indigo",
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 92,
        "return_rate_pct": 16.9,
        "is_featured": True,
        "is_new_arrival": False,
        "stock_count": 35,
        "search_tags": "selvedge denim jeans men straight leg raw indigo cotton",
    },
    {
        "id": "prd_018",
        "sku": "TL-DEN-002",
        "title": "Marseille Garment-Dyed Canvas Chore Jacket",
        "subtitle": "Three-pocket French workwear jacket in 11oz organic bull denim",
        "brand": "Noma Hardware",
        "category_id": "cat_denim_utility",
        "subcategory": "Jackets",
        "price": 5890.0,
        "original_price": 6990.0,
        "discount_pct": 16,
        "fabric": "100% Organic Cotton Bull Canvas (360 GSM)",
        "fit_profile": "Relaxed Tailored",
        "fit_notes": "Boxy workwear silhouette designed to layer comfortably over hoodies or knitwear.",
        "description": "Modeled after 1950s Lyonnaise studio jackets, the Marseille Chore Jacket is garment-dyed for rich seam highs and lows, complete with an interior chest pocket for a notebook or phone.",
        "care_instructions": "Machine wash cold separately.",
        "occasion": "Elevated Everyday",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": [{"name": "Faded Sage", "hex": "#6E7B68"}, {"name": "Workwear Ochre", "hex": "#B5833E"}, {"name": "フレンチ Navy", "hex": "#253146"}],
        "primary_color": "Faded Sage",
        "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1544022613-e87ca75a784a?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 86,
        "return_rate_pct": 6.2,
        "is_featured": False,
        "is_new_arrival": True,
        "stock_count": 27,
        "search_tags": "chore jacket workwear men canvas coat overshirt green",
    },
    {
        "id": "prd_019",
        "sku": "TL-DEN-003",
        "title": "Kojima Barrel-Leg High-Rise Women's Jean",
        "subtitle": "Sculpted curved-leg silhouette in 12oz organic vintage wash",
        "brand": "Noma Hardware",
        "category_id": "cat_denim_utility",
        "subcategory": "Jeans",
        "price": 5290.0,
        "original_price": 5990.0,
        "discount_pct": 12,
        "fabric": "99% Organic Cotton, 1% Comfort Elastane",
        "fit_profile": "True to Size",
        "fit_notes": "Nipped at the high waist with a curved outer seam that tapers at the ankle. 28-inch inseam hits cleanly at the ankle bone for heights 5'3\"–5'7\".",
        "description": "Our signature architectural denim fit for women, the Kojima Barrel Jean creates volume through the leg while maintaining a clean, defined waist and ankle-grazing crop.",
        "care_instructions": "Wash cold inside out, line dry.",
        "occasion": "Elevated Everyday",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": [{"name": "Vintage Mid-Wash", "hex": "#5C7693"}, {"name": "Washed Charcoal", "hex": "#36383C"}],
        "primary_color": "Vintage Mid-Wash",
        "image_url": "https://images.unsplash.com/photo-1584370848010-d7fe6bc767ec?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 90,
        "return_rate_pct": 9.8,
        "is_featured": False,
        "is_new_arrival": True,
        "stock_count": 41,
        "search_tags": "barrel jeans women high waist denim wide leg ankle crop",
    },
    {
        "id": "prd_020",
        "sku": "TL-DEN-004",
        "title": "Arles Heavyweight Herringbone Utility Pant",
        "subtitle": "Fatigue pocket trouser in enzyme-washed cotton herringbone",
        "brand": "Noma Hardware",
        "category_id": "cat_denim_utility",
        "subcategory": "Trousers",
        "price": 4590.0,
        "original_price": 4590.0,
        "discount_pct": 0,
        "fabric": "100% Cotton Herringbone Twill (310 GSM)",
        "fit_profile": "True to Size",
        "fit_notes": "Straight utility cut with button waist tabs allowing 2.5cm waist adjustment.",
        "description": "Built from custom-milled herringbone twill that develops a vintage patina over time, featuring rectangular patch pockets and double-needle felled seams.",
        "care_instructions": "Machine wash warm, tumble dry low.",
        "occasion": "Weekend Resort",
        "sizes": ["S", "M", "L", "XL"],
        "colors": [{"name": "Army Olive", "hex": "#4E5741"}, {"name": "Stone Ecru", "hex": "#DDD7C9"}],
        "primary_color": "Army Olive",
        "image_url": "https://images.unsplash.com/photo-1517445312882-bc9910d016b7?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 81,
        "return_rate_pct": 5.5,
        "is_featured": False,
        "is_new_arrival": False,
        "stock_count": 30,
        "search_tags": "cargo utility pants herringbone olive trousers men cotton",
    },
    {
        "id": "prd_021",
        "sku": "TL-LTH-001",
        "title": "Palermo Unlined Calfskin Penny Loafer",
        "subtitle": "Blake-stitched supple Italian leather loafer with stacked heel",
        "brand": "Tierra Leather",
        "category_id": "cat_leather_goods",
        "subcategory": "Footwear",
        "price": 8490.0,
        "original_price": 9990.0,
        "discount_pct": 15,
        "fabric": "100% Full-Grain Vegetable-Tanned Tuscan Calfskin",
        "fit_profile": "Runs Small - Size Up",
        "fit_notes": "Almond toe box runs narrow across the instep. Customers with wide feet or high insteps should size up.",
        "description": "Hand-lasted using flexible Blake-rapid construction, the Palermo Penny Loafer requires zero break-in period thanks to its glove-soft unlined calfskin upper and memory-foam leather footbed.",
        "care_instructions": "Condition with neutral leather balm and cedar shoe trees.",
        "occasion": "Work & Atelier",
        "sizes": ["S", "M", "L", "XL"],
        "colors": [{"name": "Oxblood Cordovan", "hex": "#5C1E1B"}, {"name": "Espresso Brown", "hex": "#33241E"}, {"name": "Black Calf", "hex": "#181818"}],
        "primary_color": "Oxblood Cordovan",
        "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 94,
        "return_rate_pct": 14.2,
        "is_featured": True,
        "is_new_arrival": False,
        "stock_count": 25,
        "search_tags": "leather loafers shoes penny loafer oxblood brown formal footwear",
    },
    {
        "id": "prd_022",
        "sku": "TL-LTH-002",
        "title": "Arco Sculptural Saddle-Leather Everyday Tote",
        "subtitle": "Architectural East-West shoulder bag fits a 15-inch laptop",
        "brand": "Tierra Leather",
        "category_id": "cat_leather_goods",
        "subcategory": "Bags",
        "price": 10990.0,
        "original_price": 12990.0,
        "discount_pct": 15,
        "fabric": "100% LWG Gold-Rated Pebbled Saddle Leather",
        "fit_profile": "True to Size",
        "fit_notes": "Dimensions: 41cm W x 29cm H x 15cm D. Strap drop: 26cm (fits over winter coats).",
        "description": "Designed for daily studio-to-evening transit, the Arco Tote features hand-painted raw edges, a padded 15-inch laptop sleeve, a magnetic brass bridge closure, and an internal key leash.",
        "care_instructions": "Wipe with dry microfiber cloth; store in cotton dustbag.",
        "occasion": "Work & Atelier",
        "sizes": ["M"],
        "colors": [{"name": "Cognac Tan", "hex": "#8B4A2B"}, {"name": "Black Pebble", "hex": "#1C1C1C"}, {"name": "Dark Olive", "hex": "#3C4233"}],
        "primary_color": "Cognac Tan",
        "image_url": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 92,
        "return_rate_pct": 3.8,
        "is_featured": True,
        "is_new_arrival": True,
        "stock_count": 18,
        "search_tags": "leather tote bag laptop bag women work bag cognac tan shoulder handbag",
    },
    {
        "id": "prd_023",
        "sku": "TL-LTH-003",
        "title": "Siena Woven Leather Mule Sandal",
        "subtitle": "Hand-braided nappa leather square-toe mule with 35mm block heel",
        "brand": "Tierra Leather",
        "category_id": "cat_leather_goods",
        "subcategory": "Footwear",
        "price": 6290.0,
        "original_price": 7290.0,
        "discount_pct": 14,
        "fabric": "100% Hand-Woven Lambskin Nappa",
        "fit_profile": "True to Size",
        "fit_notes": "Woven leather upper molds to foot width within 2 hours of wear.",
        "description": "Artisanal strips of supple lambskin nappa are woven by hand over a wooden last to create a breathable, architectural summer mule resting on a stable 35mm architectural heel.",
        "care_instructions": "Protect with water-repellent spray before wear.",
        "occasion": "Weekend Resort",
        "sizes": ["XS", "S", "M", "L"],
        "colors": [{"name": "Caramel Cuoio", "hex": "#A8653B"}, {"name": "Warm Bone", "hex": "#EAE3D5"}],
        "primary_color": "Caramel Cuoio",
        "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 85,
        "return_rate_pct": 7.1,
        "is_featured": False,
        "is_new_arrival": True,
        "stock_count": 29,
        "search_tags": "woven leather mules sandals heels women summer footwear",
    },
    {
        "id": "prd_024",
        "sku": "TL-LTH-004",
        "title": "Castel Solid Brass & Bridle Leather Belt",
        "subtitle": "30mm vegetable-tanned English bridle belt with sand-cast buckle",
        "brand": "Tierra Leather",
        "category_id": "cat_leather_goods",
        "subcategory": "Accessories",
        "price": 2990.0,
        "original_price": 2990.0,
        "discount_pct": 0,
        "fabric": "100% 4mm Full-Grain Bridle Leather & Solid Brass",
        "fit_profile": "True to Size",
        "fit_notes": "Five adjustment holes spaced 2.5cm apart. S fits 26-30\", M fits 30-34\", L fits 34-38\".",
        "description": "Cut from a single hide of wax-finished bridle leather and paired with a custom sand-cast solid brass buckle that develops a warm patina over decades of wear.",
        "care_instructions": "Buff with horsehair brush.",
        "occasion": "Elevated Everyday",
        "sizes": ["S", "M", "L", "XL"],
        "colors": [{"name": "Dark Havana", "hex": "#3B261D"}, {"name": "Black", "hex": "#151515"}],
        "primary_color": "Dark Havana",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80",
        "secondary_image_url": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=80",
        "popularity_score": 80,
        "return_rate_pct": 2.9,
        "is_featured": False,
        "is_new_arrival": False,
        "stock_count": 55,
        "search_tags": "leather belt brass buckle accessories men women brown",
    },
]


REVIEW_TEMPLATES = [
    # Size and fit complaints (most frequent pain point in fashion discovery!)
    {
        "product_id": "prd_002",
        "rating": 2,
        "title": "Beautiful linen drape, but waistband runs a full size small",
        "comment_text": "I ordered my usual Size S in the Solstice Pleated Linen Trouser and could barely fasten the hook-and-bar waist. The fabric itself is gorgeous and not see-through, but the product card during search didn't mention that the waistband has zero give. Had to initiate an exchange for M.",
        "sentiment": "negative",
        "complaint_category": "Size and fit",
        "fit_feedback": "Runs Small",
    },
    {
        "product_id": "prd_005",
        "rating": 2,
        "title": "Bias cut is much tighter across the hips than expected",
        "comment_text": "The Oxblood mulberry silk color is stunning in person, however the hip measurement on Size M feels closer to an XS/S. When browsing occasion dresses, I wish I could filter by body-type fit profile or see verified buyer fit warnings upfront.",
        "sentiment": "negative",
        "complaint_category": "Size and fit",
        "fit_feedback": "Runs Small",
    },
    {
        "product_id": "prd_017",
        "rating": 3,
        "title": "Incredible Japanese selvedge, but size up for rigid waist",
        "comment_text": "13.5oz denim quality rivals brands twice the price. However, first-time selvedge buyers need a clearer heads-up before adding to bag that unwashed cotton runs snug in the thigh and waist.",
        "sentiment": "neutral",
        "complaint_category": "Size and fit",
        "fit_feedback": "Runs Small",
    },
    {
        "product_id": "prd_021",
        "rating": 2,
        "title": "Narrow instep on the Palermo Penny Loafer",
        "comment_text": "Leather craftsmanship is top notch, yet the almond toe box pinched my instep immediately. Please add width guidance and 'Runs Narrow/Small' badges on the search results card.",
        "sentiment": "negative",
        "complaint_category": "Size and fit",
        "fit_feedback": "Runs Small",
    },
    {
        "product_id": "prd_011",
        "rating": 3,
        "title": "High Gurkha rise sits higher than regular trousers",
        "comment_text": "Love the brass buckle detail on the Luca Gurkha trouser, but because it sits at the navel, my regular Medium felt tight after lunch. Sizing up to Large solved it.",
        "sentiment": "neutral",
        "complaint_category": "Size and fit",
        "fit_feedback": "Runs Small",
    },
    {
        "product_id": "prd_004",
        "rating": 2,
        "title": "Bust darts are cut very narrow on the Cannes Waistcoat",
        "comment_text": "Ordered Size S based on the generic size chart, but the top two buttons pull across the chest. Needs garment-specific chest measurements on the PDP.",
        "sentiment": "negative",
        "complaint_category": "Size and fit",
        "fit_feedback": "Runs Small",
    },
    # Search relevance complaints
    {
        "product_id": "prd_001",
        "rating": 3,
        "title": "Hard to find matching suit separates through search bar",
        "comment_text": "The Valence Linen Blazer is my favourite jacket this season, but when I searched 'breathable summer office wear' and 'linen co-ord set', the search returned zero results! I only found this blazer by manually clicking through categories.",
        "sentiment": "negative",
        "complaint_category": "Search relevance",
        "fit_feedback": "True to Size",
    },
    {
        "product_id": "prd_006",
        "rating": 3,
        "title": "Great gown, but occasion search terms didn't surface it",
        "comment_text": "I searched for 'haldi guest outfit' and 'festive cocktail maxi' and got empty results, even though this Mirabel Terracotta gown is literally ideal for Indian destination weddings. Search needs synonym mapping for occasion wear.",
        "sentiment": "negative",
        "complaint_category": "Search relevance",
        "fit_feedback": "True to Size",
    },
    {
        "product_id": "prd_019",
        "rating": 2,
        "title": "Size filter didn't exclude out-of-stock variants in control view",
        "comment_text": "Spent 15 minutes clicking on denim trousers that showed up in search results only to realize my size was out of stock or not clearly filtered by fit profile.",
        "sentiment": "negative",
        "complaint_category": "Search relevance",
        "fit_feedback": "True to Size",
    },
    # Product images complaints
    {
        "product_id": "prd_003",
        "rating": 3,
        "title": "Ecru Sand shade is slightly warmer in natural daylight",
        "comment_text": "The Aerin Popover shirt feels wonderful on the skin, though studio lighting makes Ecru Sand look stark white when it is actually a warm oatmeal-ecru tone. Adding an outdoor daylight swatch photo would help.",
        "sentiment": "neutral",
        "complaint_category": "Product images",
        "fit_feedback": "True to Size",
    },
    {
        "product_id": "prd_008",
        "rating": 2,
        "title": "Needed close-up photos of the back bodice boning",
        "comment_text": "Could not tell from the two main photos whether the back had smocking or a rigid zip. A 360 fabric detail zoom would reduce pre-purchase hesitation.",
        "sentiment": "negative",
        "complaint_category": "Product images",
        "fit_feedback": "Runs Small",
    },
    # Product quality / fabric care
    {
        "product_id": "prd_015",
        "rating": 3,
        "title": "Soft cashmere blend, slight pilling under crossbody bag strap",
        "comment_text": "Very cozy oversized sweater, but noticed minor friction pilling after wearing it with a leather shoulder bag for three days. Included cashmere comb instructions would be nice.",
        "sentiment": "neutral",
        "complaint_category": "Product quality",
        "fit_feedback": "Runs Large",
    },
    # Pricing & Delivery & Checkout
    {
        "product_id": "prd_010",
        "rating": 4,
        "title": "Premium price point, though tailoring justifies it on sale",
        "comment_text": "At ₹11,990 original price I hesitated in my cart for a week, but at ₹9,490 the half-canvas wool-linen construction is genuinely superior to high-street blazers.",
        "sentiment": "neutral",
        "complaint_category": "Pricing",
        "fit_feedback": "True to Size",
    },
    {
        "product_id": "prd_022",
        "rating": 4,
        "title": "Tote is a 10/10, courier took 5 days to Tier-2 city",
        "comment_text": "The Arco Saddle-Leather Tote fits my 15-inch MacBook Pro with room to spare. Only minor gripe is delivery to Jaipur took 5 days instead of the estimated 3.",
        "sentiment": "neutral",
        "complaint_category": "Delivery experience",
        "fit_feedback": "True to Size",
    },
    {
        "product_id": "prd_013",
        "rating": 4,
        "title": "Wished promo code box was visible before starting checkout",
        "comment_text": "The Alma Merino Cardigan in Claret Burgundy is museum-grade knitwear. In the shopping bag drawer, showing estimated shipping & promo eligibility earlier would reduce cart drop-off.",
        "sentiment": "neutral",
        "complaint_category": "Checkout experience",
        "fit_feedback": "True to Size",
    },
    # Praise / 5-star reviews
    {
        "product_id": "prd_001",
        "rating": 5,
        "title": "The ultimate warm-weather architectural blazer",
        "comment_text": "Finally a linen blazer that doesn't look sloppy by noon. The Normandy flax has substantial weight and the chambray interior binding is a luxury touch.",
        "sentiment": "positive",
        "complaint_category": "None (Praise)",
        "fit_feedback": "True to Size",
    },
    {
        "product_id": "prd_009",
        "rating": 5,
        "title": "Best camp-collar linen shirt in my wardrobe",
        "comment_text": "Bought Tobacco Brown and immediately came back for Salt White. Collar rolls naturally and the slub texture feels authentically Italian.",
        "sentiment": "positive",
        "complaint_category": "None (Praise)",
        "fit_feedback": "True to Size",
    },
    {
        "product_id": "prd_007",
        "rating": 5,
        "title": "Hidden snap button on a wrap dress is genius",
        "comment_text": "So rare to find a wrap dress that actually stays secure at the neckline without safety pins! The Bemberg cupro drapes like heavy washed silk.",
        "sentiment": "positive",
        "complaint_category": "None (Praise)",
        "fit_feedback": "True to Size",
    },
    {
        "product_id": "prd_014",
        "rating": 5,
        "title": "Zero bagging at the knees after a full workday",
        "comment_text": "The Milano stitch holds its column shape all day in the studio. Pairs effortlessly with the Valence blazer and Palermo loafers.",
        "sentiment": "positive",
        "complaint_category": "None (Praise)",
        "fit_feedback": "True to Size",
    },
    {
        "product_id": "prd_022",
        "rating": 5,
        "title": "Replaced my designer work bag immediately",
        "comment_text": "Full-grain pebbled leather smells incredible, stands upright on its own, and the dedicated laptop compartment is properly padded.",
        "sentiment": "positive",
        "complaint_category": "None (Praise)",
        "fit_feedback": "True to Size",
    },
]


ROADMAP_ITEMS_DATA = [
    {
        "id": "rm_001",
        "jira_key": "THRD-101",
        "epic_name": "Intelligent Search & Synonym Discovery",
        "title": "Semantic Occasion & Fabric Synonym Query Expansion",
        "problem_evidence": "Search Intelligence logs show 18.4% of searches hit zero-result or low-relevance walls on occasion/cultural terms ('haldi guest outfit', 'breathable summer office wear', 'linen co-ord set'), driving a 54% search abandonment rate on multi-word queries.",
        "user_story": "As a customer searching by occasion or fabric feel, I want relevant products to appear even when my phrasing differs from catalog SKU titles so that I never hit a dead-end zero-result screen.",
        "acceptance_criteria": [
            "Map 150+ occasion, climate, and silhouette synonyms to structured product attributes (occasion, fabric, subcategory).",
            "Reduce zero-result search rate from 14.2% to < 3.5% across top 200 search queries.",
            "When exact matches = 0, automatically render semantic fallback recommendations with transparent match explanation tags.",
            "Track `search_submitted` with `synonym_expanded: true` property in Mixpanel and PostgreSQL events."
        ],
        "reach_score": 14500,
        "impact_score": 2.5,
        "confidence_pct": 90,
        "effort_person_weeks": 3.0,
        "customer_impact": "Critical",
        "business_impact": "+3.8% Search-to-PDP CTR, +₹18.4L projected monthly GMV",
        "status": "In Progress",
        "sprint": "Sprint 14 (Current)",
        "owner": "Ananya Rao (PM - Discovery)",
    },
    {
        "id": "rm_002",
        "jira_key": "THRD-102",
        "epic_name": "Fit Confidence & Size Intelligence",
        "title": "Persistent 'In-My-Size' & Fit-Profile Facet Bar on Search/PLP",
        "problem_evidence": "38% of negative customer reviews cite 'Size and fit' mismatches (e.g., Solstice Trouser & Seraphina Silk Midi running small), and funnel analytics reveal a 41% drop-off between PDP view and Add-to-Bag for structured non-stretch garments.",
        "user_story": "As a customer, I want relevant products to appear when I search using a category and size—along with upfront 'Runs Small / True to Size' badges—so that I can find suitable products faster and buy with confidence.",
        "acceptance_criteria": [
            "Display one-tap size pills (XS–XXL) and Fit Profile filters ('True to Size', 'Relaxed Tailored', 'Runs Small - Size Up') at the top of Search.",
            "Surface verified buyer fit callout badges directly on product cards in the treatment variant.",
            "Achieve >= 18% relative lift in Search-to-Bag conversion in A/B Experiment `exp_semantic_size_fit_filters` at p < 0.05."
        ],
        "reach_score": 16000,
        "impact_score": 2.0,
        "confidence_pct": 95,
        "effort_person_weeks": 2.5,
        "customer_impact": "Critical",
        "business_impact": "+24% Add-to-Bag lift in Treatment, -3.2% size-related return rate",
        "status": "In Progress",
        "sprint": "Sprint 14 (Current)",
        "owner": "Ananya Rao (PM - Discovery)",
    },
    {
        "id": "rm_003",
        "jira_key": "THRD-103",
        "epic_name": "Fit Confidence & Size Intelligence",
        "title": "Verified Buyer Fit Distribution & Garment Measurement Matrix on PDP",
        "problem_evidence": "GenAI Customer Intelligence identified 34 reviews explicitly requesting garment waist/hip/instep measurements rather than generic body charts (especially on `prd_002`, `prd_005`, `prd_021`).",
        "user_story": "As a fit-conscious shopper viewing a Product Detail Page, I want to see aggregated buyer fit consensus ('68% say Runs Small — Size Up') and exact garment measurements so that I select the right size on my first order.",
        "acceptance_criteria": [
            "Render visual fit spectrum bar (Runs Small / True to Size / Runs Large) aggregated live from verified `reviews` records.",
            "Display fabric stretch index, GSM weight, and specific fit guidance notes above the fold near the size selector.",
            "Reduce PDP-to-Bag hesitation time by 15% and lower exchange requests on non-stretch linen/selvedge SKUs by 20%."
        ],
        "reach_score": 12000,
        "impact_score": 2.0,
        "confidence_pct": 90,
        "effort_person_weeks": 2.0,
        "customer_impact": "High",
        "business_impact": "+2.9% PDP-to-Cart CVR, -₹6.2L monthly reverse-logistics cost",
        "status": "Shipped",
        "sprint": "Sprint 13",
        "owner": "Rohan Mehta (PM - PDP Experience)",
    },
    {
        "id": "rm_004",
        "jira_key": "THRD-104",
        "epic_name": "Intelligent Search & Synonym Discovery",
        "title": "Zero-Result Recovery Engine with Curated Editorial Fallbacks",
        "problem_evidence": "Prior to recovery module, 81% of sessions encountering a 0-result search exited within 25 seconds without viewing a single product page.",
        "user_story": "As a shopper whose specific search query yields zero exact matches, I want immediate suggested query refinements and closest-match capsule pieces so I can continue my discovery journey.",
        "acceptance_criteria": [
            "Detect 0-result queries in real time and log `zero_result: true` in `searches` table.",
            "Present clickable trending query chips and 4 curated high-converting products matching any partial token or user preferred category.",
            "Recover >= 35% of zero-result sessions into a subsequent `product_viewed` event."
        ],
        "reach_score": 6800,
        "impact_score": 2.0,
        "confidence_pct": 85,
        "effort_person_weeks": 1.5,
        "customer_impact": "High",
        "business_impact": "Recovers ~2,400 lost discovery sessions/month",
        "status": "Shipped",
        "sprint": "Sprint 13",
        "owner": "Ananya Rao (PM - Discovery)",
    },
    {
        "id": "rm_005",
        "jira_key": "THRD-105",
        "epic_name": "Visual Merchandising & Photography",
        "title": "Natural Daylight Color Swatch & Fabric Drape Video Loop on PDP",
        "problem_evidence": "Feedback analysis shows 14% of neutral/negative reviews mention studio lighting color discrepancy (e.g., Ecru Sand vs stark white on `prd_003`) or inability to gauge fabric stiffness.",
        "user_story": "As an online fashion buyer, I want to toggle between studio lookbook photography and natural daylight fabric close-ups so that I accurately judge color undertone and texture.",
        "acceptance_criteria": [
            "Support dual-image hover and gallery inspection with color hex accuracy tags on all 24 catalog SKUs.",
            "Add GSM fabric weight and weave transparency notes in the PDP specification accordion.",
            "Decrease 'Color/Image mismatch' feedback share by 40% over 60 days."
        ],
        "reach_score": 9500,
        "impact_score": 1.5,
        "confidence_pct": 80,
        "effort_person_weeks": 2.5,
        "customer_impact": "Medium",
        "business_impact": "+1.4% PDP conversion on light/pastel colorways",
        "status": "Next Sprint",
        "sprint": "Sprint 15",
        "owner": "Devika Nair (Design Lead)",
    },
    {
        "id": "rm_006",
        "jira_key": "THRD-106",
        "epic_name": "Checkout & Bag Conversion",
        "title": "Transparent Delivery ETA & Upfront Tiered Promo Calculator in Bag",
        "problem_evidence": "Funnel diagnostics indicate a 34% drop-off between `add_to_cart` and `checkout_started`, corroborated by reviews citing surprise shipping timelines for Tier-2 cities and hidden promo inputs.",
        "user_story": "As a shopper reviewing my bag, I want to see instant free-shipping eligibility, city-tier delivery estimates, and one-click promo application before entering checkout.",
        "acceptance_criteria": [
            "Display free-shipping threshold progress bar (Complimentary Express Shipping over ₹5,000) inside Bag page.",
            "Provide interactive city selector with realistic Tier-1/Tier-2/Tier-3 delivery window estimates.",
            "Improve Bag-to-Checkout progression rate from 66% to >= 75%."
        ],
        "reach_score": 8200,
        "impact_score": 1.5,
        "confidence_pct": 85,
        "effort_person_weeks": 2.0,
        "customer_impact": "High",
        "business_impact": "-8.5% Cart Abandonment Rate",
        "status": "Next Sprint",
        "sprint": "Sprint 15",
        "owner": "Karthik Subramanian (PM - Checkout)",
    },
    {
        "id": "rm_007",
        "jira_key": "THRD-107",
        "epic_name": "Personalization & Cross-Sell",
        "title": "'Complete the Atelier Look' Cross-Category Outfit Pairing Engine",
        "problem_evidence": "Exploratory experiment `exp_editorial_lookbook_bundle` shows +11% AOV among Editorial Curators when complementary trousers/loafers are suggested alongside blazers, though current sample size requires expansion.",
        "user_story": "As a shopper buying a hero garment (such as a linen blazer), I want curated pairing recommendations across complementary categories (trousers, loafers, knit shells) so I can assemble a cohesive outfit.",
        "acceptance_criteria": [
            "Generate cross-category outfit recommendations on PDP based on shared `occasion` and complementary `subcategory`.",
            "Track `recommendation_clicked` and multi-item order attach rate.",
            "Scale experiment traffic to reach n=400 per arm before full rollout decision."
        ],
        "reach_score": 7400,
        "impact_score": 1.0,
        "confidence_pct": 70,
        "effort_person_weeks": 3.0,
        "customer_impact": "Medium",
        "business_impact": "+9% Multi-item units per order",
        "status": "Planned Q1",
        "sprint": "Sprint 16",
        "owner": "Ananya Rao (PM - Discovery)",
    },
    {
        "id": "rm_008",
        "jira_key": "THRD-108",
        "epic_name": "GenAI Product Operations",
        "title": "Automated Weekly Voice-of-Customer (VoC) & Return-Risk Digest",
        "problem_evidence": "Merchandising and PM teams previously spent 6 hours/week manually tagging spreadsheet reviews to spot high-return SKUs.",
        "user_story": "As a Product Manager, I want an automated LLM synthesis pipeline that clusters weekly customer reviews by complaint category and links every insight to verifiable review IDs.",
        "acceptance_criteria": [
            "Provide structured JSON output categorizing complaints across 7 taxonomy buckets with verbatim review citations.",
            "Include deterministic SQL fallback when external LLM API keys are unconfigured.",
            "Support one-click XLSX/CSV export for weekly merchandising standups."
        ],
        "reach_score": 4500,
        "impact_score": 1.5,
        "confidence_pct": 95,
        "effort_person_weeks": 1.5,
        "customer_impact": "High",
        "business_impact": "Saves 6 hrs/wk PM ops time; flags high-return SKUs 2 weeks earlier",
        "status": "Shipped",
        "sprint": "Sprint 13",
        "owner": "Ananya Rao (PM - Discovery)",
    },
]


def seed_database(db: Session) -> None:
    """Populate the database with a rich, logically consistent synthetic dataset if empty."""
    existing_products = db.query(Product).count()
    if existing_products > 0:
        return

    rng = random.Random(42)
    base_now = datetime(2026, 11, 15, 12, 0, 0)

    # 1. Seed Categories
    for cat in CATEGORIES_DATA:
        db.add(Category(**cat))
    db.flush()

    # 2. Seed Products
    products_by_id = {}
    for p in PRODUCTS_DATA:
        prod = Product(
            id=p["id"],
            sku=p["sku"],
            title=p["title"],
            subtitle=p["subtitle"],
            brand=p["brand"],
            category_id=p["category_id"],
            subcategory=p["subcategory"],
            price=p["price"],
            original_price=p["original_price"],
            discount_pct=p["discount_pct"],
            fabric=p["fabric"],
            fit_profile=p["fit_profile"],
            fit_notes=p["fit_notes"],
            description=p["description"],
            care_instructions=p["care_instructions"],
            occasion=p["occasion"],
            available_sizes_json=json.dumps(p["sizes"]),
            available_colors_json=json.dumps(p["colors"]),
            primary_color=p["primary_color"],
            image_url=p["image_url"],
            secondary_image_url=p["secondary_image_url"],
            rating_avg=4.3,
            review_count=4,
            popularity_score=p["popularity_score"],
            return_rate_pct=p["return_rate_pct"],
            is_featured=p["is_featured"],
            is_new_arrival=p["is_new_arrival"],
            stock_count=p["stock_count"],
            search_tags=p["search_tags"],
            created_at=base_now - timedelta(days=rng.randint(45, 120)),
        )
        db.add(prod)
        products_by_id[prod.id] = prod
    db.flush()

    # 3. Seed Users (180 users including 4 named demo personas at the top)
    demo_users = [
        User(
            id="usr_demo_001",
            email="ananya.rao@threadline-demo.in",
            full_name="Ananya Rao",
            persona_segment="Fit-Conscious Minimalist",
            preferred_size="S",
            acquisition_channel="editorial_newsletter",
            primary_device="desktop_web",
            city_tier="Metro Tier-1",
            cohort_month="2026-07",
            created_at=datetime(2026, 7, 12, 10, 15, 0),
        ),
        User(
            id="usr_demo_002",
            email="vikram.sethi@threadline-demo.in",
            full_name="Vikram Sethi",
            persona_segment="Editorial Curator",
            preferred_size="L",
            acquisition_channel="organic_search",
            primary_device="mobile_ios",
            city_tier="Metro Tier-1",
            cohort_month="2026-08",
            created_at=datetime(2026, 8, 5, 14, 30, 0),
        ),
        User(
            id="usr_demo_003",
            email="meera.kapoor@threadline-demo.in",
            full_name="Meera Kapoor",
            persona_segment="Occasion Explorer",
            preferred_size="M",
            acquisition_channel="paid_social_ig",
            primary_device="mobile_ios",
            city_tier="Tier-2 Growth",
            cohort_month="2026-09",
            created_at=datetime(2026, 9, 14, 19, 10, 0),
        ),
        User(
            id="usr_demo_004",
            email="kabir.deshmukh@threadline-demo.in",
            full_name="Kabir Deshmukh",
            persona_segment="Value Trend-Seeker",
            preferred_size="M",
            acquisition_channel="influencer_referral",
            primary_device="mobile_android",
            city_tier="Tier-2 Growth",
            cohort_month="2026-10",
            created_at=datetime(2026, 10, 3, 11, 45, 0),
        ),
    ]

    first_names = [
        "Aarav", "Aditi", "Arjun", "Avani", "Dev", "Diya", "Ishaan", "Kavya",
        "Kiran", "Maya", "Neha", "Nikhil", "Pooja", "Pranav", "Rhea", "Rohan",
        "Sanya", "Siddharth", "Tanvi", "Varun", "Zoya", "kriti", "Kabir", "Nandini"
    ]
    last_names = [
        "Sharma", "Verma", "Nair", "Iyer", "Menon", "Patel", "Kulkarni", "Joshi",
        "Malhotra", "Bhatia", "Chatterjee", "Sen", "Reddy", "Rao", "Kapoor", "Mehta"
    ]
    personas = [
        "Fit-Conscious Minimalist",
        "Occasion Explorer",
        "Value Trend-Seeker",
        "Editorial Curator",
    ]
    channels = [
        "organic_search",
        "paid_social_ig",
        "editorial_newsletter",
        "direct",
        "influencer_referral",
    ]
    devices = ["mobile_ios", "mobile_android", "desktop_web"]
    device_weights = [0.44, 0.34, 0.22]
    city_tiers = ["Metro Tier-1", "Tier-2 Growth", "Tier-3 Emerging"]
    cohort_months = ["2026-07", "2026-08", "2026-09", "2026-10", "2026-11"]
    cohort_weights = [0.18, 0.20, 0.22, 0.24, 0.16]
    sizes = ["XS", "S", "M", "L", "XL"]

    all_users = list(demo_users)
    for u in demo_users:
        db.add(u)

    for idx in range(5, 181):
        uid = f"usr_{idx:03d}"
        fname = rng.choice(first_names)
        lname = rng.choice(last_names)
        c_month = rng.choices(cohort_months, weights=cohort_weights, k=1)[0]
        year, month = map(int, c_month.split("-"))
        max_day = 14 if month == 11 else 28
        created_dt = datetime(year, month, rng.randint(1, max_day), rng.randint(8, 22), rng.randint(0, 59))
        user_obj = User(
            id=uid,
            email=f"{fname.lower()}.{lname.lower()}.{idx}@example-synthetic.in",
            full_name=f"{fname.capitalize()} {lname}",
            persona_segment=rng.choice(personas),
            preferred_size=rng.choice(sizes),
            acquisition_channel=rng.choice(channels),
            primary_device=rng.choices(devices, weights=device_weights, k=1)[0],
            city_tier=rng.choices(city_tiers, weights=[0.55, 0.32, 0.13], k=1)[0],
            cohort_month=c_month,
            created_at=created_dt,
        )
        db.add(user_obj)
        all_users.append(user_obj)
    db.flush()

    # 4. Seed Experiments first so sessions and searches can reference variants consistently
    exp_1 = Experiment(
        id="exp_001",
        key="exp_semantic_size_fit_filters",
        name="Semantic Search Expansion + Sticky 'In-My-Size & Fit Profile' Filter Bar",
        problem_statement="Customers struggle to find size-available items with predictable fit profiles and frequently hit zero-result pages when searching by occasion or fabric texture.",
        hypothesis="Introducing semantic query expansion and a sticky 'In-My-Size + Fit Guidance' filter ribbon on Search & Discovery will increase Search CTR and lift Search-to-Cart conversion by at least 15%.",
        primary_metric="add_to_cart_rate",
        secondary_metrics_json=json.dumps(["search_ctr", "product_view_rate", "purchase_conversion"]),
        control_description="Standard keyword matching on title/brand with collapsed sidebar filters and no fit badge on product cards.",
        treatment_description="Semantic synonym expansion (occasion/fabric) + persistent one-tap Size & Fit-Profile pills + verified buyer Fit Guidance badge on every product card.",
        status="running",
        traffic_allocation_pct=100,
        target_sample_size=180,
        start_date=base_now - timedelta(days=28),
        end_date=None,
        owner="Ananya Rao (PM - Discovery)",
    )
    exp_2 = Experiment(
        id="exp_002",
        key="exp_pdp_fit_predictor_widget",
        name="PDP Verified Buyer Fit Spectrum & Garment Measurement Callout",
        problem_statement="High PDP-to-Bag drop-off (41%) on tailored trousers, bias-cut dresses, and leather loafers due to uncertainty over whether items run small.",
        hypothesis="Surfacing aggregated verified-buyer fit consensus ('68% recommend sizing up') directly above the size selector will increase PDP Add-to-Cart rate and reduce size hesitation.",
        primary_metric="add_to_cart_rate",
        secondary_metrics_json=json.dumps(["purchase_conversion", "product_view_rate"]),
        control_description="Generic modal size table hidden behind a secondary text link.",
        treatment_description="Inline Verified Fit Spectrum bar + fabric stretch/GSM callout directly above size buttons.",
        status="completed",
        traffic_allocation_pct=100,
        target_sample_size=160,
        start_date=base_now - timedelta(days=52),
        end_date=base_now - timedelta(days=14),
        owner="Rohan Mehta (PM - PDP Experience)",
    )
    exp_3 = Experiment(
        id="exp_003",
        key="exp_editorial_lookbook_bundle",
        name="Post-Add-to-Bag 'Complete the Atelier Look' Styling Drawer",
        problem_statement="Single-item orders account for 64% of checkouts because shoppers rarely browse cross-category pairings after adding a hero garment.",
        hypothesis="Presenting 2 curated cross-category pairing items inside the slide-over bag drawer will increase multi-item attach rate and order conversion without increasing checkout drop-off.",
        primary_metric="purchase_conversion",
        secondary_metrics_json=json.dumps(["add_to_cart_rate", "average_order_value"]),
        control_description="Standard bag confirmation toast without styling recommendations.",
        treatment_description="Editorial 'Complete the Look' pairing module inside bag drawer showing complementary trouser/footwear SKU.",
        status="running",
        traffic_allocation_pct=50,
        target_sample_size=200,
        start_date=base_now - timedelta(days=9),
        end_date=None,
        owner="Ananya Rao (PM - Discovery)",
    )
    db.add_all([exp_1, exp_2, exp_3])
    db.flush()

    # 5. Seed Sessions, Searches, Events, Orders, and Experiment Assignments
    # Queries catalogue with realistic conversion & zero-result profiles
    active_queries = [
        ("linen blazer", "linen blazer", ["prd_001", "prd_010"], 8),
        ("linen shirt", "linen shirt", ["prd_003", "prd_009"], 11),
        ("wide leg trouser", "wide leg trouser", ["prd_002", "prd_011", "prd_020"], 9),
        ("occasion dress", "occasion dress", ["prd_005", "prd_006", "prd_007", "prd_008"], 12),
        ("silk midi dress", "silk midi dress", ["prd_005", "prd_007"], 6),
        ("merino cardigan", "merino cardigan", ["prd_013", "prd_015"], 7),
        ("leather loafers", "leather loafers", ["prd_021", "prd_023"], 6),
        ("selvedge denim", "selvedge denim", ["prd_017", "prd_019"], 8),
        ("leather tote bag", "leather tote bag", ["prd_022"], 5),
        ("pleated midi skirt", "pleated midi skirt", ["prd_014", "prd_006"], 5),
        ("oversized blazer", "oversized blazer", ["prd_001", "prd_010"], 7),
        ("chore jacket", "chore jacket", ["prd_018"], 4),
    ]
    zero_result_queries = [
        ("haldi guest outfit", "haldi guest outfit"),
        ("kurta set silk", "kurta set silk"),
        ("petite friendly maxi", "petite friendly maxi"),
        ("vegan suede tote", "vegan suede tote"),
        ("breathable summer office wear", "breathable summer office wear"),
    ]

    category_names = {c["id"]: c["name"] for c in CATEGORIES_DATA}
    product_list = list(products_by_id.values())

    session_counter = 0
    search_counter = 0
    event_counter = 0
    order_counter = 0
    order_item_counter = 0

    def add_event(
        ev_name: str,
        user: User,
        sess_id: str,
        ts: datetime,
        variant: str,
        prod: Product | None = None,
        extra_props: dict | None = None,
    ):
        nonlocal event_counter
        event_counter += 1
        cat_label = category_names.get(prod.category_id) if prod else None
        ev = EventRecord(
            id=f"evt_{event_counter:05d}",
            event_name=ev_name,
            user_id=user.id,
            session_id=sess_id,
            product_id=prod.id if prod else None,
            category=cat_label,
            price=prod.price if prod else None,
            brand=prod.brand if prod else None,
            device_type=user.primary_device,
            acquisition_channel=user.acquisition_channel,
            experiment_variant=variant,
            properties_json=json.dumps(extra_props or {}),
            mixpanel_dispatched=False,
            event_timestamp=ts,
        )
        db.add(ev)

    # Track user-level exposure & outcomes for Experiment 1 (all 180 users), Experiment 2 (160 users), Experiment 3 (94 users - exploratory!)
    exp1_map = {}

    for u_idx, user in enumerate(all_users):
        variant = "treatment" if u_idx % 2 == 1 else "control"
        # Determine number of sessions based on cohort age (for realistic retention curves)
        cohort_year, cohort_m = map(int, user.cohort_month.split("-"))
        months_since = (11 - cohort_m) + 1
        num_sessions = rng.randint(2, min(6, months_since + 2))

        user_searched = False
        user_clicked = False
        user_viewed_pdp = False
        user_added_cart = False
        user_ordered = False
        user_revenue = 0.0

        for s_i in range(num_sessions):
            session_counter += 1
            sess_id = f"sess_{session_counter:04d}"

            # Spread sessions across months from user creation to Nov 2026
            if s_i == 0:
                sess_start = user.created_at + timedelta(minutes=rng.randint(5, 180))
            else:
                days_after = rng.randint(7 * s_i, max(8 * s_i, (base_now - user.created_at).days))
                sess_start = min(base_now - timedelta(hours=rng.randint(1, 48)), user.created_at + timedelta(days=days_after))

            # Concentrate last session in the most recent 21 days for active users
            if s_i == num_sessions - 1 and rng.random() < 0.72:
                sess_start = base_now - timedelta(days=rng.randint(0, 20), hours=rng.randint(1, 20))

            sess_obj = SessionModel(
                id=sess_id,
                user_id=user.id,
                device_type=user.primary_device,
                acquisition_channel=user.acquisition_channel,
                experiment_variant=variant,
                started_at=sess_start,
                ended_at=sess_start,
                duration_seconds=30,
                converted=False,
            )
            db.add(sess_obj)
            db.flush()

            t_cursor = sess_start

            # Step 1: Homepage viewed (95% of sessions)
            if rng.random() < 0.96:
                add_event("homepage_viewed", user, sess_id, t_cursor, variant, extra_props={"page": "/"})
                t_cursor += timedelta(seconds=rng.randint(12, 45))

            # Step 2: Search submitted (76% of sessions)
            searched_this_session = rng.random() < 0.76
            clicked_prod = None
            last_search_rec = None

            if searched_this_session:
                user_searched = True
                search_counter += 1
                srch_id = f"srch_{search_counter:04d}"

                # In control, 18% hit zero-result queries; in treatment, semantic expansion reduces zero-result rate to 5%
                zero_prob = 0.18 if variant == "control" else 0.05
                is_zero = rng.random() < zero_prob

                if is_zero:
                    q_raw, q_norm = rng.choice(zero_result_queries)
                    res_count = 0
                    abandoned = True if rng.random() < 0.78 else False
                    clicked_id = None
                    click_pos = None
                else:
                    q_raw, q_norm, matching_ids, res_count = rng.choice(active_queries)
                    # CTR is higher in treatment (78% vs 58% in control)
                    ctr_prob = 0.78 if variant == "treatment" else 0.58
                    if rng.random() < ctr_prob:
                        clicked_id = rng.choice(matching_ids)
                        clicked_prod = products_by_id[clicked_id]
                        click_pos = rng.randint(1, min(4, len(matching_ids)))
                        abandoned = False
                        user_clicked = True
                    else:
                        clicked_id = None
                        click_pos = None
                        abandoned = True

                applied_filters = {"size": user.preferred_size} if (variant == "treatment" and rng.random() < 0.65) else {}
                add_event(
                    "search_submitted",
                    user,
                    sess_id,
                    t_cursor,
                    variant,
                    extra_props={"query": q_raw, "results_count": res_count, "filters": applied_filters},
                )
                t_cursor += timedelta(seconds=rng.randint(8, 25))

                if applied_filters:
                    add_event(
                        "filter_applied",
                        user,
                        sess_id,
                        t_cursor,
                        variant,
                        extra_props={"filter_type": "size_and_fit", "value": user.preferred_size},
                    )
                    t_cursor += timedelta(seconds=rng.randint(5, 15))

                if clicked_prod:
                    add_event(
                        "search_result_clicked",
                        user,
                        sess_id,
                        t_cursor,
                        variant,
                        prod=clicked_prod,
                        extra_props={"query": q_raw, "position": click_pos},
                    )
                    t_cursor += timedelta(seconds=rng.randint(6, 20))

                last_search_rec = SearchRecord(
                    id=srch_id,
                    session_id=sess_id,
                    user_id=user.id,
                    query_text=q_raw,
                    normalized_query=q_norm,
                    filters_json=json.dumps(applied_filters),
                    results_count=res_count,
                    clicked_product_id=clicked_id,
                    click_position=click_pos,
                    converted_to_bag=False,
                    converted_to_order=False,
                    search_abandoned=abandoned,
                    experiment_variant=variant,
                    created_at=t_cursor,
                )
                db.add(last_search_rec)
                db.flush()

            # Step 4: Product viewed (either from search click or category/editorial browse)
            pdp_prod = clicked_prod
            if not pdp_prod and rng.random() < 0.42:
                pdp_prod = rng.choice(product_list)

            session_converted = False
            if pdp_prod:
                user_viewed_pdp = True
                add_event(
                    "product_viewed",
                    user,
                    sess_id,
                    t_cursor,
                    variant,
                    prod=pdp_prod,
                    extra_props={"fit_profile": pdp_prod.fit_profile},
                )
                t_cursor += timedelta(seconds=rng.randint(25, 95))

                # Step 5: Wishlist added (28% of PDP viewers)
                if rng.random() < 0.28:
                    add_event("wishlist_added", user, sess_id, t_cursor, variant, prod=pdp_prod)
                    t_cursor += timedelta(seconds=rng.randint(10, 30))

                # Step 6: Add to cart (Treatment has higher PDP-to-Bag conversion: 48% vs 33% in control)
                atc_prob = 0.48 if variant == "treatment" else 0.33
                if rng.random() < atc_prob:
                    user_added_cart = True
                    if last_search_rec:
                        last_search_rec.converted_to_bag = True
                    add_event(
                        "add_to_cart",
                        user,
                        sess_id,
                        t_cursor,
                        variant,
                        prod=pdp_prod,
                        extra_props={"size": user.preferred_size, "color": pdp_prod.primary_color},
                    )
                    t_cursor += timedelta(seconds=rng.randint(20, 60))

                    # Step 7: Checkout started (67% of Add-to-Cart sessions)
                    if rng.random() < 0.67:
                        add_event("checkout_started", user, sess_id, t_cursor, variant, prod=pdp_prod)
                        t_cursor += timedelta(seconds=rng.randint(30, 90))

                        # Step 8: Order placed (74% of Checkout started sessions)
                        if rng.random() < 0.74:
                            session_converted = True
                            user_ordered = True
                            if last_search_rec:
                                last_search_rec.converted_to_order = True

                            order_counter += 1
                            ord_id = f"ord_{order_counter:04d}"
                            ord_num = f"TL-2026-{1000 + order_counter}"

                            # Optionally add a second item (28% of orders)
                            second_prod = rng.choice(product_list) if rng.random() < 0.28 else None
                            subtotal = pdp_prod.price + (second_prod.price if second_prod else 0.0)
                            shipping = 0.0 if subtotal >= 5000 else 250.0
                            discount_amt = round(subtotal * 0.05, 2) if subtotal >= 8000 else 0.0
                            total_amt = round(subtotal - discount_amt + shipping, 2)
                            user_revenue += total_amt

                            order_status = "returned" if rng.random() < (pdp_prod.return_rate_pct / 100.0) else "delivered"
                            order_obj = Order(
                                id=ord_id,
                                order_number=ord_num,
                                user_id=user.id,
                                session_id=sess_id,
                                status=order_status,
                                subtotal=subtotal,
                                discount_amount=discount_amt,
                                shipping_fee=shipping,
                                total_amount=total_amt,
                                payment_method=rng.choice(["UPI / Instant Bank Transfer", "Credit Card (Visa/Mastercard)", "NetBanking"]),
                                shipping_city=rng.choice(["Bengaluru, KA", "Mumbai, MH", "New Delhi, DL", "Hyderabad, TS", "Pune, MH", "Jaipur, RJ", "Chennai, TN"]),
                                attribution_search_id=last_search_rec.id if last_search_rec else None,
                                experiment_variant=variant,
                                created_at=t_cursor,
                            )
                            db.add(order_obj)
                            db.flush()

                            order_item_counter += 1
                            db.add(
                                OrderItem(
                                    id=f"oi_{order_item_counter:04d}",
                                    order_id=ord_id,
                                    product_id=pdp_prod.id,
                                    selected_size=user.preferred_size,
                                    selected_color=pdp_prod.primary_color,
                                    quantity=1,
                                    unit_price=pdp_prod.price,
                                )
                            )
                            if second_prod:
                                order_item_counter += 1
                                db.add(
                                    OrderItem(
                                        id=f"oi_{order_item_counter:04d}",
                                        order_id=ord_id,
                                        product_id=second_prod.id,
                                        selected_size=user.preferred_size,
                                        selected_color=second_prod.primary_color,
                                        quantity=1,
                                        unit_price=second_prod.price,
                                    )
                                )

                            add_event(
                                "order_placed",
                                user,
                                sess_id,
                                t_cursor,
                                variant,
                                prod=pdp_prod,
                                extra_props={"order_id": ord_id, "order_number": ord_num, "total_amount": total_amt},
                            )
                            t_cursor += timedelta(seconds=rng.randint(10, 25))

            duration_sec = max(18, int((t_cursor - sess_start).total_seconds()))
            sess_obj.ended_at = t_cursor
            sess_obj.duration_seconds = duration_sec
            sess_obj.converted = session_converted

        # Record Experiment 1 Assignment for this user
        exp1_map[user.id] = ExperimentAssignment(
            id=f"ea_exp1_{u_idx + 1:03d}",
            experiment_id="exp_001",
            user_id=user.id,
            session_id=f"sess_{session_counter:04d}",
            variant=variant,
            exposed_at=user.created_at + timedelta(days=1),
            search_submitted=user_searched,
            search_clicked=user_clicked,
            product_viewed=user_viewed_pdp,
            added_to_cart=user_added_cart,
            order_completed=user_ordered,
            order_revenue=round(user_revenue, 2),
        )
        db.add(exp1_map[user.id])

        # Record Experiment 2 Assignment (first 160 users, completed experiment with statistically significant PDP->Bag lift)
        if u_idx < 160:
            v2 = "treatment" if (u_idx % 2 == 0) else "control"
            pdp_v = True
            atc_v2 = (rng.random() < 0.44) if v2 == "treatment" else (rng.random() < 0.28)
            ord_v2 = atc_v2 and (rng.random() < 0.52)
            db.add(
                ExperimentAssignment(
                    id=f"ea_exp2_{u_idx + 1:03d}",
                    experiment_id="exp_002",
                    user_id=user.id,
                    session_id=None,
                    variant=v2,
                    exposed_at=base_now - timedelta(days=rng.randint(15, 50)),
                    search_submitted=True,
                    search_clicked=True,
                    product_viewed=pdp_v,
                    added_to_cart=atc_v2,
                    order_completed=ord_v2,
                    order_revenue=5890.0 if ord_v2 else 0.0,
                )
            )

        # Record Experiment 3 Assignment (only 94 users exposed so far, under-powered / exploratory!)
        if u_idx < 94:
            v3 = "treatment" if (u_idx % 2 == 1) else "control"
            atc_v3 = (rng.random() < 0.36) if v3 == "treatment" else (rng.random() < 0.32)
            ord_v3 = atc_v3 and ((rng.random() < 0.46) if v3 == "treatment" else (rng.random() < 0.41))
            db.add(
                ExperimentAssignment(
                    id=f"ea_exp3_{u_idx + 1:03d}",
                    experiment_id="exp_003",
                    user_id=user.id,
                    session_id=None,
                    variant=v3,
                    exposed_at=base_now - timedelta(days=rng.randint(1, 8)),
                    search_submitted=True,
                    search_clicked=True,
                    product_viewed=True,
                    added_to_cart=atc_v3,
                    order_completed=ord_v3,
                    order_revenue=8490.0 if ord_v3 else 0.0,
                )
            )

    db.flush()

    # 6. Seed 96 Customer Reviews (expanding from the 20 rich templates + product coverage across all 24 SKUs)
    review_counter = 0
    for idx in range(96):
        review_counter += 1
        tmpl = REVIEW_TEMPLATES[idx % len(REVIEW_TEMPLATES)]
        # Ensure all 24 products have reviews while keeping complaint templates anchored to their exact SKUs for the first 60
        if idx < 60:
            target_prod_id = tmpl["product_id"]
        else:
            target_prod_id = f"prd_{(idx % 24) + 1:03d}"

        prod_obj = products_by_id[target_prod_id]
        reviewer = all_users[idx % len(all_users)]
        rev_dt = base_now - timedelta(days=rng.randint(1, 75), hours=rng.randint(1, 23))

        # Slight variation marker for repeated template rows so every review record is distinct and traceable
        suffix = "" if idx < len(REVIEW_TEMPLATES) else f" (Verified Order Batch #{idx + 101} — Size {reviewer.preferred_size})"
        rev = Review(
            id=f"rev_{review_counter:03d}",
            product_id=prod_obj.id,
            user_id=reviewer.id,
            order_id=None,
            rating=tmpl["rating"],
            title=tmpl["title"],
            comment_text=tmpl["comment_text"] + suffix,
            sentiment=tmpl["sentiment"],
            complaint_category=tmpl["complaint_category"],
            fit_feedback=tmpl["fit_feedback"],
            verified_purchase=True,
            helpful_votes=rng.randint(2, 34),
            created_at=rev_dt,
        )
        db.add(rev)

    db.flush()

    # Recompute accurate rating_avg and review_count on each product
    for prod_obj in product_list:
        prod_reviews = db.query(Review).filter(Review.product_id == prod_obj.id).all()
        if prod_reviews:
            prod_obj.review_count = len(prod_reviews)
            prod_obj.rating_avg = round(sum(r.rating for r in prod_reviews) / len(prod_reviews), 2)

    # 7. Seed Demo User's Initial Shopping Bag & Wishlist so the storefront is immediately alive
    db.add_all(
        [
            CartItem(
                id="crt_init_001",
                user_id="usr_demo_001",
                session_id="sess_0001",
                product_id="prd_001",
                selected_size="S",
                selected_color="Oatmeal Melange",
                quantity=1,
                item_type="bag",
                created_at=base_now - timedelta(hours=2),
            ),
            CartItem(
                id="crt_init_002",
                user_id="usr_demo_001",
                session_id="sess_0001",
                product_id="prd_013",
                selected_size="S",
                selected_color="Claret Burgundy",
                quantity=1,
                item_type="bag",
                created_at=base_now - timedelta(hours=1),
            ),
            CartItem(
                id="crt_init_003",
                user_id="usr_demo_001",
                session_id="sess_0001",
                product_id="prd_005",
                selected_size="M",
                selected_color="Oxblood Burgundy",
                quantity=1,
                item_type="wishlist",
                created_at=base_now - timedelta(days=1),
            ),
            CartItem(
                id="crt_init_004",
                user_id="usr_demo_001",
                session_id="sess_0001",
                product_id="prd_022",
                selected_size="M",
                selected_color="Cognac Tan",
                quantity=1,
                item_type="wishlist",
                created_at=base_now - timedelta(days=2),
            ),
        ]
    )

    # 8. Seed Roadmap Items with RICE Scores
    for rm in ROADMAP_ITEMS_DATA:
        rice_val = round(
            (rm["reach_score"] * rm["impact_score"] * (rm["confidence_pct"] / 100.0)) / rm["effort_person_weeks"],
            1,
        )
        db.add(
            RoadmapItem(
                id=rm["id"],
                jira_key=rm["jira_key"],
                epic_name=rm["epic_name"],
                title=rm["title"],
                problem_evidence=rm["problem_evidence"],
                user_story=rm["user_story"],
                acceptance_criteria_json=json.dumps(rm["acceptance_criteria"]),
                reach_score=rm["reach_score"],
                impact_score=rm["impact_score"],
                confidence_pct=rm["confidence_pct"],
                effort_person_weeks=rm["effort_person_weeks"],
                rice_score=rice_val,
                customer_impact=rm["customer_impact"],
                business_impact=rm["business_impact"],
                status=rm["status"],
                sprint=rm["sprint"],
                owner=rm["owner"],
            )
        )

    db.commit()
