"""Favorites routes - Oracle"""

import uuid
from fastapi import APIRouter, HTTPException, Depends

from database.oracle_client import execute_query, execute_query_single, execute_insert, execute_delete
from database.queries import (
    FAVORITES_BY_USER, FAVORITE_INSERT, FAVORITE_CHECK, FAVORITE_DELETE,
    PACKAGE_SIMPLE, format_favorite_with_joins
)
from auth.middleware import get_current_user

router = APIRouter()


@router.get("/")
async def list_favorites(user=Depends(get_current_user)):
    """List user's favorite packages"""
    rows = execute_query(FAVORITES_BY_USER, {"user_id": user.id})
    favorites = [format_favorite_with_joins(r) for r in rows]
    return {"favorites": favorites}


@router.post("/{package_id}")
async def add_favorite(package_id: str, user=Depends(get_current_user)):
    """Add a package to favorites"""
    # Check if package exists
    package = execute_query_single(PACKAGE_SIMPLE, {"id": package_id})
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Check if already in favorites
    existing = execute_query_single(FAVORITE_CHECK, {
        "user_id": user.id,
        "package_id": package_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")

    fav_id = str(uuid.uuid4())
    execute_insert(FAVORITE_INSERT, {
        "id": fav_id,
        "user_id": user.id,
        "package_id": package_id
    })

    return {"message": "Added to favorites", "favorite": {"id": fav_id, "package_id": package_id}}


@router.delete("/{package_id}")
async def remove_favorite(package_id: str, user=Depends(get_current_user)):
    """Remove a package from favorites"""
    count = execute_delete(FAVORITE_DELETE, {
        "user_id": user.id,
        "package_id": package_id
    })

    if count == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")

    return {"message": "Removed from favorites"}


@router.get("/check/{package_id}")
async def check_favorite(package_id: str, user=Depends(get_current_user)):
    """Check if a package is in favorites"""
    existing = execute_query_single(FAVORITE_CHECK, {
        "user_id": user.id,
        "package_id": package_id
    })
    return {"is_favorite": existing is not None}
