from bson import ObjectId
from bson.errors import InvalidId

from fastapi import APIRouter, Depends, HTTPException

from database import organisations_collection
from utils.dependencies import require_roles


router = APIRouter(
    prefix="/platform-admin",
    tags=["Platform Admin"]
)


def get_object_id(value: str):
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid organisation ID"
        )


# =========================
# GET ALL ORGANISATIONS
# =========================

@router.get("/organisations")
async def get_all_organisations(
    current_user=Depends(
        require_roles("platform_admin")
    )
):
    organisations = []

    cursor = organisations_collection.find(
        {}
    ).sort("created_at", -1)

    async for organisation in cursor:

        organisations.append({
            "id": str(organisation["_id"]),
            "name": organisation["name"],
            "status": organisation["status"],
            "created_at": organisation["created_at"]
        })

    return organisations


# =========================
# APPROVE ORGANISATION
# =========================

@router.post("/organisations/{organisation_id}/approve")
async def approve_organisation(
    organisation_id: str,
    current_user=Depends(
        require_roles("platform_admin")
    )
):
    object_id = get_object_id(organisation_id)

    organisation = await organisations_collection.find_one({
        "_id": object_id
    })

    if not organisation:
        raise HTTPException(
            status_code=404,
            detail="Organisation not found"
        )

    if organisation["status"] != "pending":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Organisation is already "
                f"{organisation['status']}"
            )
        )

    await organisations_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": "active"
            }
        }
    )

    return {
        "message": "Organisation approved",
        "organisation": {
            "id": str(object_id),
            "name": organisation["name"],
            "status": "active"
        }
    }


# =========================
# REJECT ORGANISATION
# =========================

@router.post("/organisations/{organisation_id}/reject")
async def reject_organisation(
    organisation_id: str,
    current_user=Depends(
        require_roles("platform_admin")
    )
):
    object_id = get_object_id(organisation_id)

    organisation = await organisations_collection.find_one({
        "_id": object_id
    })

    if not organisation:
        raise HTTPException(
            status_code=404,
            detail="Organisation not found"
        )

    if organisation["status"] != "pending":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Organisation is already "
                f"{organisation['status']}"
            )
        )

    await organisations_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": "rejected"
            }
        }
    )

    return {
        "message": "Organisation rejected",
        "organisation": {
            "id": str(object_id),
            "name": organisation["name"],
            "status": "rejected"
        }
    }


# =========================
# SUSPEND ORGANISATION
# =========================

@router.post("/organisations/{organisation_id}/suspend")
async def suspend_organisation(
    organisation_id: str,
    current_user=Depends(
        require_roles("platform_admin")
    )
):
    object_id = get_object_id(organisation_id)

    organisation = await organisations_collection.find_one({
        "_id": object_id
    })

    if not organisation:
        raise HTTPException(
            status_code=404,
            detail="Organisation not found"
        )

    if organisation["status"] != "active":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only active organisations "
                f"can be suspended"
            )
        )

    await organisations_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": "suspended"
            }
        }
    )

    return {
        "message": "Organisation suspended",
        "organisation": {
            "id": str(object_id),
            "name": organisation["name"],
            "status": "suspended"
        }
    }