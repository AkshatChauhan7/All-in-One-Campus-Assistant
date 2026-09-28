from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from database import (
    users_collection,
    organisations_collection,
    departments_collection
)

from schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse
)

from utils.dependencies import get_current_user

from utils.security import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# REGISTER
# ============================================================

@router.post("/register")
async def register(data: RegisterRequest):

    email = data.email.lower()

    # --------------------------------------------------------
    # 1. Check email
    # --------------------------------------------------------

    existing_user = await users_collection.find_one({
        "email": email
    })

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # --------------------------------------------------------
    # 2. Validate organisation ID
    # --------------------------------------------------------

    try:
        organisation_id = ObjectId(
            data.organisation_id
        )

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid organisation ID"
        )

    # --------------------------------------------------------
    # 3. Check organisation
    # --------------------------------------------------------

    organisation = await organisations_collection.find_one({
        "_id": organisation_id,
        "status": "active"
    })

    if not organisation:
        raise HTTPException(
            status_code=404,
            detail="Organisation not found or inactive"
        )

    # --------------------------------------------------------
    # 4. Department handling
    # --------------------------------------------------------

    department_id = None

    if data.role == "support_agent":

        # Support agent MUST have department
        if not data.department_id:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Support agent must select a department"
                )
            )

        try:
            department_id = ObjectId(
                data.department_id
            )

        except Exception:

            raise HTTPException(
                status_code=400,
                detail="Invalid department ID"
            )

        # Department must belong to selected organisation
        department = await departments_collection.find_one({
            "_id": department_id,
            "organisation_id": organisation_id,
            "is_active": True
        })

        if not department:

            raise HTTPException(
                status_code=404,
                detail="Department not found"
            )

    else:

        # Normal user cannot have a department
        if data.department_id:

            raise HTTPException(
                status_code=400,
                detail=(
                    "User role cannot have a department"
                )
            )

    # --------------------------------------------------------
    # 5. Create user
    # --------------------------------------------------------

    now = datetime.now(timezone.utc)

    user = {
        "name": data.name,
        "email": email,
        "password_hash": hash_password(data.password),

        "role": data.role,

        "organisation_id": organisation_id,

        "department_id": department_id,

        "is_active": True,

        "created_at": now
    }

    result = await users_collection.insert_one(user)

    user_id = result.inserted_id

    # --------------------------------------------------------
    # 6. Create access token
    # --------------------------------------------------------

    token = create_access_token(
        user_id=str(user_id),
        role=data.role,
        organisation_id=str(organisation_id),
        department_id=(
            str(department_id)
            if department_id
            else None
        )
    )

    # --------------------------------------------------------
    # 7. Return
    # --------------------------------------------------------

    return {
        "message": "Account created successfully",

        "user": {
            "id": str(user_id),
            "name": data.name,
            "email": email,
            "role": data.role,
            "organisation_id": str(
                organisation_id
            ),
            "department_id": (
                str(department_id)
                if department_id
                else None
            )
        },

        "access_token": token,

        "token_type": "bearer"
    }


# from datetime import datetime, timezone

# from bson import ObjectId
# from fastapi import APIRouter, Depends, HTTPException

# from database import users_collection
# from schemas.auth import (
#     LoginRequest,
#     TokenResponse,
#     RegisterRequest
# )
# from utils.dependencies import get_current_user
# from utils.security import (
#     verify_password,
#     create_access_token,
#     hash_password
# )


# router = APIRouter(
#     prefix="/auth",
#     tags=["Authentication"]
# )

# # ============================================================
# # REGISTER NORMAL USER
# # ============================================================

# @router.post("/register")
# async def register(data: RegisterRequest):

#     email = data.email.lower().strip()

#     # ----------------------------------------
#     # 1. Check if email already exists
#     # ----------------------------------------

#     existing_user = await users_collection.find_one({
#         "email": email
#     })

#     if existing_user:
#         raise HTTPException(
#             status_code=400,
#             detail="Email already registered"
#         )

#     # ----------------------------------------
#     # 2. Create normal user
#     # ----------------------------------------

#     user = {
#         "name": data.name.strip(),
#         "email": email,
#         "password_hash": hash_password(data.password),

#         # New users always start as normal users
#         "role": "user",

#         # They don't belong to an organisation yet
#         "organisation_id": None,

#         "department_id": None,

#         "is_active": True,

#         "created_at": datetime.now(timezone.utc)
#     }

#     result = await users_collection.insert_one(user)

#     return {
#         "message": "Account created successfully",
#         "user": {
#             "id": str(result.inserted_id),
#             "name": user["name"],
#             "email": user["email"],
#             "role": user["role"],
#             "organisation_id": None,
#             "department_id": None
#         }
#     }


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