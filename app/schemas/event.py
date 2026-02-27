from datetime import date

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
