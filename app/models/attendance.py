import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent = "absent"
    late = "late"


class Attendance(Base):
    __tablename__ = "attendances"
    __table_args__ = (UniqueConstraint("shift_id", "volunteer_id", name="uq_shift_volunteer"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False, index=True)
    volunteer_id: Mapped[int] = mapped_column(ForeignKey("volunteers.id", ondelete="CASCADE"), nullable=False, index=True)
    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    checked_out_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    minutes_worked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), default=AttendanceStatus.present, nullable=False)

    shift = relationship("Shift", back_populates="attendances")
    volunteer = relationship("Volunteer", back_populates="attendances")
