from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.event import Event
from app.models.shift import Shift
from app.schemas.event import EventCreate, EventRead, EventUpdate, ShiftCreate, ShiftRead, ShiftUpdate

router = APIRouter(tags=["events"], dependencies=[Depends(get_current_user)])


@router.post("/events", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Session = Depends(get_db)) -> Event:
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/events", response_model=list[EventRead])
def list_events(db: Session = Depends(get_db)) -> list[Event]:
    return db.query(Event).order_by(Event.id).all()


@router.get("/events/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)) -> Event:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.patch("/events/{event_id}", response_model=EventRead)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)) -> Event:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)) -> None:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    db.delete(event)
    db.commit()
    return None


@router.post("/events/{event_id}/shifts", response_model=ShiftRead, status_code=status.HTTP_201_CREATED)
def create_shift(event_id: int, payload: ShiftCreate, db: Session = Depends(get_db)) -> Shift:
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Shift end_time must be after start_time")

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    shift = Shift(event_id=event_id, **payload.model_dump())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


@router.get("/events/{event_id}/shifts", response_model=list[ShiftRead])
def list_event_shifts(event_id: int, db: Session = Depends(get_db)) -> list[Shift]:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return db.query(Shift).filter(Shift.event_id == event_id).order_by(Shift.id).all()


@router.get("/shifts/{shift_id}", response_model=ShiftRead)
def get_shift(shift_id: int, db: Session = Depends(get_db)) -> Shift:
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")
    return shift


@router.patch("/shifts/{shift_id}", response_model=ShiftRead)
def update_shift(shift_id: int, payload: ShiftUpdate, db: Session = Depends(get_db)) -> Shift:
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")

    data = payload.model_dump(exclude_unset=True)
    start = data.get("start_time", shift.start_time)
    end = data.get("end_time", shift.end_time)
    if end <= start:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Shift end_time must be after start_time")

    for key, value in data.items():
        setattr(shift, key, value)
    db.commit()
    db.refresh(shift)
    return shift


@router.delete("/shifts/{shift_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shift(shift_id: int, db: Session = Depends(get_db)) -> None:
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")
    db.delete(shift)
    db.commit()
    return None
