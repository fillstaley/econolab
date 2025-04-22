"""...

...
"""

import pytest
from econolab.temporal import EconoDate, EconoDuration, MINYEAR, MAXYEAR, DAYS_PER_MONTH, MONTHS_PER_YEAR


@pytest.mark.parametrize("year,month,day", [
    (MINYEAR, 1, 1),
    (2025, 4, 22),
    (MAXYEAR, MONTHS_PER_YEAR, DAYS_PER_MONTH),
])
def test_to_days_and_from_days_round_trip(year, month, day):
    d = EconoDate(year, month, day)
    days = d.to_days()
    assert EconoDate.from_days(days) == d

def test_simple_addition_and_subtraction():
    d0 = EconoDate(2025, 4, 22)
    one_day = EconoDuration(days=1)
    assert d0 + one_day == EconoDate(2025, 4, 23)
    # radd should work the same
    assert one_day + d0 == EconoDate(2025, 4, 23)
    # subtracting the same duration returns you to d0
    assert (d0 + one_day) - one_day == d0

def test_boundary_rollovers():
    # end-of-month → next month
    end_april = EconoDate(2025, 4, DAYS_PER_MONTH)
    assert end_april + EconoDuration(days=1) == EconoDate(2025, 5, 1)
    # end-of-year → next year
    end_year = EconoDate(2025, MONTHS_PER_YEAR, DAYS_PER_MONTH)
    assert end_year + EconoDuration(days=1) == EconoDate(2026, 1, 1)

def test_negative_duration_and_date_diff():
    d = EconoDate(2025,5,10)
    dur = EconoDuration(days=15)
    earlier = d - dur
    # going back and forth lands you right back
    assert earlier + dur == d
    # date - date yields a duration
    assert (d - earlier) == dur

def test_duration_arithmetic_and_comparisons():
    d1 = EconoDuration(days=7)
    d2 = EconoDuration(days=3)
    assert d1 + d2 == EconoDuration(days=10)
    assert d1 - d2 == EconoDuration(days=4)
    assert d2 * 3 == EconoDuration(days=9)
    assert d1 // d2 == 2
    assert (d1 / d2) == pytest.approx(7/3)
    assert not bool(EconoDuration(0))
    assert EconoDuration(5) > EconoDuration(2)

@pytest.mark.parametrize("invalid", [
    (2025, 0, 10),        # month zero
    (2025, 13, 10),       # month > MONTHS_PER_YEAR
    (2025, 5, 0),         # day zero
    (2025, 5, DAYS_PER_MONTH+1),  # day overflow
    (MINYEAR-1, 1, 1),    # year too small
    (MAXYEAR+1, 1, 1),    # year too big
])
def test_econodate_invalid_constructor(invalid):
    year, month, day = invalid
    with pytest.raises(ValueError):
        EconoDate(year, month, day)
