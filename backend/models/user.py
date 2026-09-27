from enum import Enum


class UserRole(str, Enum):
    PLATFORM_ADMIN = "platform_admin"
    ORG_ADMIN = "org_admin"
    SUPPORT_AGENT = "support_agent"
    USER = "user"