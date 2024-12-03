from datetime import datetime


def days_passed_in_month(month: int, year: int) -> int:
    today = datetime.now()

    if year > today.year or (year == today.year and month > today.month):
        return 0

    if year < today.year or (year == today.year and month < today.month):
        from calendar import monthrange
        return monthrange(year, month)[1]

    return today.day