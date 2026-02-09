"""Centralized SQL queries for VacanceAI Oracle database"""

import json
from typing import Any, Optional


# ============================================
# Helper functions
# ============================================

def parse_json_field(value: Any) -> Any:
    """Parse a JSON string field into a Python object."""
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    return value


def to_json_string(value: Any) -> Optional[str]:
    """Convert a Python object to a JSON string for CLOB storage."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def bool_to_number(value: bool) -> int:
    """Convert Python bool to Oracle NUMBER(1)."""
    return 1 if value else 0


def number_to_bool(value: Any) -> bool:
    """Convert Oracle NUMBER(1) to Python bool."""
    return bool(value)


# ============================================
# USERS
# ============================================

USER_SELECT = "SELECT * FROM users WHERE id = :id"
USER_BY_EMAIL = "SELECT * FROM users WHERE email = :email"
USER_INSERT = """
    INSERT INTO users (id, email, password_hash, first_name, last_name)
    VALUES (:id, :email, :password_hash, :first_name, :last_name)
"""
USER_UPDATE = """
    UPDATE users SET
        first_name = NVL(:first_name, first_name),
        last_name = NVL(:last_name, last_name),
        phone = NVL(:phone, phone),
        avatar_url = NVL(:avatar_url, avatar_url)
    WHERE id = :id
"""

# ============================================
# REFRESH TOKENS
# ============================================

REFRESH_TOKEN_INSERT = """
    INSERT INTO refresh_tokens (id, user_id, token, expires_at)
    VALUES (:id, :user_id, :token, :expires_at)
"""
REFRESH_TOKEN_SELECT = """
    SELECT * FROM refresh_tokens
    WHERE token = :token AND expires_at > SYSTIMESTAMP
"""
REFRESH_TOKEN_DELETE = "DELETE FROM refresh_tokens WHERE token = :token"
REFRESH_TOKEN_DELETE_USER = "DELETE FROM refresh_tokens WHERE user_id = :user_id"
REFRESH_TOKEN_CLEANUP = "DELETE FROM refresh_tokens WHERE expires_at <= SYSTIMESTAMP"

# ============================================
# DESTINATIONS
# ============================================

DESTINATIONS_LIST = """
    SELECT * FROM destinations
    ORDER BY average_rating DESC NULLS LAST
    OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
"""

DESTINATIONS_BY_COUNTRY = """
    SELECT * FROM destinations
    WHERE country = :country
    ORDER BY average_rating DESC NULLS LAST
    OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
"""

DESTINATION_BY_ID = "SELECT * FROM destinations WHERE id = :id"

DESTINATION_PACKAGES = """
    SELECT p.* FROM packages p
    WHERE p.destination_id = :destination_id AND p.is_active = 1
    ORDER BY p.price_per_person
"""

# ============================================
# PACKAGES
# ============================================

PACKAGES_LIST_BASE = """
    SELECT p.*,
           d.id AS dest_id, d.name AS dest_name, d.country AS dest_country,
           d.city AS dest_city, d.description AS dest_description,
           d.image_url AS dest_image_url, d.tags AS dest_tags,
           d.average_rating AS dest_average_rating, d.total_reviews AS dest_total_reviews,
           d.latitude AS dest_latitude, d.longitude AS dest_longitude
    FROM packages p
    JOIN destinations d ON p.destination_id = d.id
    WHERE p.is_active = 1
"""

PACKAGE_BY_ID = """
    SELECT p.*,
           d.id AS dest_id, d.name AS dest_name, d.country AS dest_country,
           d.city AS dest_city, d.description AS dest_description,
           d.image_url AS dest_image_url, d.tags AS dest_tags,
           d.average_rating AS dest_average_rating, d.total_reviews AS dest_total_reviews,
           d.latitude AS dest_latitude, d.longitude AS dest_longitude
    FROM packages p
    JOIN destinations d ON p.destination_id = d.id
    WHERE p.id = :id
"""

PACKAGE_SIMPLE = "SELECT * FROM packages WHERE id = :id"

PACKAGE_REVIEWS_WITH_USERS = """
    SELECT r.id, r.user_id, r.package_id, r.booking_id, r.rating,
           r.review_comment AS "comment", r.created_at, r.updated_at,
           u.first_name, u.last_name, u.avatar_url
    FROM reviews r
    JOIN users u ON r.user_id = u.id
    WHERE r.package_id = :package_id
    ORDER BY r.created_at DESC
"""

# ============================================
# BOOKINGS
# ============================================

BOOKINGS_BY_USER = """
    SELECT b.*,
           p.name AS pkg_name, p.description AS pkg_description,
           p.price_per_person AS pkg_price_per_person, p.duration_days AS pkg_duration_days,
           p.image_url AS pkg_image_url, p.destination_id AS pkg_destination_id,
           d.name AS dest_name, d.country AS dest_country,
           d.city AS dest_city, d.image_url AS dest_image_url
    FROM bookings b
    JOIN packages p ON b.package_id = p.id
    JOIN destinations d ON p.destination_id = d.id
    WHERE b.user_id = :user_id
"""

BOOKING_BY_ID = """
    SELECT b.*,
           p.name AS pkg_name, p.description AS pkg_description,
           p.price_per_person AS pkg_price_per_person, p.duration_days AS pkg_duration_days,
           p.image_url AS pkg_image_url, p.destination_id AS pkg_destination_id,
           d.name AS dest_name, d.country AS dest_country,
           d.city AS dest_city, d.image_url AS dest_image_url
    FROM bookings b
    JOIN packages p ON b.package_id = p.id
    JOIN destinations d ON p.destination_id = d.id
    WHERE b.id = :id AND b.user_id = :user_id
"""

BOOKING_INSERT = """
    INSERT INTO bookings (id, user_id, package_id, start_date, end_date, num_persons, total_price, special_requests, status, payment_status)
    VALUES (:id, :user_id, :package_id, TO_DATE(:start_date, 'YYYY-MM-DD'), TO_DATE(:end_date, 'YYYY-MM-DD'), :num_persons, :total_price, :special_requests, :status, :payment_status)
"""

BOOKING_UPDATE_STATUS = """
    UPDATE bookings SET status = :status WHERE id = :id
"""

BOOKING_SIMPLE = "SELECT * FROM bookings WHERE id = :id AND user_id = :user_id"

# ============================================
# FAVORITES
# ============================================

FAVORITES_BY_USER = """
    SELECT f.*,
           p.id AS pkg_id, p.name AS pkg_name, p.description AS pkg_description,
           p.price_per_person AS pkg_price_per_person, p.duration_days AS pkg_duration_days,
           p.image_url AS pkg_image_url, p.destination_id AS pkg_destination_id,
           p.is_active AS pkg_is_active,
           d.name AS dest_name, d.country AS dest_country,
           d.city AS dest_city, d.image_url AS dest_image_url
    FROM favorites f
    JOIN packages p ON f.package_id = p.id
    JOIN destinations d ON p.destination_id = d.id
    WHERE f.user_id = :user_id
"""

FAVORITE_INSERT = """
    INSERT INTO favorites (id, user_id, package_id)
    VALUES (:id, :user_id, :package_id)
"""

FAVORITE_CHECK = """
    SELECT id FROM favorites WHERE user_id = :user_id AND package_id = :package_id
"""

FAVORITE_DELETE = """
    DELETE FROM favorites WHERE user_id = :user_id AND package_id = :package_id
"""

# ============================================
# REVIEWS
# ============================================

REVIEWS_BY_PACKAGE = """
    SELECT r.id, r.user_id, r.package_id, r.booking_id, r.rating,
           r.review_comment AS "comment", r.created_at, r.updated_at,
           u.first_name, u.last_name, u.avatar_url
    FROM reviews r
    JOIN users u ON r.user_id = u.id
    WHERE r.package_id = :package_id
    ORDER BY r.created_at DESC
    OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
"""

REVIEW_INSERT = """
    INSERT INTO reviews (id, user_id, package_id, booking_id, rating, review_comment)
    VALUES (:id, :user_id, :package_id, :booking_id, :rating, :comment)
"""

REVIEW_CHECK_BOOKING = """
    SELECT id FROM reviews WHERE booking_id = :booking_id
"""

REVIEW_AVG_FOR_DESTINATION = """
    SELECT AVG(r.rating) AS avg_rating
    FROM reviews r
    JOIN packages p ON r.package_id = p.id
    WHERE p.destination_id = :destination_id
"""

DESTINATION_UPDATE_RATING = """
    UPDATE destinations SET average_rating = :average_rating WHERE id = :id
"""

# ============================================
# CONVERSATIONS
# ============================================

CONVERSATION_BY_ID = "SELECT * FROM conversations WHERE id = :id"

CONVERSATION_INSERT = """
    INSERT INTO conversations (id, user_id, messages, context)
    VALUES (:id, :user_id, :messages, :context)
"""

CONVERSATION_UPDATE_MESSAGES = """
    UPDATE conversations SET messages = :messages WHERE id = :id
"""

CONVERSATION_CLEAR = """
    UPDATE conversations SET messages = '[]' WHERE id = :id
"""

# ============================================
# TRIPADVISOR
# ============================================

TA_LOCATIONS_LIST = """
    SELECT * FROM tripadvisor_locations ORDER BY name
"""

TA_LOCATIONS_BY_COUNTRY = """
    SELECT * FROM tripadvisor_locations WHERE search_country = :country ORDER BY name
"""

TA_LOCATION_BY_ID = """
    SELECT * FROM tripadvisor_locations WHERE location_id = :location_id
"""

TA_PHOTOS_BY_LOCATION = """
    SELECT * FROM tripadvisor_photos WHERE location_id = :location_id
"""

TA_REVIEWS_BY_LOCATION = """
    SELECT * FROM tripadvisor_reviews WHERE location_id = :location_id
    ORDER BY published_date DESC NULLS LAST
"""

TA_COUNTRIES = """
    SELECT DISTINCT search_country FROM tripadvisor_locations
    WHERE search_country IS NOT NULL
    ORDER BY search_country
"""


# ============================================
# Row formatting helpers
# ============================================

def format_destination(row: dict) -> dict:
    """Format a destination row, parsing JSON fields."""
    if not row:
        return row
    row["tags"] = parse_json_field(row.get("tags"))
    return row


def format_package(row: dict) -> dict:
    """Format a package row, parsing JSON fields and booleans."""
    if not row:
        return row
    row["included"] = parse_json_field(row.get("included"))
    row["not_included"] = parse_json_field(row.get("not_included"))
    row["highlights"] = parse_json_field(row.get("highlights"))
    row["images"] = parse_json_field(row.get("images"))
    if "is_active" in row:
        row["is_active"] = number_to_bool(row["is_active"])
    return row


def format_package_with_destination(row: dict) -> dict:
    """Format a joined package+destination row into nested structure."""
    if not row:
        return row

    destination = {
        "id": row.pop("dest_id", None),
        "name": row.pop("dest_name", None),
        "country": row.pop("dest_country", None),
        "city": row.pop("dest_city", None),
        "description": row.pop("dest_description", None),
        "image_url": row.pop("dest_image_url", None),
        "tags": parse_json_field(row.pop("dest_tags", None)),
        "average_rating": row.pop("dest_average_rating", None),
        "total_reviews": row.pop("dest_total_reviews", None),
        "latitude": row.pop("dest_latitude", None),
        "longitude": row.pop("dest_longitude", None),
    }

    pkg = format_package(row)
    pkg["destinations"] = destination
    return pkg


def format_booking_with_joins(row: dict) -> dict:
    """Format a joined booking+package+destination row."""
    if not row:
        return row

    package = {
        "name": row.pop("pkg_name", None),
        "description": row.pop("pkg_description", None),
        "price_per_person": row.pop("pkg_price_per_person", None),
        "duration_days": row.pop("pkg_duration_days", None),
        "image_url": row.pop("pkg_image_url", None),
        "destination_id": row.pop("pkg_destination_id", None),
        "destinations": {
            "name": row.pop("dest_name", None),
            "country": row.pop("dest_country", None),
            "city": row.pop("dest_city", None),
            "image_url": row.pop("dest_image_url", None),
        }
    }

    row["packages"] = package
    return row


def format_favorite_with_joins(row: dict) -> dict:
    """Format a joined favorite+package+destination row."""
    if not row:
        return row

    package = {
        "id": row.pop("pkg_id", None),
        "name": row.pop("pkg_name", None),
        "description": row.pop("pkg_description", None),
        "price_per_person": row.pop("pkg_price_per_person", None),
        "duration_days": row.pop("pkg_duration_days", None),
        "image_url": row.pop("pkg_image_url", None),
        "destination_id": row.pop("pkg_destination_id", None),
        "is_active": number_to_bool(row.pop("pkg_is_active", 1)),
        "destinations": {
            "name": row.pop("dest_name", None),
            "country": row.pop("dest_country", None),
            "city": row.pop("dest_city", None),
            "image_url": row.pop("dest_image_url", None),
        }
    }

    row["packages"] = package
    return row


def format_review_with_user(row: dict) -> dict:
    """Format a joined review+user row."""
    if not row:
        return row

    row["users"] = {
        "first_name": row.pop("first_name", None),
        "last_name": row.pop("last_name", None),
        "avatar_url": row.pop("avatar_url", None),
    }
    return row


def format_conversation(row: dict) -> dict:
    """Format a conversation row, parsing JSON fields."""
    if not row:
        return row
    row["messages"] = parse_json_field(row.get("messages")) or []
    row["context"] = parse_json_field(row.get("context")) or {}
    return row


def format_ta_location(row: dict) -> dict:
    """Format a TripAdvisor location row."""
    if not row:
        return row
    row["address_obj"] = parse_json_field(row.get("address_obj"))
    return row


def format_ta_photo(row: dict) -> dict:
    """Format a TripAdvisor photo row."""
    if not row:
        return row
    if "uploaded_to_storage" in row:
        row["uploaded_to_storage"] = number_to_bool(row["uploaded_to_storage"])
    return row
