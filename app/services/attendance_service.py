from datetime import datetime


def compute_minutes_worked(checked_in_at: datetime, checked_out_at: datetime) -> int:
    seconds = (checked_out_at - checked_in_at).total_seconds()
    return max(0, int(seconds // 60))
