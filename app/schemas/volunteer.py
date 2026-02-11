from datetime import datetime

from pydantic import BaseModel, EmailStr


class VolunteerBase(BaseModel):
    volunteer_no: str | None = None
    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None


class VolunteerCreate(VolunteerBase):
    pass


class VolunteerUpdate(BaseModel):
    volunteer_no: str | None = None
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None


class VolunteerRead(VolunteerBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
