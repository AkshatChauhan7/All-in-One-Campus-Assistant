from database import departments_collection


class DepartmentLoader:

    async def get_active_departments(
        self,
        organisation_id,
    ) -> list[str]:

        cursor = departments_collection.find(
            {
                "organisation_id": organisation_id,
                "is_active": True,
            },
            {
                "name": 1,
            },
        )

        departments = []

        async for department in cursor:
            departments.append(department["name"])

        return departments