"""UI Agent Tools - Actions for the frontend interface"""

from langchain_core.tools import tool
from typing import Optional, List, Dict, Any
from agents.database.tools import search_packages, get_package_details


@tool
def search_vacation(
    destination: Optional[str] = None,
    budget_max: Optional[float] = None,
    duration_days: Optional[int] = None,
    travel_type: Optional[str] = None,
    num_travelers: Optional[int] = None
) -> Dict[str, Any]:
    """Search for vacation packages and display results in the interface.

    Args:
        destination: Where the user wants to go (e.g., "Maldives", "Japan", "beach")
        budget_max: Maximum budget per person in euros
        travel_type: Type of vacation (beach, mountain, city, adventure, romantic, family)
        duration_days: Preferred trip duration
        num_travelers: Number of people traveling

    Returns:
        Search results with packages to display
    """
    # Map travel_type to tags
    tags = [travel_type] if travel_type else None

    # Search packages using database tools
    packages = search_packages.invoke({
        "destination": destination,
        "max_price": budget_max,
        "max_duration": duration_days + 2 if duration_days else None,
        "min_duration": duration_days - 2 if duration_days else None,
        "tags": tags,
        "limit": 8
    })

    if not packages:
        return {
            "action": "show_message",
            "message": "Aucun package trouvé pour ces critères. Essayons avec des critères différents.",
            "suggestions": [
                "Augmenter le budget",
                "Changer la destination",
                "Modifier la durée"
            ]
        }

    return {
        "action": "show_search_results",
        "packages": packages,
        "count": len(packages),
        "filters_applied": {
            "destination": destination,
            "budget_max": budget_max,
            "duration_days": duration_days,
            "travel_type": travel_type
        }
    }


@tool
def show_package_details(package_id: str) -> Dict[str, Any]:
    """Display detailed information about a specific package.

    Args:
        package_id: UUID of the package to display

    Returns:
        Package details for display
    """
    package = get_package_details.invoke({"package_id": package_id})

    if "error" in package:
        return {
            "action": "show_error",
            "message": "Package non trouvé"
        }

    return {
        "action": "show_package_modal",
        "package": package
    }


@tool
def start_booking_flow(
    package_id: str,
    start_date: Optional[str] = None,
    num_persons: Optional[int] = None
) -> Dict[str, Any]:
    """Start the booking process for a package.

    Args:
        package_id: UUID of the package to book
        start_date: Optional pre-filled start date (YYYY-MM-DD)
        num_persons: Optional pre-filled number of travelers

    Returns:
        Booking form state
    """
    package = get_package_details.invoke({"package_id": package_id})

    if "error" in package:
        return {
            "action": "show_error",
            "message": "Package non trouvé"
        }

    return {
        "action": "open_booking_form",
        "package": package,
        "prefill": {
            "start_date": start_date,
            "num_persons": num_persons or 2
        },
        "total_estimate": package.get("price_per_person", 0) * (num_persons or 2)
    }


@tool
def add_to_favorites_action(package_id: str) -> Dict[str, Any]:
    """Add a package to the user's favorites (UI action).

    Args:
        package_id: UUID of the package

    Returns:
        Action result for UI update
    """
    return {
        "action": "add_favorite",
        "package_id": package_id,
        "message": "Ajouté aux favoris!"
    }


@tool
def navigate_to_page(page: str) -> Dict[str, Any]:
    """Navigate to a specific page in the application.

    Args:
        page: Page to navigate to (home, search, bookings, favorites, profile)

    Returns:
        Navigation action
    """
    valid_pages = ["home", "search", "bookings", "favorites", "profile"]

    if page.lower() not in valid_pages:
        return {
            "action": "show_error",
            "message": f"Page inconnue. Pages disponibles: {', '.join(valid_pages)}"
        }

    return {
        "action": "navigate",
        "page": page.lower()
    }


@tool
def get_current_page_state() -> Dict[str, Any]:
    """Get the current state of the page (what the user is viewing).

    Returns:
        Current page state information
    """
    # This would be populated by the frontend
    return {
        "action": "get_state",
        "note": "State will be provided by frontend context"
    }


@tool
def show_recommendations(
    preferences: Optional[List[str]] = None,
    budget_range: Optional[str] = None
) -> Dict[str, Any]:
    """Show personalized vacation recommendations.

    Args:
        preferences: User preferences (beach, adventure, culture, etc.)
        budget_range: Budget range (low, medium, high, luxury)

    Returns:
        Recommended packages
    """
    # Map budget range to price
    budget_map = {
        "low": (0, 800),
        "medium": (800, 1500),
        "high": (1500, 2500),
        "luxury": (2500, None)
    }

    min_price, max_price = budget_map.get(budget_range, (None, None))

    packages = search_packages.invoke({
        "min_price": min_price,
        "max_price": max_price,
        "tags": preferences,
        "limit": 6
    })

    return {
        "action": "show_recommendations",
        "packages": packages,
        "personalized": True,
        "preferences": preferences,
        "budget_range": budget_range
    }
