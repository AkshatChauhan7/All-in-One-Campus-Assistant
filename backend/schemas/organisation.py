from pydantic import BaseModel, Field


class OrganisationCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150
    )