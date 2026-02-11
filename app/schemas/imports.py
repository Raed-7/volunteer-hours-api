from pydantic import BaseModel


class ImportSummary(BaseModel):
    imported: int
    skipped: int
    failed: int


class AdminImportResponse(BaseModel):
    volunteers: ImportSummary
    events: ImportSummary
    attendance: ImportSummary
