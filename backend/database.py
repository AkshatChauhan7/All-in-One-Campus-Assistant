from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

from config import settings


client = AsyncMongoClient(
    settings.MONGO_URI,
    server_api=ServerApi(
        version="1",
        strict=True,
        deprecation_errors=True
    )
)

db = client[settings.DATABASE_NAME]


users_collection = db["users"]
organisations_collection = db["organisations"]
departments_collection = db["departments"]
join_requests_collection = db["join_requests"]