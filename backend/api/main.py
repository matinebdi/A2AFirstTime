"""VacanceAI Backend - Main FastAPI Application"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from logging_config import setup_logging
from database.session import init_engine, close_engine
from telemetry import init_telemetry

logger = logging.getLogger("vacanceai")
from .routes import health, auth, destinations, packages, bookings, favorites, reviews, conversations, tripadvisor
from a2a.server import a2a_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    setup_logging()
    logger.info("Starting %s API...", settings.app_name)
    init_engine()
    init_telemetry(app)
    yield
    # Shutdown
    logger.info("Shutting down %s API...", settings.app_name)
    close_engine()


app = FastAPI(
    title="VacanceAI API",
    description="""
    VacanceAI - Vacation Booking Platform API

    ## Features
    - Browse destinations and vacation packages
    - Book all-inclusive vacation packages
    - User authentication via JWT
    - AI-powered vacation assistant via chat
    - Google A2A Protocol for agent communication

    ## Authentication
    Most endpoints require a Bearer token (JWT).
    Use `/auth/login` to get your access token.
    """,
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(destinations.router, prefix="/api/destinations", tags=["Destinations"])
app.include_router(packages.router, prefix="/api/packages", tags=["Packages"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["Chat Assistant"])
app.include_router(tripadvisor.router, prefix="/api/tripadvisor", tags=["TripAdvisor"])
app.include_router(a2a_router, tags=["A2A Protocol"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/swagger",
        "health": "/api/health"
    }
