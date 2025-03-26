"""...
"""


MINYEAR = 1
MAXYEAR = 9999
DAYS_PER_WEEK = 7
DAYS_PER_MONTH = 30
MONTHS_PER_YEAR = 12

def set_temporal_structure(
    *,
    minyear: int | None = None,
    maxyear: int | None = None,
    days_per_week: int | None = None, 
    days_per_month: int | None = None,
    months_per_year: int | None = None, 
) -> None:
    global MINYEAR, MAXYEAR, DAYS_PER_WEEK, DAYS_PER_MONTH, MONTHS_PER_YEAR
    if minyear is not None:
        if minyear < 1:
            raise ValueError("minyear must be at least 1")
        MINYEAR = minyear
    if maxyear is not None:
        if maxyear > 9999:
            raise ValueError("maxyear must be at most 9999")
        MAXYEAR = maxyear
    if days_per_week is not None:
        if days_per_week < 1:
            raise ValueError("days_per_week must be at least 1")
        DAYS_PER_WEEK = days_per_week
    if days_per_month is not None:
        if days_per_month < 1:
            raise ValueError("days_per_month must be at least 1")
        DAYS_PER_MONTH = days_per_month
    if months_per_year is not None:
        if months_per_year < 1:
            raise ValueError("months_per_year must be at least 1")
        MONTHS_PER_YEAR = months_per_year