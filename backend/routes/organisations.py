from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from database import (
    organisations_collection,
    users_collection,
    departments_collection
)

from schemas.auth import CreateOrganisationRequest

from utils.security import (
    hash_password,
    create_access_token
)


router = APIRouter(
    prefix="/organisations",
    tags=["Organisations"]
)


@router.post("/create")
async def create_organisation(
    data: CreateOrganisationRequest
):

    email = data.email.lower()

    # ----------------------------------------
    # 1. Check if email already exists
    # ----------------------------------------

    existing_user = await users_collection.find_one({
        "email": email
    })

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # ----------------------------------------
    # 2. Check if organisation already exists
    # ----------------------------------------

    existing_org = await organisations_collection.find_one({
        "name": data.organisation_name
    })

    if existing_org:

        raise HTTPException(
            status_code=400,
            detail="Organisation already exists"
        )

    # ----------------------------------------
    # 3. Create organisation
    # ----------------------------------------

    now = datetime.now(timezone.utc)

    organisation = {
        "name": data.organisation_name,
        "status": "pending",
        "created_at": now
    }

    org_result = await organisations_collection.insert_one(
        organisation
    )

    organisation_id = org_result.inserted_id

    # ----------------------------------------
    # 4. Create organisation admin
    # ----------------------------------------

    user = {
        "name": data.name,
        "email": email,
        "password_hash": hash_password(data.password),

        "role": "org_admin",

        "organisation_id": organisation_id,

        "department_id": None,

        "is_active": True,

        "created_at": now
    }

    user_result = await users_collection.insert_one(user)

    # ----------------------------------------
    # 5. Create initial departments
    # ----------------------------------------

    departments = []

    for department in data.departments:

        department_document = {
            "organisation_id": organisation_id,

            "name": department.name,

            "bot_enabled": department.bot_enabled,

            "human_support_enabled": (
                department.human_support_enabled
            ),

            # Will be used later for
            # department-specific AI instructions
            "rules": [],

            "created_at": now,

            "is_active": True
        }

        departments.append(department_document)

    if departments:

        await departments_collection.insert_many(
            departments
        )

    # ----------------------------------------
    # 6. Create JWT
    # ----------------------------------------

    token = create_access_token(
        user_id=str(user_result.inserted_id),
        role="org_admin",
        organisation_id=str(organisation_id)
    )

    # ----------------------------------------
    # 7. Return response
    # ----------------------------------------

    return {
        "message": "Organisation created",

        "organisation": {
            "id": str(organisation_id),
            "name": data.organisation_name,
            "status": "pending"
        },

        "user": {
            "id": str(user_result.inserted_id),
            "name": data.name,
            "email": email,
            "role": "org_admin"
        },

        "departments": [
            {
                "name": department.name,
                "bot_enabled": department.bot_enabled,
                "human_support_enabled": (
                    department.human_support_enabled
                )
            }
            for department in data.departments
        ],

        "access_token": token,

        "token_type": "bearer"
    }


# --------------------------------------------
# Get all active organisations
# --------------------------------------------

@router.get("")
async def list_organisations():

    organisations = []

    cursor = organisations_collection.find({
        "status": "active"
    })

    async for org in cursor:

        organisations.append({
            "id": str(org["_id"]),
            "name": org["name"]
        })

    return organisations