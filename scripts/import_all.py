from pathlib import Path

from app.db.session import SessionLocal
from app.services.import_service import (
    import_attendance_rows,
    import_events_rows,
    import_volunteers_rows,
    load_csv,
)


if __name__ == "__main__":
    db = SessionLocal()
    try:
        volunteer_summary = import_volunteers_rows(db, load_csv(Path("data/volunteers_import_template.csv")))
        event_summary = import_events_rows(db, load_csv(Path("data/events_import_template.csv")))
        attendance_summary = import_attendance_rows(db, load_csv(Path("data/attendance_import_template.csv")))
        print(f"volunteers imported={volunteer_summary.imported} skipped={volunteer_summary.skipped} failed={volunteer_summary.failed}")
        print(f"events imported={event_summary.imported} skipped={event_summary.skipped} failed={event_summary.failed}")
        print(f"attendance imported={attendance_summary.imported} skipped={attendance_summary.skipped} failed={attendance_summary.failed}")
    finally:
        db.close()
