"""SQLAlchemy ORM models for VacanceAI Oracle database"""

from decimal import Decimal
from sqlalchemy import (
    Column, String, Integer, Numeric, Date, Text, ForeignKey,
    UniqueConstraint, Index, text as sa_text,
)
from sqlalchemy.dialects.oracle import CLOB, TIMESTAMP
from sqlalchemy.orm import relationship, declarative_base

from .types import JSONEncodedCLOB, OracleBoolean

Base = declarative_base()

TZ_TIMESTAMP = TIMESTAMP(timezone=True)


def _f(value):
    """Convert Decimal to float, pass through None."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return value


# ============================================
# 1. USERS
# ============================================

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, server_default=sa_text("SYS_GUID()"))
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50))
    avatar_url = Column(String(500))
    created_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))
    updated_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "password_hash": self.password_hash,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ============================================
# 2. REFRESH TOKENS
# ============================================

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, server_default=sa_text("SYS_GUID()"))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), nullable=False, unique=True)
    expires_at = Column(TZ_TIMESTAMP, nullable=False)
    created_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))

    user = relationship("User", back_populates="refresh_tokens")


# ============================================
# 3. DESTINATIONS
# ============================================

class Destination(Base):
    __tablename__ = "destinations"

    id = Column(String(36), primary_key=True, server_default=sa_text("SYS_GUID()"))
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    city = Column(String(100))
    description = Column(CLOB)
    image_url = Column(String(500))
    tags = Column(JSONEncodedCLOB)
    average_rating = Column(Numeric(3, 1), default=0)
    total_reviews = Column(Integer, default=0)
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    created_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))
    updated_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))

    packages = relationship("Package", back_populates="destination", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "country": self.country,
            "city": self.city,
            "description": self.description,
            "image_url": self.image_url,
            "tags": self.tags,
            "average_rating": _f(self.average_rating),
            "total_reviews": self.total_reviews,
            "latitude": _f(self.latitude),
            "longitude": _f(self.longitude),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_summary_dict(self):
        """Destination dict without created_at/updated_at (for nesting in packages)."""
        return {
            "id": self.id,
            "name": self.name,
            "country": self.country,
            "city": self.city,
            "description": self.description,
            "image_url": self.image_url,
            "tags": self.tags,
            "average_rating": _f(self.average_rating),
            "total_reviews": self.total_reviews,
            "latitude": _f(self.latitude),
            "longitude": _f(self.longitude),
        }

    def to_minimal_dict(self):
        """Minimal destination dict for booking/favorite nesting."""
        return {
            "name": self.name,
            "country": self.country,
            "city": self.city,
            "image_url": self.image_url,
        }


# ============================================
# 4. PACKAGES
# ============================================

class Package(Base):
    __tablename__ = "packages"

    id = Column(String(36), primary_key=True, server_default=sa_text("SYS_GUID()"))
    destination_id = Column(String(36), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(CLOB)
    price_per_person = Column(Numeric(10, 2), nullable=False)
    duration_days = Column(Integer, nullable=False)
    max_persons = Column(Integer, default=10)
    included = Column(JSONEncodedCLOB)
    not_included = Column(JSONEncodedCLOB)
    highlights = Column(JSONEncodedCLOB)
    image_url = Column(String(500))
    images = Column(JSONEncodedCLOB)
    available_from = Column(Date)
    available_to = Column(Date)
    is_active = Column(OracleBoolean, default=True)
    hotel_category = Column(Integer)
    created_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))
    updated_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))

    destination = relationship("Destination", back_populates="packages")
    bookings = relationship("Booking", back_populates="package")
    favorites = relationship("Favorite", back_populates="package", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="package", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "destination_id": self.destination_id,
            "name": self.name,
            "description": self.description,
            "price_per_person": _f(self.price_per_person),
            "duration_days": self.duration_days,
            "max_persons": self.max_persons,
            "included": self.included,
            "not_included": self.not_included,
            "highlights": self.highlights,
            "image_url": self.image_url,
            "images": self.images,
            "available_from": self.available_from,
            "available_to": self.available_to,
            "is_active": self.is_active,
            "hotel_category": self.hotel_category,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_dict_with_destination(self):
        """Package dict with nested destination (matches format_package_with_destination)."""
        d = self.to_dict()
        if self.destination:
            d["destinations"] = self.destination.to_summary_dict()
        else:
            d["destinations"] = None
        return d

    def to_booking_dict(self):
        """Package dict for nesting inside a booking."""
        return {
            "name": self.name,
            "description": self.description,
            "price_per_person": _f(self.price_per_person),
            "duration_days": self.duration_days,
            "image_url": self.image_url,
            "destination_id": self.destination_id,
            "destinations": self.destination.to_minimal_dict() if self.destination else None,
        }

    def to_favorite_dict(self):
        """Package dict for nesting inside a favorite."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price_per_person": _f(self.price_per_person),
            "duration_days": self.duration_days,
            "max_persons": self.max_persons,
            "image_url": self.image_url,
            "images": self.images,
            "destination_id": self.destination_id,
            "is_active": self.is_active,
            "destinations": self.destination.to_minimal_dict() if self.destination else None,
        }


# ============================================
# 5. BOOKINGS
# ============================================

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String(36), primary_key=True, server_default=sa_text("SYS_GUID()"))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    package_id = Column(String(36), ForeignKey("packages.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    num_persons = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    payment_status = Column(String(20), nullable=False, default="unpaid")
    special_requests = Column(CLOB)
    created_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))
    updated_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))

    user = relationship("User", back_populates="bookings")
    package = relationship("Package", back_populates="bookings")
    reviews = relationship("Review", back_populates="booking")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "package_id": self.package_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "num_persons": self.num_persons,
            "total_price": _f(self.total_price),
            "status": self.status,
            "payment_status": self.payment_status,
            "special_requests": self.special_requests,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_dict_with_joins(self):
        """Booking dict with nested package+destination (matches format_booking_with_joins)."""
        d = self.to_dict()
        if self.package:
            d["packages"] = self.package.to_booking_dict()
        else:
            d["packages"] = None
        return d


# ============================================
# 6. FAVORITES
# ============================================

class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "package_id", name="uq_favorites"),
    )

    id = Column(String(36), primary_key=True, server_default=sa_text("SYS_GUID()"))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    package_id = Column(String(36), ForeignKey("packages.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))

    user = relationship("User", back_populates="favorites")
    package = relationship("Package", back_populates="favorites")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "package_id": self.package_id,
            "created_at": self.created_at,
        }

    def to_dict_with_joins(self):
        """Favorite dict with nested package+destination (matches format_favorite_with_joins)."""
        d = self.to_dict()
        if self.package:
            d["packages"] = self.package.to_favorite_dict()
        else:
            d["packages"] = None
        return d


# ============================================
# 7. REVIEWS
# ============================================

class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, server_default=sa_text("SYS_GUID()"))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    package_id = Column(String(36), ForeignKey("packages.id", ondelete="CASCADE"), nullable=False)
    booking_id = Column(String(36), ForeignKey("bookings.id"))
    rating = Column(Integer, nullable=False)
    review_comment = Column(CLOB)
    created_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))
    updated_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))

    user = relationship("User", back_populates="reviews")
    package = relationship("Package", back_populates="reviews")
    booking = relationship("Booking", back_populates="reviews")

    def to_dict_with_user(self):
        """Review dict with nested user info (matches format_review_with_user).
        Maps review_comment -> 'comment' for API contract.
        """
        d = {
            "id": self.id,
            "user_id": self.user_id,
            "package_id": self.package_id,
            "booking_id": self.booking_id,
            "rating": self.rating,
            "comment": self.review_comment,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.user:
            d["users"] = {
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "avatar_url": self.user.avatar_url,
            }
        else:
            d["users"] = None
        return d


# ============================================
# 8. CONVERSATIONS
# ============================================

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    messages = Column(JSONEncodedCLOB)
    context = Column(JSONEncodedCLOB)
    created_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))
    updated_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "messages": self.messages or [],
            "context": self.context or {},
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ============================================
# 9. TRIPADVISOR LOCATIONS
# ============================================

class TripAdvisorLocation(Base):
    __tablename__ = "tripadvisor_locations"

    id = Column(String(36), primary_key=True, server_default=sa_text("SYS_GUID()"))
    location_id = Column(String(50), nullable=False, unique=True)
    name = Column(String(500))
    description = Column(CLOB)
    web_url = Column(String(1000))
    address_obj = Column(JSONEncodedCLOB)
    latitude = Column(String(50))
    longitude = Column(String(50))
    phone = Column(String(100))
    website = Column(String(1000))
    email = Column(String(255))
    rating = Column(Numeric(3, 1))
    num_reviews = Column(Integer)
    ranking_data = Column(String(500))
    price_level = Column(String(50))
    search_country = Column(String(100))
    search_query = Column(String(255))
    created_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))
    updated_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))

    photos = relationship("TripAdvisorPhoto", foreign_keys="TripAdvisorPhoto.location_id", primaryjoin="TripAdvisorLocation.location_id == TripAdvisorPhoto.location_id", lazy="select", viewonly=True)
    reviews = relationship("TripAdvisorReview", foreign_keys="TripAdvisorReview.location_id", primaryjoin="TripAdvisorLocation.location_id == TripAdvisorReview.location_id", lazy="select", viewonly=True)

    def to_dict(self):
        return {
            "id": self.id,
            "location_id": self.location_id,
            "name": self.name,
            "description": self.description,
            "web_url": self.web_url,
            "address_obj": self.address_obj,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "phone": self.phone,
            "website": self.website,
            "email": self.email,
            "rating": _f(self.rating),
            "num_reviews": self.num_reviews,
            "ranking_data": self.ranking_data,
            "price_level": self.price_level,
            "search_country": self.search_country,
            "search_query": self.search_query,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_dict_with_details(self):
        d = self.to_dict()
        d["photos"] = [p.to_dict() for p in self.photos]
        d["reviews"] = [r.to_dict() for r in self.reviews]
        avg = 0.0
        if self.reviews:
            ratings = [r.rating for r in self.reviews if r.rating]
            avg = sum(ratings) / len(ratings) if ratings else 0.0
        d["average_rating"] = round(avg, 1)
        return d


# ============================================
# 10. TRIPADVISOR PHOTOS
# ============================================

class TripAdvisorPhoto(Base):
    __tablename__ = "tripadvisor_photos"

    id = Column(String(36), primary_key=True, server_default=sa_text("SYS_GUID()"))
    location_id = Column(String(50), nullable=False)
    photo_id = Column(String(50))
    url_original = Column(String(1000))
    url_large = Column(String(1000))
    url_medium = Column(String(1000))
    url_small = Column(String(1000))
    caption = Column(String(1000))
    uploaded_to_storage = Column(OracleBoolean, default=False)
    storage_path = Column(String(500))
    created_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))

    def to_dict(self):
        return {
            "id": self.id,
            "location_id": self.location_id,
            "photo_id": self.photo_id,
            "url_original": self.url_original,
            "url_large": self.url_large,
            "url_medium": self.url_medium,
            "url_small": self.url_small,
            "caption": self.caption,
            "uploaded_to_storage": self.uploaded_to_storage,
            "storage_path": self.storage_path,
            "created_at": self.created_at,
        }


# ============================================
# 11. TRIPADVISOR REVIEWS
# ============================================

class TripAdvisorReview(Base):
    __tablename__ = "tripadvisor_reviews"

    id = Column(String(36), primary_key=True, server_default=sa_text("SYS_GUID()"))
    location_id = Column(String(50), nullable=False)
    review_id = Column(String(50))
    title = Column(String(500))
    text = Column(CLOB)
    rating = Column(Integer)
    published_date = Column(TZ_TIMESTAMP)
    travel_date = Column(String(50))
    trip_type = Column(String(50))
    username = Column(String(255))
    user_location = Column(String(255))
    url = Column(String(1000))
    created_at = Column(TZ_TIMESTAMP, nullable=False, server_default=sa_text("SYSTIMESTAMP"))

    def to_dict(self):
        """Maps 'username' -> 'user_name' for frontend compatibility."""
        return {
            "id": self.id,
            "location_id": self.location_id,
            "review_id": self.review_id,
            "title": self.title,
            "text": self.text,
            "rating": self.rating,
            "published_date": self.published_date,
            "travel_date": self.travel_date,
            "trip_type": self.trip_type,
            "user_name": self.username,
            "user_location": self.user_location,
            "url": self.url,
            "created_at": self.created_at,
        }
