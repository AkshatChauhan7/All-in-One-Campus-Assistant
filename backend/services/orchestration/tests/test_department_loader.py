import asyncio

from database import departments_collection
from services.orchestration.department_loader import DepartmentLoader


async def main():

    department = await departments_collection.find_one({
        "is_active": True
    })

    if not department:
        print("No active department found.")
        return

    organisation_id = department["organisation_id"]

    print("Organisation ID:", organisation_id)

    loader = DepartmentLoader()

    departments = await loader.get_active_departments(
        organisation_id
    )

    print("Available departments:")
    print(departments)


if __name__ == "__main__":
    asyncio.run(main())