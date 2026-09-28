import asyncio

from database import departments_collection
from services.orchestration.router import DepartmentRouter


async def main():

    department = await departments_collection.find_one({
        "is_active": True
    })

    if not department:
        print("No active departments found.")
        return

    organisation_id = department["organisation_id"]

    router = DepartmentRouter()

    result = await router.route(
        organisation_id=organisation_id,
        department_names=["HR", "IT"],
    )

    print("\nRouter result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())