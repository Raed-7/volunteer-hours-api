from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.attendance import Attendance, AttendanceStatus
from app.models.event import Event
from app.models.shift import Shift
from app.models.volunteer import Volunteer
from app.schemas.analytics import (
    AwardItem,
    EventCoverageResponse,
    LeaderboardItem,
    ReliabilityResponse,
    ShiftCoverageItem,
)

router = APIRouter(prefix="/analytics", tags=["analytics"], dependencies=[Depends(get_current_user)])


def _date_filtered_attendance(db: Session, from_date: date | None, to_date: date | None):
    query = db.query(Attendance, Volunteer, Shift).join(Volunteer, Attendance.volunteer_id == Volunteer.id).join(Shift, Attendance.shift_id == Shift.id)
    if from_date:
        query = query.filter(Shift.start_time >= datetime.combine(from_date, time.min))
    if to_date:
        query = query.filter(Shift.start_time <= datetime.combine(to_date, time.max))
    return query


@router.get("/leaderboard", response_model=list[LeaderboardItem])
def leaderboard(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    limit: int = 20,
    db: Session = Depends(get_db),
) -> list[LeaderboardItem]:
    rows = _date_filtered_attendance(db, from_date, to_date).all()
    totals: dict[int, tuple[str, int]] = {}
    for attendance, volunteer, _ in rows:
        current_name, current_minutes = totals.get(volunteer.id, (volunteer.full_name, 0))
        totals[volunteer.id] = (current_name, current_minutes + attendance.minutes_worked)

    ordered = sorted(totals.items(), key=lambda item: item[1][1], reverse=True)[:limit]
    return [
        LeaderboardItem(
            volunteer_id=volunteer_id,
            full_name=name,
            total_minutes=minutes,
            total_hours=round(minutes / 60, 2),
        )
        for volunteer_id, (name, minutes) in ordered
    ]


@router.get("/awards", response_model=list[AwardItem])
def awards(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
) -> list[AwardItem]:
    board = leaderboard(from_date, to_date, 10_000, db)
    output: list[AwardItem] = []
    for item in board:
        if item.total_hours >= 20:
            tier = "Tier A"
        elif item.total_hours >= 15:
            tier = "Tier B"
        elif item.total_hours >= 1:
            tier = "Tier C"
        else:
            continue
        output.append(AwardItem(volunteer_id=item.volunteer_id, full_name=item.full_name, tier=tier, total_hours=item.total_hours))
    return output


@router.get("/events/{event_id}/coverage", response_model=EventCoverageResponse)
def event_coverage(event_id: int, db: Session = Depends(get_db)) -> EventCoverageResponse:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    shifts = db.query(Shift).filter(Shift.event_id == event_id).all()
    shift_items: list[ShiftCoverageItem] = []
    total_required = 0
    total_attended = 0

    for shift in shifts:
        attended = (
            db.query(func.count(Attendance.id))
            .filter(Attendance.shift_id == shift.id, Attendance.checked_in_at.is_not(None))
            .scalar()
            or 0
        )
        total_required += shift.required_volunteers
        total_attended += attended
        shift_items.append(
            ShiftCoverageItem(
                shift_id=shift.id,
                shift_title=shift.title,
                required_volunteers=shift.required_volunteers,
                attended_volunteers=attended,
            )
        )

    return EventCoverageResponse(
        event_id=event_id,
        total_required=total_required,
        total_attended=total_attended,
        shifts=shift_items,
    )


@router.get("/volunteers/{volunteer_id}/reliability", response_model=ReliabilityResponse)
def reliability(
    volunteer_id: int,
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
) -> ReliabilityResponse:
    volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volunteer not found")

    rows = _date_filtered_attendance(db, from_date, to_date).filter(Attendance.volunteer_id == volunteer_id).all()
    attended = sum(1 for attendance, _, _ in rows if attendance.status == AttendanceStatus.present)
    absent = sum(1 for attendance, _, _ in rows if attendance.status == AttendanceStatus.absent)
    late = sum(1 for attendance, _, _ in rows if attendance.status == AttendanceStatus.late)
    total = len(rows)
    attendance_rate = round((attended + late) / total, 2) if total else 0.0

    return ReliabilityResponse(
        volunteer_id=volunteer_id,
        attendance_rate=attendance_rate,
        attended_count=attended,
        absent_count=absent,
        late_count=late,
        total_records=total,
    )
