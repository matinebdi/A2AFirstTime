"""
Seed Oracle DB with TripAdvisor data + Destinations + Packages.

Usage:
    python scripts/seed_oracle.py

Env vars (all optional, with defaults):
    ORACLE_HOST      (default: localhost)
    ORACLE_PORT      (default: 1521)
    ORACLE_SERVICE   (default: XE)
    ORACLE_USER      (default: VACANCEAI)
    ORACLE_PASSWORD  (default: vacanceai)
    TRIPADVISOR_API_KEY (default: built-in key)
"""

import json
import os
import random
import sys
import time
import uuid
from datetime import datetime, date

import oracledb
import requests

# ============================================
# Configuration
# ============================================

ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = os.getenv("ORACLE_PORT", "1521")
ORACLE_SERVICE = os.getenv("ORACLE_SERVICE", "XE")
ORACLE_USER = os.getenv("ORACLE_USER", "VACANCEAI")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "vacanceai")

API_KEY = os.getenv("TRIPADVISOR_API_KEY", "DA14AFDC474F4EE8962B0E3B2449D714")
API_BASE = "https://api.content.tripadvisor.com/api/v1"
API_HEADERS = {
    "accept": "application/json",
    "Referer": "https://tripadvisor-content-api.readme.io/",
    "Origin": "https://tripadvisor-content-api.readme.io",
}
API_DELAY = 0.2  # seconds between API calls

COUNTRIES = [
    "France", "Spain", "Italy", "Portugal", "Greece",
    "Morocco", "Thailand", "Mexico", "Japan", "USA",
    "Brazil", "Australia", "Indonesia", "Turkey", "Egypt",
]

COUNTRY_DATA = {
    "France":    {"city": "Paris",      "lat": 48.8566,  "lon": 2.3522,    "desc": "Discover the magic of France — from the iconic Eiffel Tower and world-class cuisine in Paris to the sun-kissed vineyards of Provence and the glamorous French Riviera.", "tags": ["culture", "cuisine", "romance", "history"]},
    "Spain":     {"city": "Barcelona",  "lat": 41.3851,  "lon": 2.1734,    "desc": "Experience Spain's vibrant energy — explore Gaudi's masterpieces in Barcelona, savor tapas in Madrid, and unwind on the stunning Costa del Sol beaches.", "tags": ["beach", "culture", "nightlife", "cuisine"]},
    "Italy":     {"city": "Rome",       "lat": 41.9028,  "lon": 12.4964,   "desc": "Italy awaits with ancient ruins in Rome, romantic canals of Venice, Renaissance art in Florence, and the breathtaking Amalfi Coast.", "tags": ["history", "cuisine", "art", "romance"]},
    "Portugal":  {"city": "Lisbon",     "lat": 38.7223,  "lon": -9.1393,   "desc": "Portugal offers charming Lisbon streets, Porto's port wine cellars, the golden beaches of the Algarve, and unforgettable pastéis de nata.", "tags": ["beach", "culture", "cuisine", "affordable"]},
    "Greece":    {"city": "Athens",     "lat": 37.9838,  "lon": 23.7275,   "desc": "Greece blends ancient history with stunning island beauty — explore the Acropolis in Athens, then island-hop through Santorini and Mykonos.", "tags": ["beach", "history", "islands", "cuisine"]},
    "Morocco":   {"city": "Marrakech",  "lat": 31.6295,  "lon": -7.9811,   "desc": "Morocco enchants with Marrakech's vibrant souks, the Sahara desert, the blue city of Chefchaouen, and aromatic Moroccan cuisine.", "tags": ["culture", "adventure", "desert", "cuisine"]},
    "Thailand":  {"city": "Bangkok",    "lat": 13.7563,  "lon": 100.5018,  "desc": "Thailand dazzles with Bangkok's ornate temples, tropical beaches in Phuket and Krabi, vibrant night markets, and legendary street food.", "tags": ["beach", "culture", "cuisine", "affordable"]},
    "Mexico":    {"city": "Cancun",     "lat": 21.1619,  "lon": -86.8515,  "desc": "Mexico offers Caribbean beaches in Cancun, ancient Mayan ruins at Chichen Itza, colorful cities like Oaxaca, and world-famous tacos.", "tags": ["beach", "history", "culture", "cuisine"]},
    "Japan":     {"city": "Tokyo",      "lat": 35.6762,  "lon": 139.6503,  "desc": "Japan merges ultra-modern Tokyo with serene Kyoto temples, cherry blossoms, Mount Fuji, and an unmatched culinary tradition.", "tags": ["culture", "cuisine", "technology", "nature"]},
    "USA":       {"city": "New York",   "lat": 40.7128,  "lon": -74.0060,  "desc": "The USA spans from New York's skyline to California's beaches, the Grand Canyon's majesty, and vibrant cities like Miami and Las Vegas.", "tags": ["city", "entertainment", "nature", "diversity"]},
    "Brazil":    {"city": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729, "desc": "Brazil pulses with Rio's carnival energy, Copacabana beach, the Amazon rainforest, and Iguazu Falls — a feast for all senses.", "tags": ["beach", "nature", "carnival", "adventure"]},
    "Australia": {"city": "Sydney",     "lat": -33.8688, "lon": 151.2093,  "desc": "Australia amazes with Sydney's harbour, the Great Barrier Reef, the Outback, and a laid-back lifestyle paired with world-class dining.", "tags": ["beach", "nature", "adventure", "diving"]},
    "Indonesia": {"city": "Bali",       "lat": -8.3405,  "lon": 115.0920,  "desc": "Indonesia is a tropical paradise — Bali's rice terraces and temples, Komodo dragons, Raja Ampat diving, and warm hospitality.", "tags": ["beach", "culture", "nature", "affordable"]},
    "Turkey":    {"city": "Istanbul",   "lat": 41.0082,  "lon": 28.9784,   "desc": "Turkey bridges East and West — Istanbul's grand bazaars, Cappadocia's fairy chimneys, turquoise coast beaches, and rich Ottoman heritage.", "tags": ["culture", "history", "beach", "cuisine"]},
    "Egypt":     {"city": "Cairo",      "lat": 30.0444,  "lon": 31.2357,   "desc": "Egypt holds the Pyramids of Giza, the Sphinx, a Nile cruise through ancient temples, and the Red Sea's spectacular coral reefs.", "tags": ["history", "adventure", "desert", "diving"]},
}

# Package templates: 2 per country (budget / premium)
PACKAGE_TEMPLATES = [
    {
        "suffix": "Explorer",
        "duration": 7,
        "price_range": (799, 1299),
        "hotel_cat": 3,
        "max_persons": 12,
        "included": {
            "transport": "Round-trip economy flights",
            "hotel": "3-star hotel, double room",
            "meals": "Daily breakfast included",
            "activities": ["Guided city tour", "Museum entrance tickets", "Local market visit"],
            "transfers": "Airport transfers included",
        },
        "not_included": ["Travel insurance", "Lunch and dinner", "Personal expenses", "Optional excursions"],
        "highlights": ["Discover iconic landmarks", "Local cuisine tasting", "Guided walking tour", "Free time for shopping"],
    },
    {
        "suffix": "Premium",
        "duration": 10,
        "price_range": (1599, 2499),
        "hotel_cat": 5,
        "max_persons": 8,
        "included": {
            "transport": "Round-trip business class flights",
            "hotel": "5-star luxury resort, suite",
            "meals": "Full board — breakfast, lunch & dinner",
            "activities": ["Private guided tours", "Spa & wellness session", "Exclusive cultural experience", "Sunset cruise"],
            "transfers": "Private luxury transfers",
        },
        "not_included": ["Travel insurance", "Personal shopping", "Premium excursions", "Minibar"],
        "highlights": ["VIP experiences", "Gourmet dining", "Luxury spa retreat", "Private cultural immersion", "Scenic helicopter tour"],
    },
]


# ============================================
# Oracle connection with retry
# ============================================

def get_connection(max_retries=3, delay=5):
    """Connect to Oracle with retry logic."""
    dsn = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}"
    for attempt in range(1, max_retries + 1):
        try:
            conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=dsn)
            print(f"Connected to Oracle: {ORACLE_USER}@{dsn}")
            return conn
        except oracledb.Error as e:
            print(f"Connection attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(delay)
    print("ERROR: Could not connect to Oracle after retries.")
    sys.exit(1)


# ============================================
# Phase 1: Fetch TripAdvisor API
# ============================================

def fetch_locations():
    """Fetch hotel locations from TripAdvisor for each country."""
    all_locations = []
    for country in COUNTRIES:
        url = f"{API_BASE}/location/search?key={API_KEY}&searchQuery={country}&category=hotels&language=en"
        try:
            resp = requests.get(url, headers=API_HEADERS, timeout=15)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                for item in data:
                    item["search_country"] = country
                all_locations.extend(data)
                print(f"  {country}: {len(data)} locations")
            else:
                print(f"  {country}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"  {country}: ERROR {e}")
        time.sleep(API_DELAY)
    return all_locations


def fetch_details(locations):
    """Fetch detailed info for each location."""
    for loc in locations:
        lid = loc["location_id"]
        url = f"{API_BASE}/location/{lid}/details?key={API_KEY}&language=en&currency=EUR"
        try:
            resp = requests.get(url, headers=API_HEADERS, timeout=15)
            if resp.status_code == 200:
                details = resp.json()
                loc["description"] = details.get("description", "")
                loc["web_url"] = details.get("web_url", "")
                loc["rating"] = details.get("rating")
                loc["num_reviews"] = details.get("num_reviews")
                loc["phone"] = details.get("phone", "")
                loc["website"] = details.get("website", "")
                loc["email"] = details.get("email", "")
                loc["latitude"] = details.get("latitude", "")
                loc["longitude"] = details.get("longitude", "")
                loc["ranking_data"] = details.get("ranking_data", {}).get("ranking_string", "")
                loc["price_level"] = details.get("price_level", "")
        except Exception as e:
            print(f"  Details {lid}: ERROR {e}")
        time.sleep(API_DELAY)
    return locations


def fetch_photos(location_ids):
    """Fetch photos for each location."""
    all_photos = []
    for lid in location_ids:
        url = f"{API_BASE}/location/{lid}/photos?key={API_KEY}&language=en"
        try:
            resp = requests.get(url, headers=API_HEADERS, timeout=15)
            if resp.status_code == 200:
                photos = resp.json().get("data", [])
                for p in photos:
                    p["location_id"] = lid
                all_photos.extend(photos)
        except Exception as e:
            print(f"  Photos {lid}: ERROR {e}")
        time.sleep(API_DELAY)
    print(f"  Total photos fetched: {len(all_photos)}")
    return all_photos


def fetch_reviews(location_ids):
    """Fetch reviews for each location."""
    all_reviews = []
    for lid in location_ids:
        url = f"{API_BASE}/location/{lid}/reviews?key={API_KEY}&language=en&limit=10"
        try:
            resp = requests.get(url, headers=API_HEADERS, timeout=15)
            if resp.status_code == 200:
                reviews = resp.json().get("data", [])
                for r in reviews:
                    r["location_id"] = lid
                all_reviews.extend(reviews)
        except Exception as e:
            print(f"  Reviews {lid}: ERROR {e}")
        time.sleep(API_DELAY)
    print(f"  Total reviews fetched: {len(all_reviews)}")
    return all_reviews


# ============================================
# Phase 2: Insert TripAdvisor data into Oracle
# ============================================

def insert_ta_locations(conn, locations):
    """Insert TripAdvisor locations into Oracle."""
    sql = """
        INSERT INTO tripadvisor_locations
            (location_id, name, description, web_url, address_obj,
             latitude, longitude, phone, website, email,
             rating, num_reviews, ranking_data, price_level,
             search_country, search_query)
        VALUES
            (:location_id, :name, :description, :web_url, :address_obj,
             :latitude, :longitude, :phone, :website, :email,
             :rating, :num_reviews, :ranking_data, :price_level,
             :search_country, :search_query)
    """
    rows = []
    for loc in locations:
        addr = loc.get("address_obj")
        if isinstance(addr, dict):
            addr_json = json.dumps(addr, ensure_ascii=False)
        elif isinstance(addr, str):
            addr_json = addr
        else:
            addr_json = "{}"

        rating_val = loc.get("rating")
        if rating_val is not None:
            try:
                rating_val = float(rating_val)
            except (ValueError, TypeError):
                rating_val = None

        num_reviews_val = loc.get("num_reviews")
        if num_reviews_val is not None:
            try:
                num_reviews_val = int(num_reviews_val)
            except (ValueError, TypeError):
                num_reviews_val = None

        rows.append({
            "location_id": str(loc["location_id"]),
            "name": loc.get("name", ""),
            "description": loc.get("description", ""),
            "web_url": loc.get("web_url", ""),
            "address_obj": addr_json,
            "latitude": str(loc.get("latitude", "")),
            "longitude": str(loc.get("longitude", "")),
            "phone": loc.get("phone", ""),
            "website": (loc.get("website", "") or "")[:1000],
            "email": loc.get("email", ""),
            "rating": rating_val,
            "num_reviews": num_reviews_val,
            "ranking_data": (loc.get("ranking_data", "") or "")[:500],
            "price_level": loc.get("price_level", ""),
            "search_country": loc.get("search_country", ""),
            "search_query": loc.get("search_country", ""),
        })

    cursor = conn.cursor()
    cursor.setinputsizes(description=oracledb.DB_TYPE_CLOB, address_obj=oracledb.DB_TYPE_CLOB)
    cursor.executemany(sql, rows, batcherrors=True)
    errors = cursor.getbatcherrors()
    conn.commit()
    if errors:
        for e in errors:
            print(f"    Location batch error at row {e.offset}: {e.message}")
    print(f"  Inserted {len(rows) - len(errors)} / {len(rows)} locations")
    return rows


def insert_ta_photos(conn, photos):
    """Insert TripAdvisor photos into Oracle."""
    sql = """
        INSERT INTO tripadvisor_photos
            (location_id, photo_id, url_original, url_large, url_medium, url_small,
             caption, uploaded_to_storage)
        VALUES
            (:location_id, :photo_id, :url_original, :url_large, :url_medium, :url_small,
             :caption, 0)
    """
    rows = []
    for p in photos:
        images = p.get("images", {})
        if not isinstance(images, dict):
            images = {}
        rows.append({
            "location_id": str(p["location_id"]),
            "photo_id": str(p.get("id", "")),
            "url_original": images.get("original", {}).get("url", "") if isinstance(images.get("original"), dict) else "",
            "url_large": images.get("large", {}).get("url", "") if isinstance(images.get("large"), dict) else "",
            "url_medium": images.get("medium", {}).get("url", "") if isinstance(images.get("medium"), dict) else "",
            "url_small": images.get("small", {}).get("url", "") if isinstance(images.get("small"), dict) else "",
            "caption": (p.get("caption", "") or "")[:1000],
        })

    cursor = conn.cursor()
    cursor.executemany(sql, rows, batcherrors=True)
    errors = cursor.getbatcherrors()
    conn.commit()
    if errors:
        for e in errors:
            print(f"    Photo batch error at row {e.offset}: {e.message}")
    print(f"  Inserted {len(rows) - len(errors)} / {len(rows)} photos")
    return rows


def insert_ta_reviews(conn, reviews):
    """Insert TripAdvisor reviews into Oracle."""
    sql = """
        INSERT INTO tripadvisor_reviews
            (location_id, review_id, title, text, rating,
             published_date, travel_date, trip_type,
             username, user_location, url)
        VALUES
            (:location_id, :review_id, :title, :text, :rating,
             :published_date, :travel_date, :trip_type,
             :username, :user_location, :url)
    """
    rows = []
    for r in reviews:
        # Parse published_date ISO string to datetime
        pub_date = None
        pub_str = r.get("published_date", "")
        if pub_str:
            try:
                pub_date = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        rating_val = r.get("rating")
        if rating_val is not None:
            try:
                rating_val = int(rating_val)
            except (ValueError, TypeError):
                rating_val = None

        user_info = r.get("user", {})
        if not isinstance(user_info, dict):
            user_info = {}

        user_loc = user_info.get("user_location", {})
        user_loc_name = ""
        if isinstance(user_loc, dict):
            user_loc_name = user_loc.get("name", "")
        elif isinstance(user_loc, str):
            user_loc_name = user_loc

        rows.append({
            "location_id": str(r["location_id"]),
            "review_id": str(r.get("id", "")),
            "title": (r.get("title", "") or "")[:500],
            "text": r.get("text", "") or "",
            "rating": rating_val,
            "published_date": pub_date,
            "travel_date": (r.get("travel_date", "") or "")[:50],
            "trip_type": (r.get("trip_type", "") or "")[:50],
            "username": (user_info.get("username", "") or "")[:255],
            "user_location": (user_loc_name or "")[:255],
            "url": (r.get("url", "") or "")[:1000],
        })

    cursor = conn.cursor()
    cursor.setinputsizes(text=oracledb.DB_TYPE_CLOB)
    cursor.executemany(sql, rows, batcherrors=True)
    errors = cursor.getbatcherrors()
    conn.commit()
    if errors:
        for e in errors:
            print(f"    Review batch error at row {e.offset}: {e.message}")
    print(f"  Inserted {len(rows) - len(errors)} / {len(rows)} reviews")
    return rows


# ============================================
# Phase 3: Seed Destinations + Packages
# ============================================

def get_country_photos(photo_rows, location_rows):
    """Build a mapping of country -> list of photo URLs from the inserted data."""
    # Map location_id -> search_country
    loc_to_country = {}
    for loc in location_rows:
        loc_to_country[loc["location_id"]] = loc["search_country"]

    country_photos = {c: [] for c in COUNTRIES}
    for p in photo_rows:
        country = loc_to_country.get(p["location_id"])
        if country:
            url = p.get("url_large") or p.get("url_medium") or p.get("url_original") or ""
            if url:
                country_photos[country].append(url)
    return country_photos


def seed_destinations(conn, country_photos):
    """Insert 15 destinations (1 per country) and return list of {id, country}."""
    sql = """
        INSERT INTO destinations
            (id, name, country, city, description, image_url, tags,
             average_rating, total_reviews, latitude, longitude)
        VALUES
            (:id, :name, :country, :city, :description, :image_url, :tags,
             :average_rating, :total_reviews, :latitude, :longitude)
    """
    rows = []
    dest_map = {}  # country -> uuid

    for country in COUNTRIES:
        data = COUNTRY_DATA[country]
        dest_id = str(uuid.uuid4())
        dest_map[country] = dest_id

        photos = country_photos.get(country, [])
        image_url = photos[0] if photos else ""

        rows.append({
            "id": dest_id,
            "name": f"{data['city']}, {country}",
            "country": country,
            "city": data["city"],
            "description": data["desc"],
            "image_url": image_url,
            "tags": json.dumps(data["tags"]),
            "average_rating": 0,
            "total_reviews": 0,
            "latitude": data["lat"],
            "longitude": data["lon"],
        })

    cursor = conn.cursor()
    cursor.setinputsizes(description=oracledb.DB_TYPE_CLOB, tags=oracledb.DB_TYPE_CLOB)
    cursor.executemany(sql, rows, batcherrors=True)
    errors = cursor.getbatcherrors()
    conn.commit()
    if errors:
        for e in errors:
            print(f"    Destination batch error at row {e.offset}: {e.message}")
    print(f"  Inserted {len(rows) - len(errors)} / {len(rows)} destinations")
    return dest_map


def seed_packages(conn, dest_map, country_photos):
    """Insert 30 packages (2 per country: explorer + premium)."""
    sql = """
        INSERT INTO packages
            (id, destination_id, name, description, price_per_person,
             duration_days, max_persons, included, not_included, highlights,
             image_url, images, available_from, available_to,
             is_active, hotel_category)
        VALUES
            (:id, :destination_id, :name, :description, :price_per_person,
             :duration_days, :max_persons, :included, :not_included, :highlights,
             :image_url, :images, TO_DATE(:available_from, 'YYYY-MM-DD'), TO_DATE(:available_to, 'YYYY-MM-DD'),
             1, :hotel_category)
    """
    rows = []
    random.seed(42)

    for country in COUNTRIES:
        dest_id = dest_map.get(country)
        if not dest_id:
            continue

        data = COUNTRY_DATA[country]
        photos = country_photos.get(country, [])

        for tmpl in PACKAGE_TEMPLATES:
            pkg_id = str(uuid.uuid4())
            price_lo, price_hi = tmpl["price_range"]
            price = random.randint(price_lo, price_hi)

            # Pick 3-5 photos for this package
            pkg_photos = photos[:5] if len(photos) >= 5 else photos[:]
            image_url = pkg_photos[0] if pkg_photos else ""

            pkg_name = f"{data['city']} {tmpl['suffix']} — {tmpl['duration']} days"
            pkg_desc = (
                f"{'Explore' if tmpl['suffix'] == 'Explorer' else 'Experience the luxury of'} "
                f"{data['city']}, {country} on this {tmpl['duration']}-day "
                f"{'adventure' if tmpl['suffix'] == 'Explorer' else 'premium getaway'}. "
                f"{data['desc']}"
            )

            rows.append({
                "id": pkg_id,
                "destination_id": dest_id,
                "name": pkg_name,
                "description": pkg_desc,
                "price_per_person": price,
                "duration_days": tmpl["duration"],
                "max_persons": tmpl["max_persons"],
                "included": json.dumps(tmpl["included"], ensure_ascii=False),
                "not_included": json.dumps(tmpl["not_included"], ensure_ascii=False),
                "highlights": json.dumps(tmpl["highlights"], ensure_ascii=False),
                "image_url": image_url,
                "images": json.dumps(pkg_photos),
                "available_from": "2025-01-01",
                "available_to": "2025-12-31",
                "hotel_category": tmpl["hotel_cat"],
            })

    cursor = conn.cursor()
    cursor.setinputsizes(
        description=oracledb.DB_TYPE_CLOB,
        included=oracledb.DB_TYPE_CLOB,
        not_included=oracledb.DB_TYPE_CLOB,
        highlights=oracledb.DB_TYPE_CLOB,
        images=oracledb.DB_TYPE_CLOB,
    )
    cursor.executemany(sql, rows, batcherrors=True)
    errors = cursor.getbatcherrors()
    conn.commit()
    if errors:
        for e in errors:
            print(f"    Package batch error at row {e.offset}: {e.message}")
    print(f"  Inserted {len(rows) - len(errors)} / {len(rows)} packages")


# ============================================
# Phase 4: Verification
# ============================================

def verify(conn):
    """Print row counts for seeded tables."""
    tables = [
        "tripadvisor_locations",
        "tripadvisor_photos",
        "tripadvisor_reviews",
        "destinations",
        "packages",
    ]
    cursor = conn.cursor()
    print("\n  Table counts:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"    {table:30s} {count}")


# ============================================
# Cleanup (idempotent re-run)
# ============================================

def cleanup(conn):
    """Delete all data from target tables in FK-safe order."""
    tables = [
        "tripadvisor_reviews",
        "tripadvisor_photos",
        "tripadvisor_locations",
        "packages",
        "destinations",
    ]
    cursor = conn.cursor()
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        print(f"  Cleared {table} ({cursor.rowcount} rows)")
    conn.commit()


# ============================================
# Main
# ============================================

def main():
    print("=" * 60)
    print("VacanceAI — Oracle Database Seeder")
    print("=" * 60)

    conn = get_connection()

    # Cleanup for idempotence
    print("\n[0/4] Cleaning existing data...")
    cleanup(conn)

    # Phase 1: Fetch TripAdvisor
    print("\n[1/4] Fetching TripAdvisor locations...")
    locations = fetch_locations()
    print(f"  Total locations: {len(locations)}")

    location_ids = [str(loc["location_id"]) for loc in locations]

    print("\n[1/4] Fetching TripAdvisor details...")
    locations = fetch_details(locations)

    print("\n[1/4] Fetching TripAdvisor photos...")
    photos = fetch_photos(location_ids)

    print("\n[1/4] Fetching TripAdvisor reviews...")
    reviews = fetch_reviews(location_ids)

    # Phase 2: Insert TripAdvisor data
    print("\n[2/4] Inserting TripAdvisor locations...")
    loc_rows = insert_ta_locations(conn, locations)

    print("\n[2/4] Inserting TripAdvisor photos...")
    photo_rows = insert_ta_photos(conn, photos)

    print("\n[2/4] Inserting TripAdvisor reviews...")
    insert_ta_reviews(conn, reviews)

    # Phase 3: Seed destinations + packages
    print("\n[3/4] Building country photo map...")
    country_photos = get_country_photos(photo_rows, loc_rows)

    print("\n[3/4] Seeding destinations...")
    dest_map = seed_destinations(conn, country_photos)

    print("\n[3/4] Seeding packages...")
    seed_packages(conn, dest_map, country_photos)

    # Phase 4: Verify
    print("\n[4/4] Verification...")
    verify(conn)

    conn.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
