from bson import ObjectId
from database import departments_collection

class DepartmentRouter:

    async def route(
        self,
        organisation_id,
        department_names: list[str],
    ) -> list[dict]:

        if not department_names:
            return []

        if isinstance(organisation_id, str):
            organisation_id = ObjectId(organisation_id)

        cursor = departments_collection.find({
            "organisation_id": organisation_id,
            "name": {"$in": department_names},
            "is_active": True,
        })

        departments = []

        async for department in cursor:
            departments.append({
                "department_id": str(department["_id"]),
                "name": department["name"],
            })

        return departments