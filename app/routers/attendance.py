from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.shift import Shift
from app.models.volunteer import Volunteer
from app.schemas.attendance import (
    AttendanceRead,
    CheckInRequest,
    CheckOutRequest,
    VolunteerHoursBreakdown,
    VolunteerHoursResponse,
)
from app.services.attendance_service import compute_minutes_worked

router = APIRouter(tags=["attendance"], dependencies=[Depends(get_current_user)])


@router.post("/shifts/{shift_id}/check-in", response_model=AttendanceRead, status_code=status.HTTP_201_CREATED)
def check_in(shift_id: int, payload: CheckInRequest, db: Session = Depends(get_db)) -> Attendance:
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")

    volunteer = db.query(Volunteer).filter(Volunteer.id == payload.volunteer_id).first()
    if not volunteer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volunteer not found")

    existing = (
        db.query(Attendance)
        .filter(Attendance.shift_id == shift_id, Attendance.volunteer_id == payload.volunteer_id)
        .first()
    )
    if existing and existing.checked_in_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Volunteer already checked in for this shift")

    checked_in_at = payload.checked_in_at or datetime.utcnow()
    if existing:
        existing.checked_in_at = checked_in_at
        existing.status = payload.status
        attendance = existing
    else:
        attendance = Attendance(
            shift_id=shift_id,
            volunteer_id=payload.volunteer_id,
            checked_in_at=checked_in_at,
            status=payload.status,
        )
        db.add(attendance)

    db.commit()
    db.refresh(attendance)
    return attendance


@router.post("/shifts/{shift_id}/check-out", response_model=AttendanceRead)
def check_out(shift_id: int, payload: CheckOutRequest, db: Session = Depends(get_db)) -> Attendance:
    attendance = (
        db.query(Attendance)
        .filter(Attendance.shift_id == shift_id, Attendance.volunteer_id == payload.volunteer_id)
        .first()
    )
    if not attendance or not attendance.checked_in_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot check out without check in")

    if attendance.checked_out_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Volunteer already checked out")

    checked_out_at = payload.checked_out_at or datetime.utcnow()
    if checked_out_at < attendance.checked_in_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Check-out cannot occur before check-in")

    attendance.checked_out_at = checked_out_at
    attendance.minutes_worked = compute_minutes_worked(attendance.checked_in_at, checked_out_at)

    db.commit()
    db.refresh(attendance)
    return attendance


@router.get("/volunteers/{volunteer_id}/hours", response_model=VolunteerHoursResponse)
def volunteer_hours(
    volunteer_id: int,
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
) -> VolunteerHoursResponse:
    volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volunteer not found")

    query = db.query(Attendance, Shift, Event).join(Shift, Attendance.shift_id == Shift.id).join(Event, Shift.event_id == Event.id)
    query = query.filter(Attendance.volunteer_id == volunteer_id)

    if from_date:
        query = query.filter(Shift.start_time >= datetime.combine(from_date, time.min))
    if to_date:
        query = query.filter(Shift.start_time <= datetime.combine(to_date, time.max))

    rows = query.all()
    breakdown = [
        VolunteerHoursBreakdown(shift_id=shift.id, event_title=event.title, minutes_worked=attendance.minutes_worked)
        for attendance, shift, event in rows
    ]
    total_minutes = sum(item.minutes_worked for item in breakdown)
    return VolunteerHoursResponse(
        volunteer_id=volunteer_id,
        from_date=from_date,
        to_date=to_date,
        total_minutes=total_minutes,
        total_hours=round(total_minutes / 60, 2),
        breakdown=breakdown,
    )
