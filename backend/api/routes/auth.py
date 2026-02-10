"""Authentication routes - JWT-based with Oracle"""

import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone

from database.oracle_client import execute_query_single, execute_insert, execute_update, execute_delete
from database.queries import USER_BY_EMAIL, USER_INSERT, USER_SELECT, USER_UPDATE, REFRESH_TOKEN_INSERT, REFRESH_TOKEN_SELECT, REFRESH_TOKEN_DELETE, REFRESH_TOKEN_DELETE_USER
from auth.jwt_service import hash_password, verify_password, create_access_token, create_refresh_token
from auth.middleware import get_current_user

router = APIRouter()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UpdateProfileRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None


@router.post("/signup")
async def signup(request: SignUpRequest):
    """Register a new user"""
    # Check if email already exists
    existing = execute_query_single(USER_BY_EMAIL, {"email": request.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        user_id = str(uuid.uuid4())
        hashed = hash_password(request.password)

        execute_insert(USER_INSERT, {
            "id": user_id,
            "email": request.email,
            "password_hash": hashed,
            "first_name": request.first_name,
            "last_name": request.last_name,
        })

        return {
            "message": "User created successfully",
            "user_id": user_id,
            "email": request.email
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(request: LoginRequest):
    """Login with email and password"""
    user = execute_query_single(USER_BY_EMAIL, {"email": request.email})

    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create tokens
    access_token = create_access_token(user["id"], user["email"])
    refresh_token, refresh_expires = create_refresh_token(user["id"])

    # Store refresh token
    execute_insert(REFRESH_TOKEN_INSERT, {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "token": refresh_token,
        "expires_at": refresh_expires,
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 3600,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name")
        }
    }


@router.post("/logout")
async def logout(user=Depends(get_current_user)):
    """Logout current user - delete all refresh tokens"""
    execute_delete(REFRESH_TOKEN_DELETE_USER, {"user_id": user.id})
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(request: RefreshRequest):
    """Refresh access token"""
    # Find valid refresh token
    token_row = execute_query_single(REFRESH_TOKEN_SELECT, {"token": request.refresh_token})

    if not token_row:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = execute_query_single(USER_SELECT, {"id": token_row["user_id"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Delete old refresh token
    execute_delete(REFRESH_TOKEN_DELETE, {"token": request.refresh_token})

    # Create new tokens
    access_token = create_access_token(user["id"], user["email"])
    new_refresh, refresh_expires = create_refresh_token(user["id"])

    execute_insert(REFRESH_TOKEN_INSERT, {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "token": new_refresh,
        "expires_at": refresh_expires,
    })

    return {
        "access_token": access_token,
        "refresh_token": new_refresh,
        "expires_in": 3600
    }


@router.get("/me")
async def get_current_user_profile(user=Depends(get_current_user)):
    """Get current user's profile"""
    result = execute_query_single(USER_SELECT, {"id": user.id})

    if not result:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Don't return password hash
    result.pop("password_hash", None)
    return result


@router.patch("/me")
async def update_profile(
    request: UpdateProfileRequest,
    user=Depends(get_current_user)
):
    """Update current user's profile"""
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    update_data["id"] = user.id

    execute_update(USER_UPDATE, update_data)

    result = execute_query_single(USER_SELECT, {"id": user.id})
    result.pop("password_hash", None)

    return {"message": "Profile updated", "profile": result}


AVATAR_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "avatars")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_SIZE = 2 * 1024 * 1024  # 2 MB


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    """Upload user avatar image"""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Format non supporte. Utilisez JPG, PNG ou WebP.")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image trop volumineuse (max 2 Mo)")

    os.makedirs(AVATAR_DIR, exist_ok=True)

    # Remove old avatar if exists
    for old_ext in ALLOWED_EXTENSIONS:
        old_path = os.path.join(AVATAR_DIR, f"{user.id}{old_ext}")
        if os.path.exists(old_path):
            os.remove(old_path)

    filename = f"{user.id}{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    avatar_url = f"/api/auth/avatar/{filename}"
    execute_update(USER_UPDATE, {"id": user.id, "avatar_url": avatar_url})

    return {"avatar_url": avatar_url}


@router.get("/avatar/{filename}")
async def get_avatar(filename: str):
    """Serve avatar image"""
    # Sanitize filename to prevent path traversal
    safe_name = os.path.basename(filename)
    filepath = os.path.join(AVATAR_DIR, safe_name)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Avatar not found")
    return FileResponse(filepath)
