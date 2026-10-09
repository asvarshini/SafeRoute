import os
import re
import json
from datetime import date, datetime
from typing import Any, Optional

import requests
import serpapi

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import (
    create_tables,
    save_hotel,
    get_hotel_id,
    get_connection,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

if not SERPAPI_API_KEY:
    print("WARNING: SERPAPI_API_KEY is not configured.")


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="SafeRoute API",
    description=(
        "Travel planning backend using SerpApi hotel, hotel review, "
        "and travel news data together with Open-Meteo weather data."
    ),
    version="1.1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

create_tables()


# ============================================================
# SERPAPI CLIENT
# ============================================================

serp_client = None

if SERPAPI_API_KEY:
    serp_client = serpapi.Client(
        api_key=SERPAPI_API_KEY
    )


# ============================================================
# CONSTANTS
# ============================================================

# Review text is more expensive than using the structured
# reviews_breakdown already returned by Google Hotels.
#
# Therefore:
#
# - reviews_breakdown can help ALL returned hotels.
# - detailed review text is retrieved only for the first
#   six hotels.
#
# This gives broader coverage without multiplying API calls
# unnecessarily.

MAX_HOTELS_WITH_REVIEW_ANALYSIS = 6

MAX_TRAVEL_NEWS = 10


# ============================================================
# REQUEST MODELS
# ============================================================

class PlanRequest(BaseModel):
    origin: str = Field(
        min_length=1,
        max_length=200,
    )

    destination: str = Field(
        min_length=1,
        max_length=200,
    )

    budget: int = Field(
        gt=0,
    )

    travelers: int = Field(
        gt=0,
        le=50,
    )

    start_date: str

    end_date: str


class CommunityReviewRequest(BaseModel):
    hotel_id: int = Field(
        gt=0,
    )

    rating: int = Field(
        ge=1,
        le=5,
    )

    category: str = Field(
        min_length=1,
        max_length=100,
    )

    experience: str = Field(
        min_length=5,
        max_length=2000,
    )


class SafetyReportRequest(BaseModel):
    hotel_name: str = Field(
        min_length=1,
        max_length=200,
    )

    report_type: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str = Field(
        min_length=5,
        max_length=2000,
    )


# ============================================================
# BASIC HELPERS
# ============================================================

def require_serpapi():
    if not SERPAPI_API_KEY or serp_client is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "SerpApi is not configured. "
                "Add SERPAPI_API_KEY to the backend .env file."
            ),
        )


def safe_float(
    value: Any,
    default: Optional[float] = None,
):
    try:
        if value is None:
            return default

        if isinstance(value, bool):
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def safe_int(
    value: Any,
    default: Optional[int] = None,
):
    try:
        if value is None:
            return default

        if isinstance(value, bool):
            return default

        return int(value)

    except (TypeError, ValueError):
        return default


def parse_price(
    value: Any,
) -> Optional[int]:
    """
    Converts values such as:

        2500
        "₹2,500"
        "$120"
        "2,500"

    into an integer.

    Missing price remains None.
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):

        if value <= 0:
            return None

        return int(round(value))

    text = str(value).strip()

    if not text:
        return None

    cleaned = re.sub(
        r"[^\d.]",
        "",
        text,
    )

    if not cleaned:
        return None

    try:
        number = float(cleaned)

        if number <= 0:
            return None

        return int(round(number))

    except ValueError:
        return None


def parse_date(
    value: str,
) -> date:

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid date '{value}'. "
                "Use YYYY-MM-DD format."
            ),
        )


def clean_text(
    value: Any,
) -> str:

    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value),
    ).strip()


def clamp(
    value: float,
    minimum: float,
    maximum: float,
):
    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


# ============================================================
# SERPAPI SEARCH HELPER
# ============================================================

def serpapi_search(
    params: dict,
):
    """
    Centralized SerpApi request helper.
    """

    require_serpapi()

    try:

        results = serp_client.search(
            params
        )

        if results is None:

            raise HTTPException(
                status_code=502,
                detail=(
                    "SerpApi returned no response."
                ),
            )

        if isinstance(
            results,
            dict,
        ):

            if results.get("error"):

                raise HTTPException(
                    status_code=502,
                    detail=(
                        f"SerpApi error: "
                        f"{results['error']}"
                    ),
                )

        return results

    except HTTPException:
        raise

    except Exception as exc:

        print(
            "SerpApi request error:",
            repr(exc),
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to retrieve travel data "
                "from the external search service."
            ),
        )


# ============================================================
# REVIEW KEYWORDS
# ============================================================

HYGIENE_POSITIVE = [
    "clean",
    "cleanliness",
    "hygiene",
    "hygienic",
    "spotless",
    "tidy",
    "sanitized",
    "sanitary",
    "fresh",
    "well maintained",
    "well-maintained",
    "clean room",
    "clean rooms",
    "clean bathroom",
    "clean bathrooms",
]

HYGIENE_NEGATIVE = [
    "dirty",
    "unclean",
    "hygiene issue",
    "hygiene problem",
    "filthy",
    "bad smell",
    "smell",
    "stained",
    "unclean bathroom",
    "dirty bathroom",
    "dirty room",
    "dirty rooms",
    "poor cleanliness",
    "poor hygiene",
    "mold",
    "mould",
]

SAFETY_POSITIVE = [
    "safe",
    "secure",
    "female friendly",
    "women friendly",
    "women-friendly",
    "solo female",
    "female solo",
    "well lit",
    "well-lit",
    "security guard",
    "cctv",
    "security camera",
    "good security",
    "secure access",
    "safe area",
    "safe location",
]

SAFETY_NEGATIVE = [
    "unsafe",
    "not safe",
    "security issue",
    "security problem",
    "poor security",
    "harassment",
    "stalking",
    "theft",
    "stolen",
    "robbery",
    "dark area",
    "isolated",
    "unsafe area",
    "unsafe location",
    "security concern",
]


# ============================================================
# REVIEW BREAKDOWN CATEGORY NAMES
# ============================================================

# Google Hotels categories can differ between properties.
#
# SerpApi examples include categories such as:
# "Cleanliness", "Property", "Service", etc.
#
# We therefore search multiple possible names.

HYGIENE_CATEGORY_NAMES = [
    "cleanliness",
    "hygiene",
    "sanitary",
    "sanitation",
    "housekeeping",
    "bathroom",
    "bathrooms",
]

SAFETY_CATEGORY_NAMES = [
    "safety",
    "security",
]


# ============================================================
# KEYWORD MATCHING
# ============================================================

def phrase_matches(
    text: str,
    phrase: str,
) -> bool:
    """
    Whole-word / whole-phrase matching.

    This prevents:

        safe -> unsafe

    from being considered a match.
    """

    text = clean_text(
        text
    ).lower()

    phrase = clean_text(
        phrase
    ).lower()

    if not text or not phrase:
        return False

    pattern = (
        r"(?<!\w)"
        + re.escape(phrase)
        + r"(?!\w)"
    )

    return (
        re.search(
            pattern,
            text,
        )
        is not None
    )


def matched_keywords(
    text: str,
    keywords: list[str],
) -> list[str]:

    matches = []

    for keyword in keywords:

        if phrase_matches(
            text,
            keyword,
        ):

            matches.append(
                keyword
            )

    return matches


# ============================================================
# EVIDENCE ITEM BUILDER
# ============================================================

def make_review_excerpt(text: str, max_length: int = 180) -> str:
    """Return a short, readable excerpt from a review."""

    text = clean_text(text)

    if not text:
        return ""

    # Prefer the first sentence when it is reasonably short.
    first_sentence = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0].strip()

    if 20 <= len(first_sentence) <= max_length:
        return first_sentence

    if len(text) <= max_length:
        return text

    return text[:max_length - 1].rstrip() + "…"


def build_evidence_items(
    positive_counts: dict[str, int],
    negative_counts: dict[str, int],
    total_reviews: int,
    positive_label: str,
    negative_label: str,
    positive_examples: Optional[dict[str, list[dict]]] = None,
    negative_examples: Optional[dict[str, list[dict]]] = None,
):

    positive = []
    negative = []

    positive_examples = positive_examples or {}
    negative_examples = negative_examples or {}

    if total_reviews <= 0:
        return positive, negative

    for keyword, count in positive_counts.items():

        if count <= 0:
            continue

        percentage = round((count / total_reviews) * 100)

        positive.append({
            "point": f"{positive_label}: {keyword}",
            "keyword": keyword,
            "mentions": count,
            "percentage": percentage,
            "examples": positive_examples.get(keyword, []),
        })

    for keyword, count in negative_counts.items():

        if count <= 0:
            continue

        percentage = round((count / total_reviews) * 100)

        negative.append({
            "point": f"{negative_label}: {keyword}",
            "keyword": keyword,
            "mentions": count,
            "percentage": percentage,
            "examples": negative_examples.get(keyword, []),
        })

    return positive, negative


# ============================================================
# TEXT REVIEW ANALYSIS
# ============================================================

def analyze_reviews(
    reviews: list[dict],
    category: str,
):
    """
    Analyzes actual review text.

    Supporting evidence is retained as short excerpts so the
    frontend can show why a category was classified as positive
    or a reported concern.

    This is deliberately NOT presented as an objective
    measurement of safety or hygiene.
    """

    total_reviews = len(reviews)

    if category == "hygiene":
        positive_keywords = HYGIENE_POSITIVE
        negative_keywords = HYGIENE_NEGATIVE
        positive_label = "Positive hygiene evidence"
        negative_label = "Reported hygiene concern"
    else:
        positive_keywords = SAFETY_POSITIVE
        negative_keywords = SAFETY_NEGATIVE
        positive_label = "Positive safety evidence"
        negative_label = "Reported safety concern"

    if total_reviews == 0:
        return {
            "score": None,
            "insufficient_data": True,
            "positive": [],
            "negative": [],
            "review_count": 0,
            "evidence_review_count": 0,
        }

    positive_counts = {}
    negative_counts = {}
    positive_examples = {}
    negative_examples = {}

    score = 5.0
    evidence_review_count = 0

    for review in reviews:

        if not isinstance(review, dict):
            continue

        text = clean_text(
            review.get("text")
            or review.get("snippet")
            or review.get("content")
            or review.get("title")
        )

        if not text:
            continue

        negative_matches = matched_keywords(text, negative_keywords)
        positive_matches = matched_keywords(text, positive_keywords)

        review_date = clean_text(
            review.get("date")
            or review.get("published_date")
            or review.get("iso_date")
        )

        # Negative evidence gets priority so a review saying
        # "not safe" does not also become positive evidence.
        if negative_matches:

            evidence_review_count += 1
            score -= 1.0

            for keyword in negative_matches:
                negative_counts[keyword] = negative_counts.get(keyword, 0) + 1

                examples = negative_examples.setdefault(keyword, [])
                if len(examples) < 2:
                    example = {
                        "text": make_review_excerpt(text),
                    }
                    if review_date:
                        example["date"] = review_date
                    examples.append(example)

        elif positive_matches:

            evidence_review_count += 1
            score += 0.7

            for keyword in positive_matches:
                positive_counts[keyword] = positive_counts.get(keyword, 0) + 1

                examples = positive_examples.setdefault(keyword, [])
                if len(examples) < 2:
                    example = {
                        "text": make_review_excerpt(text),
                    }
                    if review_date:
                        example["date"] = review_date
                    examples.append(example)

    if evidence_review_count == 0:
        return {
            "score": None,
            "insufficient_data": True,
            "positive": [],
            "negative": [],
            "review_count": total_reviews,
            "evidence_review_count": 0,
        }

    score = round(clamp(score, 0.0, 10.0), 1)

    positive, negative = build_evidence_items(
        positive_counts,
        negative_counts,
        total_reviews,
        positive_label,
        negative_label,
        positive_examples,
        negative_examples,
    )

    return {
        "score": score,
        "insufficient_data": False,
        "positive": positive,
        "negative": negative,
        "review_count": total_reviews,
        "evidence_review_count": evidence_review_count,
    }


# ============================================================
# FIND REVIEW BREAKDOWN CATEGORY
# ============================================================

def find_review_breakdown_category(
    breakdown: list[dict],
    category_names: list[str],
):
    """
    Finds the best matching category from SerpApi's
    reviews_breakdown response.
    """

    if not isinstance(
        breakdown,
        list,
    ):
        return None

    candidates = []

    for item in breakdown:

        if not isinstance(
            item,
            dict,
        ):
            continue

        name = clean_text(
            item.get("name")
        ).lower()

        description = clean_text(
            item.get("description")
        ).lower()

        total_mentioned = safe_int(
            item.get(
                "total_mentioned"
            ),
            0,
        )

        if total_mentioned <= 0:
            continue

        for target in category_names:

            target = target.lower()

            # Exact name.
            if name == target:

                candidates.append(
                    (
                        3,
                        total_mentioned,
                        item,
                    )
                )

                continue

            # Name contains target.
            if target in name:

                candidates.append(
                    (
                        2,
                        total_mentioned,
                        item,
                    )
                )

                continue

            # Description contains target.
            if target in description:

                candidates.append(
                    (
                        1,
                        total_mentioned,
                        item,
                    )
                )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True,
    )

    return candidates[0][2]


# ============================================================
# STRUCTURED REVIEW BREAKDOWN ANALYSIS
# ============================================================

def analyze_review_breakdown(
    breakdown: list[dict],
    category: str,
):
    """
    Converts SerpApi's structured review breakdown into
    a transparent 0-10 category signal.

    This is NOT a guarantee.

    Positive = 10
    Neutral = 5
    Negative = 0

    We also use a confidence adjustment so that a category
    mentioned only a few times does not immediately become
    an extreme 0 or 10.
    """

    if category == "hygiene":

        category_names = (
            HYGIENE_CATEGORY_NAMES
        )

        label = (
            "Hygiene review category"
        )

    else:

        category_names = (
            SAFETY_CATEGORY_NAMES
        )

        label = (
            "Safety review category"
        )

    matched = find_review_breakdown_category(
        breakdown,
        category_names,
    )

    if not matched:

        return {
            "score": None,
            "insufficient_data": True,
            "positive": [],
            "negative": [],
            "review_count": 0,
            "evidence_review_count": 0,
            "source": (
                "Google Hotels reviews breakdown"
            ),
            "category": None,
        }

    total = safe_int(
        matched.get(
            "total_mentioned"
        ),
        0,
    )

    positive = safe_int(
        matched.get(
            "positive"
        ),
        0,
    )

    negative = safe_int(
        matched.get(
            "negative"
        ),
        0,
    )

    neutral = safe_int(
        matched.get(
            "neutral"
        ),
        0,
    )

    if total <= 0:

        return {
            "score": None,
            "insufficient_data": True,
            "positive": [],
            "negative": [],
            "review_count": 0,
            "evidence_review_count": 0,
            "source": (
                "Google Hotels reviews breakdown"
            ),
            "category": clean_text(
                matched.get("name")
            ),
        }

    positive = max(
        0,
        min(
            positive,
            total,
        ),
    )

    negative = max(
        0,
        min(
            negative,
            total,
        ),
    )

    neutral = max(
        0,
        min(
            neutral,
            total,
        ),
    )

    counted = (
        positive
        + negative
        + neutral
    )

    if counted <= 0:

        return {
            "score": None,
            "insufficient_data": True,
            "positive": [],
            "negative": [],
            "review_count": total,
            "evidence_review_count": 0,
            "source": (
                "Google Hotels reviews breakdown"
            ),
            "category": clean_text(
                matched.get("name")
            ),
        }

    raw_score = (
        (
            positive * 10
            + neutral * 5
            + negative * 0
        )
        / counted
    )

    # Confidence adjustment.
    #
    # 1 mention should not immediately become 10/10.
    #
    # More category mentions increase confidence.

    confidence_weight = (
        counted
        / (
            counted + 5
        )
    )

    score = (
        raw_score
        * confidence_weight
        + 5.0
        * (
            1
            - confidence_weight
        )
    )

    score = round(
        clamp(
            score,
            0.0,
            10.0,
        ),
        1,
    )

    category_name = clean_text(
        matched.get("name")
        or matched.get("description")
        or "Relevant category"
    )

    positive_items = []
    negative_items = []

    if positive > 0:

        positive_items.append({
            "point": (
                f"{label}: "
                f"{category_name} "
                "was mentioned positively"
            ),
            "keyword": category_name,
            "mentions": positive,
            "percentage": round(
                (
                    positive
                    / counted
                )
                * 100
            ),
        })

    if negative > 0:

        negative_items.append({
            "point": (
                f"{label}: "
                f"{category_name} "
                "was mentioned negatively"
            ),
            "keyword": category_name,
            "mentions": negative,
            "percentage": round(
                (
                    negative
                    / counted
                )
                * 100
            ),
        })

    return {
        "score": score,

        "insufficient_data": False,

        "positive": positive_items,

        "negative": negative_items,

        "review_count": total,

        "evidence_review_count": counted,

        "source": (
            "Google Hotels reviews breakdown "
            "via SerpApi"
        ),

        "category": category_name,

        "category_token": matched.get(
            "category_token"
        ),

        "breakdown": {
            "total_mentioned": total,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
        },
    }


# ============================================================
# MERGE STRUCTURED + TEXT REVIEW ANALYSIS
# ============================================================

def attach_text_examples(
    items: list[dict],
    text_items: list[dict],
) -> list[dict]:
    """Attach short review excerpts to structured category evidence."""

    if not items or not text_items:
        return items

    combined_examples = []

    for text_item in text_items:
        for example in text_item.get("examples", []) or []:
            if example not in combined_examples:
                combined_examples.append(example)
            if len(combined_examples) >= 3:
                break
        if len(combined_examples) >= 3:
            break

    if not combined_examples:
        return items

    updated = []
    for item in items:
        copy = dict(item)
        copy["examples"] = combined_examples[:3]
        updated.append(copy)

    return updated


def merge_review_analyses(
    breakdown_analysis: dict,
    text_analysis: dict,
):
    """
    Structured review-breakdown information is preferred for the
    score. Review text is retained as supporting evidence,
    including short excerpts when available.
    """

    breakdown_has_data = (
        breakdown_analysis
        and not breakdown_analysis.get("insufficient_data", True)
        and breakdown_analysis.get("score") is not None
    )

    text_has_data = (
        text_analysis
        and not text_analysis.get("insufficient_data", True)
        and text_analysis.get("score") is not None
    )

    if breakdown_has_data:
        result = dict(breakdown_analysis)

        if text_has_data:
            result["positive"] = attach_text_examples(
                result.get("positive", []),
                text_analysis.get("positive", []),
            )
            result["negative"] = attach_text_examples(
                result.get("negative", []),
                text_analysis.get("negative", []),
            )

            result["text_evidence"] = {
                "score": text_analysis.get("score"),
                "positive": text_analysis.get("positive", []),
                "negative": text_analysis.get("negative", []),
                "review_count": text_analysis.get("review_count", 0),
                "evidence_review_count": text_analysis.get(
                    "evidence_review_count", 0
                ),
            }

        return result

    if text_has_data:
        result = dict(text_analysis)
        result["source"] = "Google Hotels Reviews text via SerpApi"
        return result

    return {
        "score": None,
        "insufficient_data": True,
        "positive": [],
        "negative": [],
        "review_count": 0,
        "evidence_review_count": 0,
        "source": "Google Hotels Reviews via SerpApi",
    }


# ============================================================
# GOOGLE HOTELS REVIEWS
# ============================================================

def get_hotel_reviews(
    property_token: str,
    category_token: Optional[str] = None,
):
    """
    Retrieves Google Hotels reviews.

    category_token is optional.

    If supplied, SerpApi returns reviews associated
    with that category.

    Most recent reviews are requested.
    """

    if not property_token:
        return []

    params = {
        "engine": "google_hotels_reviews",

        "property_token": property_token,

        "hl": "en",

        "sort_by": 2,
    }

    if category_token:

        params["category_token"] = (
            category_token
        )

    results = serpapi_search(
        params
    )

    reviews = results.get(
        "reviews",
        [],
    )

    if not isinstance(
        reviews,
        list,
    ):
        return []

    return reviews


# ============================================================
# HOTEL PRICE EXTRACTION
# ============================================================

def extract_hotel_nightly_price(hotel: dict) -> Optional[int]:
    """
    Extract the actual lowest nightly price from the Google Hotels
    property response. Never invents a price and never converts a
    missing price into zero.
    """

    candidates = []

    rate_per_night = hotel.get("rate_per_night")
    if isinstance(rate_per_night, dict):
        candidates.extend([
            rate_per_night.get("extracted_lowest"),
            rate_per_night.get("lowest"),
            rate_per_night.get("extracted_before_taxes_fees"),
        ])

    # Some Google Hotels responses also expose individual rate sources
    # under prices[]. Use those only as a fallback.
    prices = hotel.get("prices")
    if isinstance(prices, list):
        for source in prices:
            if not isinstance(source, dict):
                continue
            source_rate = source.get("rate_per_night")
            if not isinstance(source_rate, dict):
                continue
            candidates.extend([
                source_rate.get("extracted_lowest"),
                source_rate.get("lowest"),
                source_rate.get("extracted_before_taxes_fees"),
            ])

    # Keep the legacy field only as a final fallback.
    candidates.append(hotel.get("price"))

    parsed = []
    for candidate in candidates:
        value = parse_price(candidate)
        if value is not None:
            parsed.append(value)

    return min(parsed) if parsed else None


# ============================================================
# HOTEL SEARCH
# ============================================================

def search_hotels(
    destination: str,
    start_date: str,
    end_date: str,
    travelers: int,
    budget: int,
):
    results = serpapi_search({
        "engine": "google_hotels",

        "q": destination,

        "check_in_date": start_date,

        "check_out_date": end_date,

        "adults": travelers,

        # Ask Google Hotels to prioritize lower-priced properties.
        # We still preserve the actual returned price for each hotel.
        "sort_by": 3,

        "currency": "INR",

        "gl": "in",

        "hl": "en",
    })

    properties = results.get(
        "properties",
        [],
    )

    if not isinstance(
        properties,
        list,
    ):
        properties = []

    hotels = []

    for index, hotel in enumerate(
        properties
    ):

        if not isinstance(
            hotel,
            dict,
        ):
            continue

        name = clean_text(
            hotel.get("name")
        )

        if not name:
            continue

        # ====================================================
        # PRICE
        # ====================================================

        price = extract_hotel_nightly_price(hotel)

        price_available = price is not None

        within_budget = None

        if price_available:
            within_budget = price <= budget

        # ====================================================
        # RATING
        # ====================================================

        rating = safe_float(
            hotel.get(
                "overall_rating"
            )
            or hotel.get(
                "rating"
            )
        )

        # ====================================================
        # TOTAL REVIEW COUNT
        # ====================================================

        total_review_count = safe_int(
            hotel.get(
                "reviews"
            )
        )

        # ====================================================
        # PROPERTY TOKEN
        # ====================================================

        property_token = clean_text(
            hotel.get(
                "property_token"
            )
        )

        # ====================================================
        # DIRECT HOTEL LINK
        # ====================================================

        hotel_link = (
            hotel.get("link")
            or hotel.get("hotel_link")
            or hotel.get("booking_link")
        )

        if hotel_link:

            hotel_link = clean_text(
                hotel_link
            )

        # ====================================================
        # REVIEWS BREAKDOWN
        # ====================================================

        reviews_breakdown = hotel.get(
            "reviews_breakdown",
            [],
        )

        if not isinstance(
            reviews_breakdown,
            list,
        ):
            reviews_breakdown = []

        # ====================================================
        # STRUCTURED CATEGORY ANALYSIS
        # ====================================================

        hygiene_breakdown = (
            analyze_review_breakdown(
                reviews_breakdown,
                "hygiene",
            )
        )

        safety_breakdown = (
            analyze_review_breakdown(
                reviews_breakdown,
                "safety",
            )
        )

        # ====================================================
        # DEFAULT TEXT ANALYSIS
        # ====================================================

        text_hygiene_analysis = {
            "score": None,
            "insufficient_data": True,
            "positive": [],
            "negative": [],
            "review_count": 0,
            "evidence_review_count": 0,
        }

        text_safety_analysis = {
            "score": None,
            "insufficient_data": True,
            "positive": [],
            "negative": [],
            "review_count": 0,
            "evidence_review_count": 0,
        }

        review_sample_count = 0

        # ====================================================
        # DETAILED REVIEW TEXT
        # ====================================================
        #
        # Only the first six hotels get detailed review
        # retrieval.
        #
        # If a relevant category token exists, use it.
        #
        # Otherwise use general hotel reviews.
        #
        # This is based on SerpApi's documented category_token
        # capability.
        # ====================================================

        if (
            index
            < MAX_HOTELS_WITH_REVIEW_ANALYSIS
            and property_token
        ):

            # ------------------------------------------------
            # HYGIENE REVIEW TEXT
            # ------------------------------------------------

            hygiene_reviews = []

            try:

                hygiene_category_token = (
                    hygiene_breakdown.get(
                        "category_token"
                    )
                    if hygiene_breakdown
                    else None
                )

                hygiene_reviews = (
                    get_hotel_reviews(
                        property_token,
                        hygiene_category_token,
                    )
                )

                if hygiene_reviews:

                    text_hygiene_analysis = (
                        analyze_reviews(
                            hygiene_reviews,
                            "hygiene",
                        )
                    )

            except HTTPException as exc:

                print(
                    f"Hygiene review search failed "
                    f"for {name}:",
                    exc.detail,
                )

            except Exception as exc:

                print(
                    f"Hygiene review analysis failed "
                    f"for {name}:",
                    repr(exc),
                )

            # ------------------------------------------------
            # SAFETY REVIEW TEXT
            # ------------------------------------------------

            safety_reviews = []

            try:

                safety_category_token = (
                    safety_breakdown.get(
                        "category_token"
                    )
                    if safety_breakdown
                    else None
                )

                safety_reviews = (
                    get_hotel_reviews(
                        property_token,
                        safety_category_token,
                    )
                )

                if safety_reviews:

                    text_safety_analysis = (
                        analyze_reviews(
                            safety_reviews,
                            "safety",
                        )
                    )

            except HTTPException as exc:

                print(
                    f"Safety review search failed "
                    f"for {name}:",
                    exc.detail,
                )

            except Exception as exc:

                print(
                    f"Safety review analysis failed "
                    f"for {name}:",
                    repr(exc),
                )

            review_sample_count = max(
                len(hygiene_reviews),
                len(safety_reviews),
            )

        # ====================================================
        # FINAL ANALYSIS
        # ====================================================

        hygiene_analysis = (
            merge_review_analyses(
                hygiene_breakdown,
                text_hygiene_analysis,
            )
        )

        safety_analysis = (
            merge_review_analyses(
                safety_breakdown,
                text_safety_analysis,
            )
        )

        # ====================================================
        # DATABASE RECORD
        # ====================================================

        hotel_data = {
            "name": name,

            # Keep a missing price as NULL/None.
            # Zero is not a real hotel price and must never be
            # displayed as one.

            "price": price,

            "rating": rating,

            "hygiene_score": (
                hygiene_analysis.get(
                    "score"
                )
                if hygiene_analysis.get(
                    "score"
                ) is not None
                else 0
            ),

            "womens_safety_score": (
                safety_analysis.get(
                    "score"
                )
                if safety_analysis.get(
                    "score"
                ) is not None
                else 0
            ),

            "hygiene_evidence": (
                hygiene_analysis
            ),

            "safety_evidence": (
                safety_analysis
            ),
        }

        # ====================================================
        # SAVE HOTEL
        # ====================================================

        try:

            database_hotel_id = (
                save_hotel(
                    hotel_data
                )
            )

        except Exception as exc:

            print(
                f"Database save failed for {name}:",
                repr(exc),
            )

            database_hotel_id = None

        # IMPORTANT:
        #
        # This is the real SQLite ID.
        #
        # Never use index + 1.

        hotel_data["id"] = (
            database_hotel_id
        )

        hotel_data["hotel_id"] = (
            database_hotel_id
        )

        # ====================================================
        # COMMUNITY SUMMARY
        # ====================================================

        external_safety_score = (
            safety_analysis.get(
                "score"
            )
        )

        if database_hotel_id is not None:

            community_summary = (
                get_community_summary(
                    database_hotel_id,
                    external_safety_score,
                )
            )

        else:

            community_summary = {
                "community_rating": None,
                "community_score_10": None,
                "community_review_count": 0,
                "community_weight": 0,
                "combined_womens_safety_score": (
                    external_safety_score
                ),
                "combined_score_source": (
                    "External review evidence"
                    if external_safety_score
                    is not None
                    else "Insufficient evidence"
                ),
            }

        hotel_data.update(
            community_summary
        )

        # ====================================================
        # FRONTEND RESULT
        # ====================================================

        hotel_data[
            "price_available"
        ] = price_available

        hotel_data[
            "within_budget"
        ] = within_budget

        hotel_data[
            "property_token"
        ] = property_token

        hotel_data[
            "link"
        ] = hotel_link

        hotel_data[
            "total_review_count"
        ] = total_review_count

        hotel_data[
            "review_sample_count"
        ] = review_sample_count

        hotel_data[
            "review_analysis_limited"
        ] = (
            index
            >= MAX_HOTELS_WITH_REVIEW_ANALYSIS
        )

        hotel_data[
            "source"
        ] = (
            "Google Hotels via SerpApi"
        )

        hotel_data[
            "review_source"
        ] = (
            "Google Hotels Reviews via SerpApi"
        )

        hotel_data[
            "review_breakdown_available"
        ] = bool(
            reviews_breakdown
        )

        hotels.append(
            hotel_data
        )

    # ========================================================
    # SORTING
    # ========================================================

    def hotel_sort_key(
        hotel,
    ):

        within_budget = (
            hotel.get(
                "within_budget"
            )
        )

        price = hotel.get(
            "price"
        )

        price_available = hotel.get(
            "price_available",
            False,
        )

        if within_budget is True:

            budget_rank = 0

        elif within_budget is None:

            budget_rank = 1

        else:

            budget_rank = 2

        if not price_available:

            price_rank = float(
                "inf"
            )

        else:

            price_rank = (
                price
                or float("inf")
            )

        return (
            budget_rank,
            price_rank,
        )

    hotels.sort(
        key=hotel_sort_key
    )

    return hotels


# ============================================================
# COMMUNITY SAFETY SUMMARY
# ============================================================

def get_community_summary(
    hotel_id: int,
    external_safety_score: Optional[float] = None,
):
    """
    Calculates the human community signal.

    IMPORTANT:

    The community score does NOT overwrite the original
    SerpApi-derived safety score.

    Instead we produce:

        external score
        community score
        combined score

    so the user can see where the information came from.
    """

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                rating
            FROM community_reviews
            WHERE hotel_id = ?
            ORDER BY created_at ASC
            """,
            (
                hotel_id,
            ),
        )

        rows = cursor.fetchall()

    finally:

        conn.close()

    ratings = []

    for row in rows:

        value = safe_float(
            row[0]
        )

        if value is not None:

            ratings.append(
                value
            )

    count = len(
        ratings
    )

    if count == 0:

        return {
            "community_rating": None,

            "community_score_10": None,

            "community_review_count": 0,

            "community_weight": 0,

            "combined_womens_safety_score": (
                external_safety_score
            ),

            "combined_score_source": (
                "External review evidence"
                if external_safety_score
                is not None
                else "Insufficient evidence"
            ),
        }

    # ========================================================
    # COMMUNITY AVERAGE
    # ========================================================

    community_rating = round(
        sum(ratings)
        / count,
        1,
    )

    # Convert /5 to /10.

    community_score_10 = round(
        community_rating * 2,
        1,
    )

    # ========================================================
    # COMMUNITY WEIGHT
    # ========================================================
    #
    # 1 report  -> 15%
    # 2 reports -> 20%
    # 3 reports -> 25%
    # 4 reports -> 30%
    # 5+ reports -> 35%
    #
    # The cap prevents a small number of reports from
    # completely replacing external review evidence.
    # ========================================================

    community_weight = min(
        0.35,
        0.10
        + (
            0.05
            * count
        ),
    )

    # ========================================================
    # COMBINED SCORE
    # ========================================================

    if external_safety_score is not None:

        combined_score = round(
            (
                external_safety_score
                * (
                    1
                    - community_weight
                )
            )
            +
            (
                community_score_10
                * community_weight
            ),
            1,
        )

        combined_source = (
            "External review evidence + "
            "traveler community reports"
        )

    else:

        # If external evidence doesn't exist, community
        # evidence can still be shown.
        #
        # We explicitly identify it as community-only.

        combined_score = (
            community_score_10
        )

        combined_source = (
            "Traveler community reports only"
        )

    return {
        "community_rating": (
            community_rating
        ),

        "community_score_10": (
            community_score_10
        ),

        "community_review_count": (
            count
        ),

        "community_weight": (
            community_weight
        ),

        "combined_womens_safety_score": (
            combined_score
        ),

        "combined_score_source": (
            combined_source
        ),
    }


# ============================================================
# OPEN-METEO GEOCODING
# ============================================================

def geocode_destination(
    destination: str,
):
    """
    Resolve a destination name to latitude/longitude.

    Open-Meteo's geocoder supports country-code filtering, so
    Indian destinations are searched with countryCode=IN first.
    A few common city-name aliases are also tried because users
    may enter older/common names such as Bangalore instead of
    Bengaluru.

    Returns a location dictionary or None.
    """

    destination = clean_text(destination)

    if not destination:
        return None

    aliases = {
        "bangalore": "Bengaluru",
        "bengaluru": "Bengaluru",
        "bombay": "Mumbai",
        "calcutta": "Kolkata",
        "madras": "Chennai",
        "poona": "Pune",
        "mysore": "Mysuru",
        "new delhi": "Delhi",
        "new delhi, india": "Delhi",
    }

    search_terms = [destination]

    lower_destination = destination.lower().strip()

    if lower_destination in aliases:
        canonical = aliases[lower_destination]
        if canonical.lower() != lower_destination:
            search_terms.append(canonical)

    # If the user already supplied an Indian state/country, keep
    # the original query and also try the city portion alone.
    if "," in destination:
        city_part = destination.split(",", 1)[0].strip()
        if city_part and city_part not in search_terms:
            search_terms.append(city_part)

    for search_term in search_terms:
        try:
            response = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={
                    "name": search_term,
                    "count": 5,
                    "language": "en",
                    "format": "json",
                    "countryCode": "IN",
                },
                timeout=15,
            )

            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])

            if not isinstance(results, list) or not results:
                continue

            # Prefer an Indian result explicitly returned by the
            # geocoder. This protects against ambiguous city names.
            location = next(
                (
                    item
                    for item in results
                    if isinstance(item, dict)
                    and str(item.get("country_code", "")).upper() == "IN"
                ),
                results[0],
            )

            latitude = safe_float(location.get("latitude"))
            longitude = safe_float(location.get("longitude"))

            if latitude is None or longitude is None:
                continue

            return {
                "latitude": latitude,
                "longitude": longitude,
                "name": location.get("name"),
                "country": location.get("country"),
                "country_code": location.get("country_code"),
                "admin1": location.get("admin1"),
            }

        except requests.RequestException as exc:
            print(
                "Open-Meteo geocoding request error:",
                repr(exc),
            )
            continue

        except (ValueError, TypeError) as exc:
            print(
                "Open-Meteo geocoding response error:",
                repr(exc),
            )
            continue

        except Exception as exc:
            print(
                "Open-Meteo geocoding error:",
                repr(exc),
            )
            continue

    # Final fallback: retry without the country filter. This helps
    # with inputs such as "Delhi, India" or destinations whose
    # geocoder record does not expose country_code consistently.
    fallback_term = destination.split(",", 1)[0].strip() or destination

    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": fallback_term,
                "count": 10,
                "language": "en",
                "format": "json",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        if isinstance(results, list):
            # Prefer India when it is present, otherwise use the first
            # valid geocoded result rather than failing the weather card.
            ordered = sorted(
                [item for item in results if isinstance(item, dict)],
                key=lambda item: (
                    str(item.get("country_code", "")).upper() != "IN",
                    item.get("name", ""),
                ),
            )

            for location in ordered:
                latitude = safe_float(location.get("latitude"))
                longitude = safe_float(location.get("longitude"))

                if latitude is not None and longitude is not None:
                    return {
                        "latitude": latitude,
                        "longitude": longitude,
                        "name": location.get("name"),
                        "country": location.get("country"),
                        "country_code": location.get("country_code"),
                        "admin1": location.get("admin1"),
                    }

    except Exception as exc:
        print(
            "Open-Meteo fallback geocoding error:",
            repr(exc),
        )

    return None


# ============================================================
# WEATHER DESCRIPTION
# ============================================================

def weather_description(
    code: Any,
) -> str:

    code = safe_int(
        code
    )

    if code is None:
        return "Weather information"

    weather_codes = {

        0: "Clear sky",

        1: "Mainly clear",

        2: "Partly cloudy",

        3: "Overcast",

        45: "Fog",

        48: "Depositing rime fog",

        51: "Light drizzle",

        53: "Moderate drizzle",

        55: "Dense drizzle",

        56: "Light freezing drizzle",

        57: "Dense freezing drizzle",

        61: "Slight rain",

        63: "Moderate rain",

        65: "Heavy rain",

        66: "Light freezing rain",

        67: "Heavy freezing rain",

        71: "Slight snowfall",

        73: "Moderate snowfall",

        75: "Heavy snowfall",

        77: "Snow grains",

        80: "Slight rain showers",

        81: "Moderate rain showers",

        82: "Violent rain showers",

        85: "Slight snow showers",

        86: "Heavy snow showers",

        95: "Thunderstorm",

        96: "Thunderstorm with slight hail",

        99: "Thunderstorm with heavy hail",
    }

    return weather_codes.get(
        code,
        "Weather information",
    )


# ============================================================
# OPEN-METEO WEATHER
# ============================================================

def get_open_meteo_weather(
    destination: str,
    start_date: str,
    end_date: str,
):

    start = parse_date(
        start_date
    )

    end = parse_date(
        end_date
    )

    today = date.today()

    # ========================================================
    # DATE RANGE
    # ========================================================

    if end < start:
        return {
            "available": False,
            "reason": (
                "The end date cannot be before the start date."
            ),
            "forecast": [],
            "official_alerts": [],
        }

    # Open-Meteo Forecast API supports up to 16 future days and
    # also exposes recent past days. For older past dates, use the
    # Historical Weather API instead of pretending a forecast exists.
    future_end_days = (end - today).days
    past_start_days = (today - start).days

    if start > today and future_end_days > 15:
        return {
            "available": False,
            "reason": (
                "Weather forecast is available only within "
                "the next 16 days."
            ),
            "forecast": [],
            "official_alerts": [],
        }

    # ========================================================
    # GEOCODE
    # ========================================================

    location = geocode_destination(destination)

    if not location:
        return {
            "available": False,
            "reason": (
                "Could not locate the destination for weather lookup."
            ),
            "forecast": [],
            "official_alerts": [],
        }

    is_past = end < today
    is_mixed = start < today <= end

    if is_past and past_start_days > 92:
        # Historical Weather API can go much farther back, but the
        # UI is intended for recent travel planning. Keep the route
        # bounded and explicit.
        return {
            "available": False,
            "reason": (
                "Weather history is limited to the recent planning window "
                "for SafeRoute."
            ),
            "forecast": [],
            "official_alerts": [],
        }

    # ========================================================
    # WEATHER REQUEST
    # ========================================================

    try:

        weather_endpoint = (
            "https://api.open-meteo.com/v1/forecast"
            if not is_past
            else "https://archive-api.open-meteo.com/v1/archive"
        )

        response = requests.get(

            weather_endpoint,

            params={

                "latitude": location[
                    "latitude"
                ],

                "longitude": location[
                    "longitude"
                ],

                "daily": ",".join([
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_probability_max",
                    "precipitation_sum",
                    "rain_sum",
                    "wind_speed_10m_max",
                ]),

                "timezone": "auto",

                "start_date": start_date,

                "end_date": end_date,

                **(
                    {
                        # Only send past_days when the requested range
                        # actually starts in the past. Open-Meteo does not
                        # accept a negative past_days value for a future-only
                        # trip.
                        **(
                            {
                                "past_days": min(max(past_start_days, 0), 92)
                            }
                            if start < today
                            else {}
                        ),
                        
                    }
                    if not is_past
                    else {}
                ),
            },

            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

        daily = data.get(
            "daily",
            {},
        )

        dates = daily.get(
            "time",
            [],
        )

        max_temps = daily.get(
            "temperature_2m_max",
            [],
        )

        min_temps = daily.get(
            "temperature_2m_min",
            [],
        )

        weather_codes = daily.get(
            "weather_code",
            [],
        )

        rain_probability = daily.get(
            "precipitation_probability_max",
            [],
        )

        precipitation_sum = daily.get(
            "precipitation_sum",
            [],
        )

        rain_sum = daily.get(
            "rain_sum",
            [],
        )

        wind_speed = daily.get(
            "wind_speed_10m_max",
            [],
        )

        forecast = []

        for index, forecast_date in enumerate(
            dates
        ):

            forecast.append({

                "date": forecast_date,

                "description": (
                    weather_description(
                        weather_codes[index]
                        if index
                        < len(
                            weather_codes
                        )
                        else None
                    )
                ),

                "temperature_min": (

                    min_temps[index]

                    if index
                    < len(
                        min_temps
                    )

                    else None
                ),

                "temperature_max": (

                    max_temps[index]

                    if index
                    < len(
                        max_temps
                    )

                    else None
                ),

                # IMPORTANT:
                # This exactly matches SafetyAlert.jsx.

                "rain_probability": (

                    rain_probability[index]

                    if index
                    < len(
                        rain_probability
                    )

                    else None
                ),

                "precipitation_sum": (

                    precipitation_sum[index]

                    if index
                    < len(
                        precipitation_sum
                    )

                    else None
                ),

                "rain_sum": (

                    rain_sum[index]

                    if index
                    < len(
                        rain_sum
                    )

                    else None
                ),

                # IMPORTANT:
                # This exactly matches SafetyAlert.jsx.

                "wind_speed_kmh": (

                    wind_speed[index]

                    if index
                    < len(
                        wind_speed
                    )

                    else None
                ),
            })

        return {

            "available": True,

            "destination": destination,

            "location": location,

            "forecast": forecast,

            # Open-Meteo forecast data is not the same
            # thing as an official government emergency
            # alert feed.

            "official_alerts": [],

            "source": (
                "Open-Meteo Forecast API"
                if not is_past
                else "Open-Meteo Historical Weather API"
            ),

            "alert_source_connected": False,

            "alert_note": (
                "Official government emergency alerts "
                "are not currently connected. Weather "
                "forecast information is available below."
            ),
        }

    except Exception as exc:

        print(
            "Open-Meteo weather error:",
            repr(exc),
        )

        return {

            "available": False,

            "reason": (
                f"Weather request failed: {str(exc)}"
            ),

            "forecast": [],

            "official_alerts": [],

            "alert_source_connected": False,
        }


# ============================================================
# SAFETY / WEATHER INFORMATION
# ============================================================

def search_safety_alert(
    destination: str,
    start_date: str,
    end_date: str,
):

    weather = get_open_meteo_weather(
        destination,
        start_date,
        end_date,
    )

    official_alerts = weather.get(
        "official_alerts",
        [],
    )

    if official_alerts:

        message = (
            "Official weather-provider alert "
            "information is available."
        )

    elif weather.get(
        "available"
    ):

        message = (
            "No weather-provider alerts were "
            "returned. The forecast below should "
            "still be reviewed because weather "
            "conditions can change."
        )

    else:

        message = (
            weather.get(
                "reason"
            )
            or
            "Weather alert information is unavailable."
        )

    return {

        "has_alert": bool(
            official_alerts
        ),

        "message": message,

        "weather": weather,

        "official_alerts": (
            official_alerts
        ),

        "source": weather.get(
            "source",
            "Open-Meteo",
        ),
    }


# ============================================================
# GOOGLE NEWS / TRAVEL INFORMATION
# ============================================================

def search_travel_news(
    destination: str,
):

    if not SERPAPI_API_KEY:
        return []

    query = (
        f"{destination} travel "
        "(protest OR strike OR road closure OR "
        "landslide OR flood OR travel disruption)"
    )

    try:

        results = serpapi_search({

            "engine": "google_news",

            "q": query,

            "gl": "in",

            "hl": "en",

            "so": "1",
        })

        news_results = results.get(
            "news_results",
            [],
        )

        if not isinstance(
            news_results,
            list,
        ):
            return []

        output = []

        for item in news_results[
            :MAX_TRAVEL_NEWS
        ]:

            if not isinstance(
                item,
                dict,
            ):
                continue

            source = item.get(
                "source"
            )

            if isinstance(
                source,
                dict,
            ):

                source_name = source.get(
                    "name"
                )

            else:

                source_name = source

            output.append({

                "title": clean_text(
                    item.get(
                        "title"
                    )
                ),

                "snippet": clean_text(
                    item.get(
                        "snippet"
                    )
                ),

                "link": item.get(
                    "link"
                ),

                "date": item.get(
                    "date"
                ),

                "iso_date": item.get(
                    "iso_date"
                ),

                "source": {

                    "name": (
                        clean_text(
                            source_name
                        )
                        if source_name
                        else "News source"
                    ),
                },

                "information_type": (
                    "Recent travel information"
                ),

                "official": False,
            })

        return output

    except HTTPException:

        return []

    except Exception as exc:

        print(
            "Travel news error:",
            repr(exc),
        )

        return []


# ============================================================
# TRANSPORT ESTIMATE
# ============================================================

def estimate_transport(
    origin: str,
    destination: str,
    travelers: int,
):
    """
    Approximate planning estimate.

    NOT a live transport fare.
    """

    base_estimate = 1000

    if travelers <= 1:

        multiplier = 1.0

    elif travelers <= 2:

        multiplier = 1.7

    elif travelers <= 4:

        multiplier = 2.8

    else:

        multiplier = 3.8

    estimated_cost = int(
        base_estimate
        * multiplier
    )

    return {

        "origin": origin,

        "destination": destination,

        "travelers": travelers,

        "estimated_cost_inr": (
            estimated_cost
        ),

        "currency": "INR",

        "is_live_price": False,

        "note": (
            "This is an approximate planning estimate, "
            "not a live transport fare."
        ),
    }


# ============================================================
# MAIN PLAN ENDPOINT
# ============================================================

@app.post("/plan")
def create_plan(
    request: PlanRequest,
):
    """
    Main SafeRoute planning endpoint.

    Uses:

        1. SerpApi Google Hotels
        2. SerpApi Google Hotels Reviews
        3. SerpApi Google News
        4. Open-Meteo weather
        5. SQLite community reports
    """

    origin = clean_text(
        request.origin
    )

    destination = clean_text(
        request.destination
    )

    if not origin:

        raise HTTPException(
            status_code=400,
            detail="Origin is required.",
        )

    if not destination:

        raise HTTPException(
            status_code=400,
            detail="Destination is required.",
        )

    if request.budget <= 0:

        raise HTTPException(
            status_code=400,
            detail=(
                "Budget must be greater than zero."
            ),
        )

    if request.travelers <= 0:

        raise HTTPException(
            status_code=400,
            detail=(
                "Travelers must be at least 1."
            ),
        )

    start = parse_date(
        request.start_date
    )

    end = parse_date(
        request.end_date
    )

    today = date.today()

    if start < today:

        raise HTTPException(
            status_code=400,
            detail=(
                "Start date cannot be in the past."
            ),
        )

    if end <= start:

        raise HTTPException(
            status_code=400,
            detail=(
                "End date must be after the start date."
            ),
        )

    # ========================================================
    # HOTELS
    # ========================================================

    hotels = search_hotels(

        destination=destination,

        start_date=request.start_date,

        end_date=request.end_date,

        travelers=request.travelers,

        budget=request.budget,
    )

    # ========================================================
    # WEATHER
    # ========================================================

    safety_alert = search_safety_alert(

        destination=destination,

        start_date=request.start_date,

        end_date=request.end_date,
    )

    # ========================================================
    # TRAVEL NEWS
    # ========================================================

    travel_news = search_travel_news(
        destination
    )

    # ========================================================
    # TRANSPORT
    # ========================================================

    transport = estimate_transport(

        origin=origin,

        destination=destination,

        travelers=request.travelers,
    )

    # ========================================================
    # RETURN PLAN
    # ========================================================

    return {

        "origin": origin,

        "destination": destination,

        "budget": request.budget,

        "travelers": request.travelers,

        "start_date": request.start_date,

        "end_date": request.end_date,

        "hotels": hotels,

        "safety_alert": safety_alert,

        "travel_news": travel_news,

        "transport": transport,

        "data_sources": {

            "hotels": (
                "Google Hotels via SerpApi"
            ),

            "hotel_reviews": (
                "Google Hotels Reviews via SerpApi"
            ),

            "travel_news": (
                "Google News via SerpApi"
            ),

            "weather": (
                "Open-Meteo"
            ),

            "community": (
                "SafeRoute traveler community "
                "reports stored in SQLite"
            ),
        },

        "disclaimer": (
            "Hotel hygiene and women's safety "
            "information consists of transparent "
            "review-based and community-based signals. "
            "These are not guarantees of safety, "
            "hygiene, or future conditions."
        ),
    }


# ============================================================
# COMMUNITY REVIEWS
# ============================================================

@app.post(
    "/community/reviews"
)
def create_community_review(
    request: CommunityReviewRequest,
):
    """
    Saves a traveler community experience.

    Uses the real SQLite hotel ID.
    """

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                id,
                name
            FROM hotels
            WHERE id = ?
            """,
            (
                request.hotel_id,
            ),
        )

        hotel = cursor.fetchone()

        if not hotel:

            raise HTTPException(
                status_code=404,
                detail="Hotel not found.",
            )

        cursor.execute(
            """
            INSERT INTO community_reviews (
                hotel_id,
                rating,
                category,
                experience
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                request.hotel_id,

                request.rating,

                clean_text(
                    request.category
                ),

                clean_text(
                    request.experience
                ),
            ),
        )

        conn.commit()

        # ====================================================
        # READ ORIGINAL EXTERNAL SCORE
        # ====================================================

        cursor.execute(
            """
            SELECT
                womens_safety_score
            FROM hotels
            WHERE id = ?
            """,
            (
                request.hotel_id,
            ),
        )

        score_row = cursor.fetchone()

        external_score = None

        if score_row:

            external_score = safe_float(
                score_row[0]
            )

            # Database.py stores 0 when no external score
            # was available.
            #
            # Therefore 0 here means "missing", not a
            # genuine 0/10 assessment.

            if external_score == 0:

                external_score = None

        # ====================================================
        # RECALCULATE COMMUNITY SUMMARY
        # ====================================================

        community_summary = (
            get_community_summary(
                request.hotel_id,
                external_score,
            )
        )

        return {

            "success": True,

            "message": (
                "Your experience was submitted successfully."
            ),

            "hotel_id": (
                request.hotel_id
            ),

            "hotel_name": (
                hotel[1]
            ),

            "community": (
                community_summary
            ),
        }

    except HTTPException:

        raise

    except Exception as exc:

        conn.rollback()

        print(
            "Community review save error:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to save the community experience."
            ),
        )

    finally:

        conn.close()


# ============================================================
# GET COMMUNITY REVIEWS FOR HOTEL
# ============================================================

@app.get(
    "/community/hotel/{hotel_id}"
)
def get_community_reviews(
    hotel_id: int,
):
    conn = get_connection()

    cursor = conn.cursor()

    try:

        # ====================================================
        # HOTEL
        # ====================================================

        cursor.execute(
            """
            SELECT
                id,
                name,
                womens_safety_score
            FROM hotels
            WHERE id = ?
            """,
            (
                hotel_id,
            ),
        )

        hotel = cursor.fetchone()

        if not hotel:

            raise HTTPException(
                status_code=404,
                detail="Hotel not found.",
            )

        # ====================================================
        # COMMUNITY REVIEWS
        # ====================================================

        cursor.execute(
            """
            SELECT
                id,
                rating,
                category,
                experience,
                created_at
            FROM community_reviews
            WHERE hotel_id = ?
            ORDER BY created_at DESC
            """,
            (
                hotel_id,
            ),
        )

        rows = cursor.fetchall()

        reviews = []

        for row in rows:

            reviews.append({

                "id": row[0],

                "rating": row[1],

                "category": row[2],

                "experience": row[3],

                "created_at": row[4],
            })

        # ====================================================
        # COMMUNITY AVERAGE
        # ====================================================

        if reviews:

            average_rating = round(

                sum(
                    review["rating"]
                    for review in reviews
                )
                / len(reviews),

                1,
            )

        else:

            average_rating = None

        # ====================================================
        # EXTERNAL SCORE
        # ====================================================

        external_score = safe_float(
            hotel[2]
        )

        if external_score == 0:

            external_score = None

        # ====================================================
        # COMBINED SCORE
        # ====================================================

        community_summary = (
            get_community_summary(
                hotel_id,
                external_score,
            )
        )

        return {

            "hotel_id": hotel[0],

            "hotel_name": hotel[1],

            "community_rating": (
                average_rating
            ),

            "review_count": (
                len(reviews)
            ),

            "reviews": reviews,

            "external_womens_safety_score": (
                external_score
            ),

            "community_score_10": (
                community_summary.get(
                    "community_score_10"
                )
            ),

            "community_review_count": (
                community_summary.get(
                    "community_review_count"
                )
            ),

            "community_weight": (
                community_summary.get(
                    "community_weight"
                )
            ),

            "combined_womens_safety_score": (
                community_summary.get(
                    "combined_womens_safety_score"
                )
            ),

            "combined_score_source": (
                community_summary.get(
                    "combined_score_source"
                )
            ),
        }

    except HTTPException:

        raise

    except Exception as exc:

        print(
            "Community review read error:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load community experiences."
            ),
        )

    finally:

        conn.close()


# ============================================================
# SAFETY REPORT
# ============================================================

@app.post(
    "/safety/reports"
)
def receive_safety_report(
    request: SafetyReportRequest,
):
    """
    Receives a safety report.

    IMPORTANT:

    database.py does not contain a safety_reports table.

    Therefore this endpoint does NOT pretend to persist
    the report.
    """

    return {

        "success": True,

        "message": (
            "Safety report received by the API."
        ),

        "stored": False,

        "note": (
            "Persistent safety-report storage is not enabled "
            "because the current database schema does not "
            "contain a safety_reports table."
        ),

        "hotel_name": clean_text(
            request.hotel_name
        ),

        "report_type": clean_text(
            request.report_type
        ),
    }


# ============================================================
# HOTEL SAFETY DATABASE LOOKUP
# ============================================================

@app.get(
    "/safety/hotel/{hotel_name}"
)
def get_hotel_safety_information(
    hotel_name: str,
):
    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                id,
                name,
                price,
                rating,
                hygiene_score,
                womens_safety_score,
                hygiene_evidence,
                safety_evidence
            FROM hotels
            WHERE name = ?
            """,
            (
                hotel_name,
            ),
        )

        row = cursor.fetchone()

        if not row:

            raise HTTPException(
                status_code=404,
                detail="Hotel not found.",
            )

        try:

            hygiene_evidence = json.loads(
                row[6]
            )

        except Exception:

            hygiene_evidence = {}

        try:

            safety_evidence = json.loads(
                row[7]
            )

        except Exception:

            safety_evidence = {}

        external_score = safe_float(
            row[5]
        )

        if external_score == 0:

            external_score = None

        community_summary = (
            get_community_summary(
                row[0],
                external_score,
            )
        )

        return {

            "id": row[0],

            "name": row[1],

            "price": row[2],

            "rating": row[3],

            "hygiene_score": row[4],

            "womens_safety_score": (
                external_score
            ),

            "hygiene_evidence": (
                hygiene_evidence
            ),

            "safety_evidence": (
                safety_evidence
            ),

            "community_rating": (
                community_summary.get(
                    "community_rating"
                )
            ),

            "community_score_10": (
                community_summary.get(
                    "community_score_10"
                )
            ),

            "community_review_count": (
                community_summary.get(
                    "community_review_count"
                )
            ),

            "combined_womens_safety_score": (
                community_summary.get(
                    "combined_womens_safety_score"
                )
            ),

            "combined_score_source": (
                community_summary.get(
                    "combined_score_source"
                )
            ),
        }

    finally:

        conn.close()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health"
)
def health_check():

    return {

        "status": "ok",

        "serpapi_configured": bool(
            SERPAPI_API_KEY
        ),

        "database": "SQLite",

        "service": "SafeRoute API",
    }


# ============================================================
# DATABASE TEST
# ============================================================

@app.get(
    "/db-test"
)
def database_test():

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                id,
                name,
                price,
                rating,
                hygiene_score,
                womens_safety_score
            FROM hotels
            ORDER BY id DESC
            LIMIT 20
            """
        )

        rows = cursor.fetchall()

        hotels = []

        for row in rows:

            hotels.append({

                "id": row[0],

                "name": row[1],

                "price": row[2],

                "rating": row[3],

                "hygiene_score": row[4],

                "womens_safety_score": row[5],
            })

        return {

            "count": len(
                hotels
            ),

            "hotels": hotels,
        }

    finally:

        conn.close()


# ============================================================
# WEATHER TEST
# ============================================================

@app.get(
    "/weather-test"
)
def weather_test(
    destination: str,
    start_date: str,
    end_date: str,
):

    return get_open_meteo_weather(

        destination,

        start_date,

        end_date,
    )


# ============================================================
# ALERT TEST
# ============================================================

@app.get(
    "/alert-test"
)
def alert_test(
    destination: str,
    start_date: str,
    end_date: str,
):

    return search_safety_alert(

        destination,

        start_date,

        end_date,
    )


# ============================================================
# NEWS TEST
# ============================================================

@app.get(
    "/news-test"
)
def news_test(
    destination: str,
):

    return {

        "destination": destination,

        "results": search_travel_news(
            destination
        ),
    }


# ============================================================
# REVIEWS TEST
# ============================================================

@app.get(
    "/reviews-test"
)
def reviews_test(
    property_token: str,
):

    reviews = get_hotel_reviews(
        property_token
    )

    return {

        "review_count": len(
            reviews
        ),

        "reviews": reviews,
    }


# ============================================================
# ROOT
# ============================================================

@app.get(
    "/"
)
def root():

    return {

        "name": "SafeRoute API",

        "status": "running",

        "message": (
            "SafeRoute backend is running."
        ),

        "documentation": "/docs",
    }