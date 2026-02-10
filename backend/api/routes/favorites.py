"""Favorites routes - SQLAlchemy ORM"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload

from database.session import get_db
from database.models import Favorite, Package
from auth.middleware import get_current_user

router = APIRouter()


@router.get("/")
async def list_favorites(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user's favorite packages"""
    rows = (
        db.query(Favorite)
        .options(joinedload(Favorite.package).joinedload(Package.destination))
        .filter(Favorite.user_id == user.id)
        .all()
    )
    favorites = [f.to_dict_with_joins() for f in rows]
    return {"favorites": favorites}


@router.post("/{package_id}")
async def add_favorite(
    package_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a package to favorites"""
    package = db.query(Package).filter(Package.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.package_id == package_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")

    fav_id = str(uuid.uuid4())
    fav = Favorite(id=fav_id, user_id=user.id, package_id=package_id)
    db.add(fav)
    db.commit()

    return {"message": "Added to favorites", "favorite": {"id": fav_id, "package_id": package_id}}


@router.delete("/{package_id}")
async def remove_favorite(
    package_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a package from favorites"""
    count = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.package_id == package_id)
        .delete()
    )
    db.commit()

    if count == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")

    return {"message": "Removed from favorites"}


@router.get("/check/{package_id}")
async def check_favorite(
    package_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if a package is in favorites"""
    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.package_id == package_id)
        .first()
    )
    return {"is_favorite": existing is not None}
