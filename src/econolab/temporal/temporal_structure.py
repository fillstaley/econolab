"""Specifications for the temporal structure of an EconoLab model."""

from dataclasses import dataclass, field
from typing import Sequence


@dataclass(frozen=True)
class TemporalStructure:
    """Defines the temporal structure of an EconoLab model.
    
    Parameters
    ----------
    minyear : int
        Smallest possible year (must be > 0).
    maxyear : int
        Largest possible year (must be > ``minyear``).
    days_per_week : int
        Number of days in a week (must be > 0).
    days_per_month : int or sequence of int
        If int, number of days in each month (must be > 0).
        If sequence, elements specify days in each month and the length
        specifies ``months_per_year``.
    months_per_year : int, optional
        Number of months in a year (must be > 0). Should be omitted if
        ``days_per_month`` is a sequence (it will be inferred from its length).
    
    Attributes
    ----------
    minyear : int
    maxyear : int
    days_per_week : int
    days_per_month : int or sequence of int
    months_per_year : int
    days_per_year : int
        Total days in a year, summing per-month lengths or uniform months.
    """
    minyear: int = field()
    maxyear: int = field()
    days_per_week: int = field()
    days_per_month: int | Sequence[int] = field()
    months_per_year: int  | None = field(default=None)
    
    
    def __post_init__(self):
        # Validate integer fields
        for name in ("minyear", "maxyear", "days_per_week"):  # these must be positive ints
            val = getattr(self, name)
            if not isinstance(val, int) or val <= 0:
                raise ValueError(f"{name} must be a positive integer, got {val!r}")

        # Validate maxyear
        if self.maxyear < self.minyear:
            raise ValueError(f"maxyear ({self.maxyear}) must be at least equal to minyear ({self.minyear})")

        # Validate days_per_month and infer months_per_year
        dpm = self.days_per_month
        if isinstance(dpm, int):
            if dpm <= 0:
                raise ValueError(f"days_per_month must be positive, got {dpm!r}")
            # ensure months_per_year provided
            if self.months_per_year is None:
                raise ValueError(
                    "months_per_year must be provided when days_per_month is an int"
                )
        elif isinstance(dpm, Sequence):
            # sequence case: validate elements and infer months_per_year
            for i, dm in enumerate(dpm):
                if not isinstance(dm, int) or dm <= 0:
                    raise ValueError(f"days_per_month[{i}] must be a positive integer, got {dm!r}")
            object.__setattr__(self, 'months_per_year', len(dpm))
        else:
            raise TypeError(
                f"days_per_month must be an int or sequence of ints, got {type(dpm).__name__}"
            )

    @property
    def days_per_year(self) -> int:
        """Total days in a year, summing per-month lengths or uniform months."""
        dpm = self.days_per_month
        return sum(dpm) if isinstance(dpm, Sequence) else self.months_per_year * dpm

# A sensible default (Gregorian-like) temporal structure
DEFAULT_TEMPORAL_STRUCTURE = TemporalStructure(
    minyear=1,
    maxyear=9999,
    days_per_week=7,
    days_per_month=30,
    months_per_year=12,
)
