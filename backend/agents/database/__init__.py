"""Database Agent - Handles all Oracle database operations"""
from .agent import database_agent, invoke_database_agent
from .tools import (
    search_packages,
    get_package_details,
    get_destinations,
    create_booking,
    get_user_bookings,
    add_to_favorites,
    get_user_favorites,
    remove_from_favorites
)

__all__ = [
    "database_agent",
    "invoke_database_agent",
    "search_packages",
    "get_package_details",
    "get_destinations",
    "create_booking",
    "get_user_bookings",
    "add_to_favorites",
    "get_user_favorites",
    "remove_from_favorites"
]
