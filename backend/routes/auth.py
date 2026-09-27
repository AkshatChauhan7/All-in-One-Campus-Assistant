from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from database import users_collection
from schemas.auth import (
    LoginRequest,
    TokenResponse
)
from utils.dependencies import get_current_user
from utils.security import (
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=TokenResponse
)
async def login(data: LoginRequest):

    email = data.email.lower()

    user = await users_collection.find_one({
        "email": email
    })

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        data.password,
        user["password_hash"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.get("is_active", True):

        raise HTTPException(
            status_code=403,
            detail="Account is disabled"
        )

    token = create_access_token(
        user_id=str(user["_id"]),
        role=user["role"],
        organisation_id=(
            str(user["organisation_id"])
            if user.get("organisation_id")
            else None
        ),
        department_id=(
            str(user["department_id"])
            if user.get("department_id")
            else None
        )
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
async def get_me(
    current_user=Depends(get_current_user)
):

    return {
        "id": str(current_user["_id"]),
        "name": current_user["name"],
        "email": current_user["email"],
        "role": current_user["role"],
        "organisation_id": (
            str(current_user["organisation_id"])
            if current_user.get("organisation_id")
            else None
        ),
        "department_id": (
            str(current_user["department_id"])
            if current_user.get("department_id")
            else None
        )
    }