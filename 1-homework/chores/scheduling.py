import calendar
from datetime import date, timedelta

from .models import Chore


def next_due_date(due_date, recurrence):
    if due_date is None or recurrence == Chore.Recurrence.NONE:
        return None
    if recurrence == Chore.Recurrence.DAILY:
        return due_date + timedelta(days=1)
    if recurrence == Chore.Recurrence.WEEKLY:
        return due_date + timedelta(weeks=1)
    if recurrence == Chore.Recurrence.MONTHLY:
        year = due_date.year + (due_date.month == 12)
        month = 1 if due_date.month == 12 else due_date.month + 1
        day = min(due_date.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)
    raise ValueError(f"Unsupported recurrence: {recurrence}")
