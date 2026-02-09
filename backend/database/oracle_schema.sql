-- =============================================
-- VacanceAI - Oracle 21c XE Schema
-- Run as SYSDBA to create the VACANCEAI user,
-- then all tables are created in that schema.
-- =============================================

-- ============================================
-- STEP 1: Create dedicated user (run as SYSDBA)
-- ============================================
ALTER SESSION SET "_ORACLE_SCRIPT"=true;

-- Drop user if exists (with all objects)
BEGIN
    EXECUTE IMMEDIATE 'DROP USER VACANCEAI CASCADE';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -1918 THEN RAISE; END IF;
END;
/

CREATE USER VACANCEAI IDENTIFIED BY vacanceai
    DEFAULT TABLESPACE USERS
    TEMPORARY TABLESPACE TEMP
    QUOTA UNLIMITED ON USERS;

GRANT CONNECT, RESOURCE, CREATE VIEW, CREATE TRIGGER TO VACANCEAI;
GRANT CREATE SESSION TO VACANCEAI;

ALTER SESSION SET "_ORACLE_SCRIPT"=false;

-- ============================================
-- STEP 2: Connect as VACANCEAI and create tables
-- ============================================
-- If running manually: CONNECT VACANCEAI/vacanceai@//localhost:1521/XE
-- If running from a tool, the rest executes as SYSDBA but objects are created
-- in VACANCEAI schema via ALTER SESSION SET CURRENT_SCHEMA:
ALTER SESSION SET CURRENT_SCHEMA = VACANCEAI;

-- ============================================
-- Drop existing tables (reverse dependency order)
-- ============================================
BEGIN EXECUTE IMMEDIATE 'DROP TABLE tripadvisor_reviews CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE tripadvisor_photos CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE tripadvisor_locations CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE package_embeddings CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE conversations CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE reviews CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE favorites CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE bookings CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE packages CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE destinations CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE refresh_tokens CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE users CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/

-- ============================================
-- 1. USERS
-- ============================================
CREATE TABLE users (
    id              VARCHAR2(36) DEFAULT SYS_GUID() PRIMARY KEY,
    email           VARCHAR2(255) NOT NULL UNIQUE,
    password_hash   VARCHAR2(255) NOT NULL,
    first_name      VARCHAR2(100),
    last_name       VARCHAR2(100),
    phone           VARCHAR2(50),
    avatar_url      VARCHAR2(500),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE INDEX idx_users_email ON users(email);

-- ============================================
-- 2. REFRESH TOKENS
-- ============================================
CREATE TABLE refresh_tokens (
    id              VARCHAR2(36) DEFAULT SYS_GUID() PRIMARY KEY,
    user_id         VARCHAR2(36) NOT NULL,
    token           VARCHAR2(500) NOT NULL UNIQUE,
    expires_at      TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_refresh_tokens_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);

-- ============================================
-- 3. DESTINATIONS
-- ============================================
CREATE TABLE destinations (
    id              VARCHAR2(36) DEFAULT SYS_GUID() PRIMARY KEY,
    name            VARCHAR2(255) NOT NULL,
    country         VARCHAR2(100) NOT NULL,
    city            VARCHAR2(100),
    description     CLOB,
    image_url       VARCHAR2(500),
    tags            CLOB CHECK (tags IS JSON),
    average_rating  NUMBER(3,1) DEFAULT 0,
    total_reviews   NUMBER DEFAULT 0,
    latitude        NUMBER(10,7),
    longitude       NUMBER(10,7),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE INDEX idx_destinations_country ON destinations(country);
CREATE INDEX idx_destinations_rating ON destinations(average_rating DESC);

-- ============================================
-- 4. PACKAGES
-- ============================================
CREATE TABLE packages (
    id              VARCHAR2(36) DEFAULT SYS_GUID() PRIMARY KEY,
    destination_id  VARCHAR2(36) NOT NULL,
    name            VARCHAR2(255) NOT NULL,
    description     CLOB,
    price_per_person NUMBER(10,2) NOT NULL,
    duration_days   NUMBER NOT NULL,
    max_persons     NUMBER DEFAULT 10,
    included        CLOB CHECK (included IS JSON),
    not_included    CLOB CHECK (not_included IS JSON),
    highlights      CLOB CHECK (highlights IS JSON),
    image_url       VARCHAR2(500),
    images          CLOB CHECK (images IS JSON),
    available_from  DATE,
    available_to    DATE,
    is_active       NUMBER(1) DEFAULT 1,
    hotel_category  NUMBER(1),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_packages_destination FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);

CREATE INDEX idx_packages_destination ON packages(destination_id);
CREATE INDEX idx_packages_price ON packages(price_per_person);
CREATE INDEX idx_packages_active ON packages(is_active);
CREATE INDEX idx_packages_dates ON packages(available_from, available_to);

-- ============================================
-- 5. BOOKINGS
-- ============================================
CREATE TABLE bookings (
    id              VARCHAR2(36) DEFAULT SYS_GUID() PRIMARY KEY,
    user_id         VARCHAR2(36) NOT NULL,
    package_id      VARCHAR2(36) NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    num_persons     NUMBER NOT NULL,
    total_price     NUMBER(10,2) NOT NULL,
    status          VARCHAR2(20) DEFAULT 'pending' NOT NULL,
    payment_status  VARCHAR2(20) DEFAULT 'unpaid' NOT NULL,
    special_requests CLOB,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_bookings_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_bookings_package FOREIGN KEY (package_id) REFERENCES packages(id),
    CONSTRAINT chk_booking_status CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed')),
    CONSTRAINT chk_payment_status CHECK (payment_status IN ('unpaid', 'paid', 'refunded'))
);

CREATE INDEX idx_bookings_user ON bookings(user_id);
CREATE INDEX idx_bookings_package ON bookings(package_id);
CREATE INDEX idx_bookings_status ON bookings(status);

-- ============================================
-- 6. FAVORITES
-- ============================================
CREATE TABLE favorites (
    id              VARCHAR2(36) DEFAULT SYS_GUID() PRIMARY KEY,
    user_id         VARCHAR2(36) NOT NULL,
    package_id      VARCHAR2(36) NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_favorites_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_favorites_package FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE,
    CONSTRAINT uq_favorites UNIQUE (user_id, package_id)
);

CREATE INDEX idx_favorites_user ON favorites(user_id);

-- ============================================
-- 7. REVIEWS
-- ============================================
CREATE TABLE reviews (
    id              VARCHAR2(36) DEFAULT SYS_GUID() PRIMARY KEY,
    user_id         VARCHAR2(36) NOT NULL,
    package_id      VARCHAR2(36) NOT NULL,
    booking_id      VARCHAR2(36),
    rating          NUMBER(1) NOT NULL,
    review_comment  CLOB,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_reviews_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_reviews_package FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE,
    CONSTRAINT fk_reviews_booking FOREIGN KEY (booking_id) REFERENCES bookings(id),
    CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5)
);

CREATE INDEX idx_reviews_package ON reviews(package_id);
CREATE INDEX idx_reviews_user ON reviews(user_id);

-- ============================================
-- 8. CONVERSATIONS
-- ============================================
CREATE TABLE conversations (
    id              VARCHAR2(36) PRIMARY KEY,
    user_id         VARCHAR2(36),
    messages        CLOB CHECK (messages IS JSON),
    context         CLOB CHECK (context IS JSON),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_conversations_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_conversations_user ON conversations(user_id);

-- ============================================
-- 9. PACKAGE EMBEDDINGS (RAG - disabled for now)
-- ============================================
CREATE TABLE package_embeddings (
    id              VARCHAR2(36) DEFAULT SYS_GUID() PRIMARY KEY,
    package_id      VARCHAR2(36) NOT NULL,
    content         CLOB,
    embedding       CLOB,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_embeddings_package FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE
);

CREATE INDEX idx_embeddings_package ON package_embeddings(package_id);

-- ============================================
-- 10. TRIPADVISOR LOCATIONS
-- ============================================
CREATE TABLE tripadvisor_locations (
    id              VARCHAR2(36) DEFAULT SYS_GUID() PRIMARY KEY,
    location_id     VARCHAR2(50) NOT NULL UNIQUE,
    name            VARCHAR2(500),
    description     CLOB,
    web_url         VARCHAR2(1000),
    address_obj     CLOB CHECK (address_obj IS JSON),
    latitude        VARCHAR2(50),
    longitude       VARCHAR2(50),
    phone           VARCHAR2(100),
    website         VARCHAR2(1000),
    email           VARCHAR2(255),
    rating          NUMBER(3,1),
    num_reviews     NUMBER,
    ranking_data    VARCHAR2(500),
    price_level     VARCHAR2(50),
    search_country  VARCHAR2(100),
    search_query    VARCHAR2(255),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE INDEX idx_ta_locations_lid ON tripadvisor_locations(location_id);
CREATE INDEX idx_ta_locations_country ON tripadvisor_locations(search_country);

-- ============================================
-- 11. TRIPADVISOR PHOTOS
-- ============================================
CREATE TABLE tripadvisor_photos (
    id                  VARCHAR2(36) DEFAULT SYS_GUID() PRIMARY KEY,
    location_id         VARCHAR2(50) NOT NULL,
    photo_id            VARCHAR2(50),
    url_original        VARCHAR2(1000),
    url_large           VARCHAR2(1000),
    url_medium          VARCHAR2(1000),
    url_small           VARCHAR2(1000),
    caption             VARCHAR2(1000),
    uploaded_to_storage NUMBER(1) DEFAULT 0,
    storage_path        VARCHAR2(500),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE INDEX idx_ta_photos_location ON tripadvisor_photos(location_id);

-- ============================================
-- 12. TRIPADVISOR REVIEWS
-- ============================================
CREATE TABLE tripadvisor_reviews (
    id                  VARCHAR2(36) DEFAULT SYS_GUID() PRIMARY KEY,
    location_id         VARCHAR2(50) NOT NULL,
    review_id           VARCHAR2(50),
    title               VARCHAR2(500),
    text                CLOB,
    rating              NUMBER(1),
    published_date      TIMESTAMP WITH TIME ZONE,
    travel_date         VARCHAR2(50),
    trip_type           VARCHAR2(50),
    username            VARCHAR2(255),
    user_location       VARCHAR2(255),
    url                 VARCHAR2(1000),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE INDEX idx_ta_reviews_location ON tripadvisor_reviews(location_id);

-- ============================================
-- TRIGGERS: auto-update updated_at
-- ============================================

CREATE OR REPLACE TRIGGER trg_users_updated
    BEFORE UPDATE ON users FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/

CREATE OR REPLACE TRIGGER trg_destinations_updated
    BEFORE UPDATE ON destinations FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/

CREATE OR REPLACE TRIGGER trg_packages_updated
    BEFORE UPDATE ON packages FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/

CREATE OR REPLACE TRIGGER trg_bookings_updated
    BEFORE UPDATE ON bookings FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/

CREATE OR REPLACE TRIGGER trg_reviews_updated
    BEFORE UPDATE ON reviews FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/

CREATE OR REPLACE TRIGGER trg_conversations_updated
    BEFORE UPDATE ON conversations FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/

CREATE OR REPLACE TRIGGER trg_ta_locations_updated
    BEFORE UPDATE ON tripadvisor_locations FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/
