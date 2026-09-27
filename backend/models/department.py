from enum import Enum


class DepartmentType(str, Enum):
    IT = "IT"
    HR = "HR"
    FINANCE = "Finance"
    FACILITIES = "Facilities"
    ADMINISTRATION = "Administration"
    OTHER = "Other"