"""initial tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    role_enum = sa.Enum("admin", "organiser", name="userrole")
    attendance_enum = sa.Enum("present", "absent", "late", name="attendancestatus")
    role_enum.create(op.get_bind(), checkfirst=True)
    attendance_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("event_category", sa.String(length=100), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_id"), "events", ["id"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "volunteers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("volunteer_no", sa.String(length=100), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_volunteers_email"), "volunteers", ["email"], unique=False)
    op.create_index(op.f("ix_volunteers_full_name"), "volunteers", ["full_name"], unique=False)
    op.create_index(op.f("ix_volunteers_id"), "volunteers", ["id"], unique=False)

    op.create_table(
        "shifts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("required_volunteers", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_shifts_event_id"), "shifts", ["event_id"], unique=False)
    op.create_index(op.f("ix_shifts_id"), "shifts", ["id"], unique=False)

    op.create_table(
        "attendances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("shift_id", sa.Integer(), nullable=False),
        sa.Column("volunteer_id", sa.Integer(), nullable=False),
        sa.Column("checked_in_at", sa.DateTime(), nullable=True),
        sa.Column("checked_out_at", sa.DateTime(), nullable=True),
        sa.Column("minutes_worked", sa.Integer(), nullable=False),
        sa.Column("status", attendance_enum, nullable=False),
        sa.ForeignKeyConstraint(["shift_id"], ["shifts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["volunteer_id"], ["volunteers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("shift_id", "volunteer_id", name="uq_shift_volunteer"),
    )
    op.create_index(op.f("ix_attendances_id"), "attendances", ["id"], unique=False)
    op.create_index(op.f("ix_attendances_shift_id"), "attendances", ["shift_id"], unique=False)
    op.create_index(op.f("ix_attendances_volunteer_id"), "attendances", ["volunteer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_attendances_volunteer_id"), table_name="attendances")
    op.drop_index(op.f("ix_attendances_shift_id"), table_name="attendances")
    op.drop_index(op.f("ix_attendances_id"), table_name="attendances")
    op.drop_table("attendances")
    op.drop_index(op.f("ix_shifts_id"), table_name="shifts")
    op.drop_index(op.f("ix_shifts_event_id"), table_name="shifts")
    op.drop_table("shifts")
    op.drop_index(op.f("ix_volunteers_id"), table_name="volunteers")
    op.drop_index(op.f("ix_volunteers_full_name"), table_name="volunteers")
    op.drop_index(op.f("ix_volunteers_email"), table_name="volunteers")
    op.drop_table("volunteers")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_events_id"), table_name="events")
    op.drop_table("events")
    sa.Enum(name="attendancestatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)
