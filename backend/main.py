from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import client
from routes import (
    auth,
    organisations,
    departments,
    join_requests,
    platform_admin,
    organisation_admin,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to MongoDB...")

    await client.admin.command("ping")

    print("MongoDB connected successfully!")

    yield

    await client.close()

    print("MongoDB connection closed!")


app = FastAPI(
    title="OneDesk AI",
    description="One Front Door for Everything",
    version="1.0.0",
    lifespan=lifespan
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Routes
# =========================

app.include_router(auth.router)
app.include_router(organisations.router)
app.include_router(departments.router)
app.include_router(join_requests.router)
app.include_router(platform_admin.router)
app.include_router(organisation_admin.router)


@app.get("/")
async def root():
    return {
        "message": "OneDesk AI API is running"
    }