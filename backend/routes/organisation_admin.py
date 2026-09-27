from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException
from database import (
    users_collection,
    organisations_collection,
    departments_collection,
    join_requests_collection,
)
from utils.dependencies import require_roles

router = APIRouter(
    prefix="/organisation-admin",
    tags=["Organisation Admin"]
)


def get_object_id(value: str):
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid ID"
        )


# ============================================================
# DASHBOARD
# ============================================================

@router.get("/dashboard")
async def get_dashboard(
    current_user=Depends(require_roles("org_admin"))
):
    organisation_id = current_user["organisation_id"]

    organisation = await organisations_collection.find_one({
        "_id": organisation_id
    })

    if not organisation:
        raise HTTPException(
            status_code=404,
            detail="Organisation not found"
        )

    department_count = await departments_collection.count_documents({
        "organisation_id": organisation_id,
        "is_active": True
    })

    user_count = await users_collection.count_documents({
        "organisation_id": organisation_id,
        "is_active": True
    })

    support_agent_count = await users_collection.count_documents({
        "organisation_id": organisation_id,
        "role": "support_agent",
        "is_active": True
    })

    pending_requests = await join_requests_collection.count_documents({
        "organisation_id": organisation_id,
        "status": "pending"
    })

    return {
        "organisation": {
            "id": str(organisation["_id"]),
            "name": organisation["name"],
            "status": organisation["status"]
        },
        "stats": {
            "departments": department_count,
            "users": user_count,
            "support_agents": support_agent_count,
            "pending_requests": pending_requests
        }
    }


# ============================================================
# USERS
# ============================================================

@router.get("/users")
async def get_users(
    current_user=Depends(require_roles("org_admin"))
):
    organisation_id = current_user["organisation_id"]

    users = []

    cursor = users_collection.find({
        "organisation_id": organisation_id
    })

    async for user in cursor:
        users.append({
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "department_id": (
                str(user["department_id"])
                if user.get("department_id")
                else None
            ),
            "is_active": user.get("is_active", True)
        })

    return users


# ============================================================
# DEPARTMENTS
# ============================================================

@router.get("/departments")
async def get_departments(
    current_user=Depends(require_roles("org_admin"))
):
    organisation_id = current_user["organisation_id"]

    departments = []

    cursor = departments_collection.find({
        "organisation_id": organisation_id,
        "is_active": True
    })

    async for department in cursor:
        departments.append({
            "id": str(department["_id"]),
            "name": department["name"],
            "bot_enabled": department.get("bot_enabled", True),
            "human_support_enabled": department.get(
                "human_support_enabled",
                True
            ),
            "rules": department.get("rules", [])
        })

    return departments


# ============================================================
# CREATE DEPARTMENT
# ============================================================

@router.post("/departments")
async def create_department(
    data: dict,
    current_user=Depends(require_roles("org_admin"))
):
    organisation_id = current_user["organisation_id"]

    name = data.get("name", "").strip()

    if len(name) < 2:
        raise HTTPException(
            status_code=400,
            detail="Department name is required"
        )

    existing = await departments_collection.find_one({
        "organisation_id": organisation_id,
        "name": name,
        "is_active": True
    })

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Department already exists"
        )

    department = {
        "organisation_id": organisation_id,
        "name": name,
        "bot_enabled": data.get("bot_enabled", True),
        "human_support_enabled": data.get(
            "human_support_enabled",
            True
        ),
        "rules": [],
        "is_active": True
    }

    result = await departments_collection.insert_one(department)

    return {
        "message": "Department created",
        "department": {
            "id": str(result.inserted_id),
            "name": name,
            "bot_enabled": department["bot_enabled"],
            "human_support_enabled": department[
                "human_support_enabled"
            ]
        }
    }


# ============================================================
# UPDATE DEPARTMENT
# ============================================================

@router.patch("/departments/{department_id}")
async def update_department(
    department_id: str,
    data: dict,
    current_user=Depends(require_roles("org_admin"))
):
    organisation_id = current_user["organisation_id"]

    department_object_id = get_object_id(department_id)

    department = await departments_collection.find_one({
        "_id": department_object_id,
        "organisation_id": organisation_id,
        "is_active": True
    })

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    update_data = {}

    if "name" in data:
        name = data["name"].strip()

        if len(name) < 2:
            raise HTTPException(
                status_code=400,
                detail="Department name is invalid"
            )

        update_data["name"] = name

    if "bot_enabled" in data:
        update_data["bot_enabled"] = bool(
            data["bot_enabled"]
        )

    if "human_support_enabled" in data:
        update_data["human_support_enabled"] = bool(
            data["human_support_enabled"]
        )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No changes provided"
        )

    await departments_collection.update_one(
        {"_id": department_object_id},
        {"$set": update_data}
    )

    updated = await departments_collection.find_one({
        "_id": department_object_id
    })

    return {
        "message": "Department updated",
        "department": {
            "id": str(updated["_id"]),
            "name": updated["name"],
            "bot_enabled": updated.get("bot_enabled", True),
            "human_support_enabled": updated.get(
                "human_support_enabled",
                True
            )
        }
    }


# ============================================================
# DELETE DEPARTMENT
# ============================================================

@router.delete("/departments/{department_id}")
async def delete_department(
    department_id: str,
    current_user=Depends(require_roles("org_admin"))
):
    organisation_id = current_user["organisation_id"]

    department_object_id = get_object_id(department_id)

    department = await departments_collection.find_one({
        "_id": department_object_id,
        "organisation_id": organisation_id,
        "is_active": True
    })

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    await departments_collection.update_one(
        {"_id": department_object_id},
        {
            "$set": {
                "is_active": False
            }
        }
    )

    return {
        "message": "Department deleted"
    }


# ============================================================
# JOIN REQUESTS
# ============================================================

@router.get("/join-requests")
async def get_join_requests(
    current_user=Depends(require_roles("org_admin"))
):
    organisation_id = current_user["organisation_id"]

    requests = []

    cursor = join_requests_collection.find({
        "organisation_id": organisation_id
    }).sort("created_at", -1)

    async for request in cursor:
        requests.append({
            "id": str(request["_id"]),
            "user_id": str(request["user_id"]),
            "role": request["role"],
            "department_id": (
                str(request["department_id"])
                if request.get("department_id")
                else None
            ),
            "status": request["status"],
            "created_at": request.get("created_at")
        })

    return requests