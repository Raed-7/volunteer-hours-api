from datetime import date, datetime

from pydantic import BaseModel


class EventBase(BaseModel):
    title: str
    event_category: str
    event_date: date
    location: str
    description: str | None = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: str | None = None
    event_category: str | None = None
    event_date: date | None = None
    location: str | None = None
    description: str | None = None


class EventRead(EventBase):
    id: int

    model_config = {"from_attributes": True}


class ShiftBase(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    required_volunteers: int = 0


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(BaseModel):
    title: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    required_volunteers: int | None = None


class ShiftRead(ShiftBase):
    id: int
    event_id: int

    model_config = {"from_attributes": True}
