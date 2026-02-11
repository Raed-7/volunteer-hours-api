import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.attendance import Attendance, AttendanceStatus
from app.models.event import Event
from app.models.shift import Shift
from app.models.volunteer import Volunteer


@dataclass
class Summary:
    imported: int = 0
    skipped: int = 0
    failed: int = 0


def _parse_datetime(value: str) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def import_volunteers_rows(db: Session, rows: list[dict[str, str]]) -> Summary:
    summary = Summary()
    for row in rows:
        full_name = (row.get("full_name") or "").strip()
        email = (row.get("email") or "").strip() or None
        if not full_name:
            summary.failed += 1
            continue

        if email:
            duplicate = db.query(Volunteer).filter(Volunteer.email == email).first()
        else:
            duplicate = db.query(Volunteer).filter(Volunteer.full_name == full_name).first()
        if duplicate:
            summary.skipped += 1
            continue

        volunteer = Volunteer(
            volunteer_no=(row.get("volunteer_no") or "").strip() or None,
            full_name=full_name,
            email=email,
            phone=(row.get("phone") or "").strip() or None,
            notes=(row.get("notes") or "").strip() or None,
        )
        db.add(volunteer)
        summary.imported += 1
    db.commit()
    return summary


def import_events_rows(db: Session, rows: list[dict[str, str]]) -> Summary:
    summary = Summary()
    for row in rows:
        title = (row.get("title") or "").strip()
        event_category = (row.get("event_category") or "").strip()
        event_date_raw = (row.get("event_date") or "").strip()
        location = (row.get("location") or "").strip()

        if not all([title, event_category, event_date_raw, location]):
            summary.failed += 1
            continue

        try:
            event_date = date.fromisoformat(event_date_raw)
        except ValueError:
            summary.failed += 1
            continue

        existing = db.query(Event).filter(Event.title == title, Event.event_date == event_date).first()
        if existing:
            summary.skipped += 1
            continue

        event = Event(
            title=title,
            event_category=event_category,
            event_date=event_date,
            location=location,
            description=(row.get("description") or "").strip() or None,
        )
        db.add(event)
        summary.imported += 1
    db.commit()
    return summary


def import_attendance_rows(db: Session, rows: list[dict[str, str]]) -> Summary:
    summary = Summary()
    for row in rows:
        try:
            shift_id = int((row.get("shift_id") or "").strip())
            volunteer_id = int((row.get("volunteer_id") or "").strip())
        except ValueError:
            summary.failed += 1
            continue

        shift = db.query(Shift).filter(Shift.id == shift_id).first()
        volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
        if not shift or not volunteer:
            summary.failed += 1
            continue

        existing = db.query(Attendance).filter(Attendance.shift_id == shift_id, Attendance.volunteer_id == volunteer_id).first()
        if existing:
            summary.skipped += 1
            continue

        checked_in_at = _parse_datetime(row.get("checked_in_at") or "")
        checked_out_at = _parse_datetime(row.get("checked_out_at") or "")
        if (row.get("checked_in_at") and checked_in_at is None) or (row.get("checked_out_at") and checked_out_at is None):
            summary.failed += 1
            continue

        minutes_worked_raw = (row.get("minutes_worked") or "").strip()
        hours_worked_raw = (row.get("hours_worked") or "").strip()
        status_raw = (row.get("status") or "present").strip().lower()

        try:
            if minutes_worked_raw:
                minutes_worked = int(minutes_worked_raw)
            elif hours_worked_raw:
                minutes_worked = int(float(hours_worked_raw) * 60)
            elif checked_in_at and checked_out_at and checked_out_at >= checked_in_at:
                minutes_worked = int((checked_out_at - checked_in_at).total_seconds() // 60)
            else:
                minutes_worked = 0
        except ValueError:
            summary.failed += 1
            continue

        if checked_in_at and checked_out_at and checked_out_at < checked_in_at:
            summary.failed += 1
            continue

        try:
            status_enum = AttendanceStatus(status_raw)
        except ValueError:
            status_enum = AttendanceStatus.present

        db.add(
            Attendance(
                shift_id=shift_id,
                volunteer_id=volunteer_id,
                checked_in_at=checked_in_at,
                checked_out_at=checked_out_at,
                minutes_worked=max(0, minutes_worked),
                status=status_enum,
            )
        )
        summary.imported += 1

    db.commit()
    return summary


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))
