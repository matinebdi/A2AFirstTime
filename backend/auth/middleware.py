"""Authentication middleware for VacanceAI - JWT-based (Oracle)"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from auth.jwt_service import decode_token
from database.oracle_client import execute_query_single

security = HTTPBearer()


class User:
    """User model from Oracle database"""

    def __init__(self, data: dict):
        self.id = data.get("id")
        self.email = data.get("email")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.phone = data.get("phone")
        self.avatar_url = data.get("avatar_url")
        self.created_at = data.get("created_at")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Verify JWT token and return current user"""
    token = credentials.credentials

    try:
        payload = decode_token(token)

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_row = execute_query_single(
            "SELECT * FROM users WHERE id = :id",
            {"id": user_id}
        )

        if not user_row:
            raise HTTPException(status_code=401, detail="User not found")

        return User(user_row)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )


async def get_optional_user(request: Request) -> Optional[User]:
    """Return user if authenticated, None otherwise"""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    try:
        token = auth_header.replace("Bearer ", "")
        payload = decode_token(token)

        if payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user_row = execute_query_single(
            "SELECT * FROM users WHERE id = :id",
            {"id": user_id}
        )

        if user_row:
            return User(user_row)

    except Exception:
        pass

    return None
