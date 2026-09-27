from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from database import (
    organisations_collection,
    departments_collection,
    join_requests_collection,
    users_collection
)

from schemas.auth import JoinOrganisationRequest
from utils.dependencies import get_current_user, require_roles

router = APIRouter(
    prefix="/join-requests",
    tags=["Join Requests"]
)


@router.post("")
async def create_join_request(
    data: JoinOrganisationRequest,
    current_user=Depends(get_current_user)
):

    # User must not already belong to an organisation
    if current_user.get("organisation_id"):

        raise HTTPException(
            status_code=400,
            detail="You already belong to an organisation"
        )

    if data.role not in [
        "user",
        "support_agent"
    ]:

        raise HTTPException(
            status_code=400,
            detail="Invalid organisation role"
        )

    try:

        organisation_id = ObjectId(
            data.organisation_id
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid organisation ID"
        )

    # Check organisation
    organisation = await organisations_collection.find_one({
        "_id": organisation_id,
        "status": "active"
    })

    if not organisation:

        raise HTTPException(
            status_code=404,
            detail="Organisation not found"
        )

    department_id = None

    # Support agent requires department
    if data.role == "support_agent":

        if not data.department_id:

            raise HTTPException(
                status_code=400,
                detail="Support agent must select a department"
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

    # Prevent duplicate pending requests
    existing = await join_requests_collection.find_one({
        "user_id": current_user["_id"],
        "organisation_id": organisation_id,
        "status": "pending"
    })

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Join request already exists"
        )

    request = {
        "user_id": current_user["_id"],
        "organisation_id": organisation_id,
        "requested_role": data.role,
        "department_id": department_id,
        "status": "pending",
        "created_at": datetime.now(timezone.utc)
    }

    result = await join_requests_collection.insert_one(
        request
    )

    return {
        "message": "Join request submitted",
        "request_id": str(result.inserted_id)
    }


@router.get("")
async def get_join_requests(
    current_user=Depends(
        get_current_user
    )
):

    if current_user["role"] != "org_admin":

        raise HTTPException(
            status_code=403,
            detail="Only organisation admin can view requests"
        )

    cursor = join_requests_collection.find({
        "organisation_id": current_user["organisation_id"],
        "status": "pending"
    })

    requests = []

    async for request in cursor:

        user = await users_collection.find_one({
            "_id": request["user_id"]
        })

        requests.append({
            "id": str(request["_id"]),
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"]
            },
            "requested_role": request["requested_role"],
            "department_id": (
                str(request["department_id"])
                if request.get("department_id")
                else None
            ),
            "created_at": request["created_at"]
        })

    return requests


@router.post("/{request_id}/approve")
async def approve_join_request(
    request_id: str,
    current_user=Depends(
        require_roles("org_admin")
    )
):

    try:

        request_object_id = ObjectId(
            request_id
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid request ID"
        )

    request = await join_requests_collection.find_one({
        "_id": request_object_id,
        "organisation_id": current_user["organisation_id"],
        "status": "pending"
    })

    if not request:

        raise HTTPException(
            status_code=404,
            detail="Join request not found"
        )

    update = {
        "organisation_id": request["organisation_id"],
        "role": request["requested_role"],
        "department_id": request.get("department_id")
    }

    await users_collection.update_one(
        {
            "_id": request["user_id"]
        },
        {
            "$set": update
        }
    )

    await join_requests_collection.update_one(
        {
            "_id": request_object_id
        },
        {
            "$set": {
                "status": "approved",
                "approved_by": current_user["_id"],
                "approved_at": datetime.now(timezone.utc)
            }
        }
    )

    return {
        "message": "Join request approved"
    }


@router.post("/{request_id}/reject")
async def reject_join_request(
    request_id: str,
    current_user=Depends(
        require_roles("org_admin")
    )
):

    try:

        request_object_id = ObjectId(
            request_id
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid request ID"
        )

    result = await join_requests_collection.update_one(
        {
            "_id": request_object_id,
            "organisation_id": current_user["organisation_id"],
            "status": "pending"
        },
        {
            "$set": {
                "status": "rejected",
                "rejected_by": current_user["_id"],
                "rejected_at": datetime.now(timezone.utc)
            }
        }
    )

    if result.modified_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Join request not found"
        )

    return {
        "message": "Join request rejected"
    }