"""Authentication middleware for VacanceAI - JWT-based (Oracle)"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy.orm import Session

from auth.jwt_service import decode_token
from database.session import get_db
from database.models import User as UserModel

security = HTTPBearer()


class User:
    """User model from Oracle database"""

    def __init__(self, model: UserModel):
        self.id = model.id
        self.email = model.email
        self.first_name = model.first_name
        self.last_name = model.last_name
        self.phone = model.phone
        self.avatar_url = model.avatar_url
        self.created_at = model.created_at


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
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

        user_row = db.query(UserModel).filter(UserModel.id == user_id).first()

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


async def get_optional_user(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
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

        user_row = db.query(UserModel).filter(UserModel.id == user_id).first()

        if user_row:
            return User(user_row)

    except Exception:
        pass

    return None
