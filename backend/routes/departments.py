from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from database import departments_collection
from schemas.department import DepartmentCreate
from utils.dependencies import require_roles


router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


@router.post("")
async def create_department(
    data: DepartmentCreate,
    current_user=Depends(
        require_roles("org_admin")
    )
):

    organisation_id = current_user["organisation_id"]

    existing = await departments_collection.find_one({
        "organisation_id": organisation_id,
        "name": data.name
    })

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Department already exists"
        )

    department = {
        "organisation_id": organisation_id,
        "name": data.name,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }

    result = await departments_collection.insert_one(
        department
    )

    return {
        "message": "Department created",
        "department": {
            "id": str(result.inserted_id),
            "name": data.name
        }
    }

@router.get("")
async def get_departments(
    current_user=Depends(
        require_roles(
            "org_admin",
            "support_agent",
            "user"
        )
    )
):

    cursor = departments_collection.find({
        "organisation_id": current_user["organisation_id"],
        "is_active": True
    })

    departments = []

    async for department in cursor:

        departments.append({
            "id": str(department["_id"]),
            "name": department["name"]
        })

    return departments