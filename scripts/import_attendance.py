from pathlib import Path

from app.db.session import SessionLocal
from app.services.import_service import import_attendance_rows, load_csv


if __name__ == "__main__":
    db = SessionLocal()
    try:
        rows = load_csv(Path("data/attendance_import_template.csv"))
        summary = import_attendance_rows(db, rows)
        print(f"attendance imported={summary.imported} skipped={summary.skipped} failed={summary.failed}")
    finally:
        db.close()
