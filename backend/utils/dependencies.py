from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

from database import users_collection
from utils.security import decode_access_token


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:

        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user = await users_collection.find_one({
            "_id": ObjectId(user_id)
        })

    except InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.get("is_active", True):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    return user


def require_roles(*roles):

    async def role_checker(
        current_user=Depends(get_current_user)
    ):

        if current_user["role"] not in roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user

    return role_checker