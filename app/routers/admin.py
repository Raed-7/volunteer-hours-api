import csv
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.db.session import get_db
from app.schemas.imports import AdminImportResponse, ImportSummary
from app.services.import_service import (
    Summary,
    import_attendance_rows,
    import_events_rows,
    import_volunteers_rows,
    load_csv,
)

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])
DATA_DIR = Path("data")


def _to_summary(summary: Summary) -> ImportSummary:
    return ImportSummary(imported=summary.imported, skipped=summary.skipped, failed=summary.failed)


async def _parse_upload(file: UploadFile | None) -> list[dict[str, str]]:
    if not file:
        return []
    content = (await file.read()).decode("utf-8-sig")
    return list(csv.DictReader(content.splitlines()))


@router.post("/import", response_model=AdminImportResponse)
async def admin_import(
    db: Session = Depends(get_db),
    volunteers_file: UploadFile | None = File(default=None),
    events_file: UploadFile | None = File(default=None),
    attendance_file: UploadFile | None = File(default=None),
) -> AdminImportResponse:
    volunteers_rows = await _parse_upload(volunteers_file)
    if not volunteers_rows and (DATA_DIR / "volunteers_import_template.csv").exists():
        volunteers_rows = load_csv(DATA_DIR / "volunteers_import_template.csv")

    events_rows = await _parse_upload(events_file)
    if not events_rows and (DATA_DIR / "events_import_template.csv").exists():
        events_rows = load_csv(DATA_DIR / "events_import_template.csv")

    attendance_rows = await _parse_upload(attendance_file)
    if not attendance_rows and (DATA_DIR / "attendance_import_template.csv").exists():
        attendance_rows = load_csv(DATA_DIR / "attendance_import_template.csv")

    volunteers = import_volunteers_rows(db, volunteers_rows)
    events = import_events_rows(db, events_rows)
    attendance = import_attendance_rows(db, attendance_rows)

    return AdminImportResponse(
        volunteers=_to_summary(volunteers),
        events=_to_summary(events),
        attendance=_to_summary(attendance),
    )
