from datetime import date, datetime

from pydantic import BaseModel

from app.models.attendance import AttendanceStatus


class CheckInRequest(BaseModel):
    volunteer_id: int
    checked_in_at: datetime | None = None
    status: AttendanceStatus = AttendanceStatus.present


class CheckOutRequest(BaseModel):
    volunteer_id: int
    checked_out_at: datetime | None = None


class AttendanceRead(BaseModel):
    id: int
    shift_id: int
    volunteer_id: int
    checked_in_at: datetime | None
    checked_out_at: datetime | None
    minutes_worked: int
    status: AttendanceStatus

    model_config = {"from_attributes": True}


class VolunteerHoursBreakdown(BaseModel):
    shift_id: int
    event_title: str
    minutes_worked: int


class VolunteerHoursResponse(BaseModel):
    volunteer_id: int
    from_date: date | None
    to_date: date | None
    total_minutes: int
    total_hours: float
    breakdown: list[VolunteerHoursBreakdown]
