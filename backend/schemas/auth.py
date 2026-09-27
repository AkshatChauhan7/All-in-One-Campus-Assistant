from pydantic import BaseModel, EmailStr, Field

from models.user import UserRole


class InitialDepartment(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )

    bot_enabled: bool = True
    human_support_enabled: bool = True


class CreateOrganisationRequest(BaseModel):
    organisation_name: str = Field(
        min_length=2,
        max_length=150
    )

    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

    departments: list[InitialDepartment] = Field(default_factory=list)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class JoinOrganisationRequest(BaseModel):
    organisation_id: str

    role: UserRole

    department_id: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"