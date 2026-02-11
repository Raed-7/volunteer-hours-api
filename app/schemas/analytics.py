from pydantic import BaseModel


class LeaderboardItem(BaseModel):
    volunteer_id: int
    full_name: str
    total_minutes: int
    total_hours: float


class AwardItem(BaseModel):
    volunteer_id: int
    full_name: str
    tier: str
    total_hours: float


class ShiftCoverageItem(BaseModel):
    shift_id: int
    shift_title: str
    required_volunteers: int
    attended_volunteers: int


class EventCoverageResponse(BaseModel):
    event_id: int
    total_required: int
    total_attended: int
    shifts: list[ShiftCoverageItem]


class ReliabilityResponse(BaseModel):
    volunteer_id: int
    attendance_rate: float
    attended_count: int
    absent_count: int
    late_count: int
    total_records: int
