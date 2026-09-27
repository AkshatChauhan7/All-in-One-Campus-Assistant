import asyncio
from datetime import datetime, timezone

from database import users_collection
from utils.security import hash_password


async def create_platform_admin():

    email = input("Admin email: ").strip().lower()
    name = input("Admin name: ").strip()
    password = input("Admin password: ")

    existing = await users_collection.find_one({
        "email": email
    })

    if existing:
        print("A user with this email already exists.")
        return

    now = datetime.now(timezone.utc)

    admin = {
        "name": name,
        "email": email,
        "password_hash": hash_password(password),

        "role": "platform_admin",

        "organisation_id": None,
        "department_id": None,

        "is_active": True,

        "created_at": now
    }

    result = await users_collection.insert_one(admin)

    print("Platform admin created successfully!")
    print("ID:", result.inserted_id)
    print("Email:", email)


async def main():
    await create_platform_admin()


if __name__ == "__main__":
    asyncio.run(main())