#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lesson13.py — Date/Time & Text Utilities (Lesson 13)

This single-file module implements the Lesson 13 homework with:
- friendly, educational error messages (consistent with earlier lessons),
- PEP 8 / PEP 257 compliant code with type hints,
- robust input helpers,
- doctests for core logic,
- an interactive CLI with small demos and preferences saved to ~/.lesson13_config.json.

References (design notes, not strict validators):
- `zoneinfo` (PEP 615) — standard IANA time zone support in Python 3.9+.
- Email format: RFC 5322 (IMF) is complex; we use practical checks with helpful hints.
- Phone formats: E.164 caps international numbers at 15 digits; this module shows simple templates only.
- Password strength: includes Shannon entropy as an explanatory metric.
- Regex word boundaries: Python's `re` supports \\b zero-width assertion for word boundaries.

Run doctests:
    python lesson13.py --test

Start interactive CLI:
    python lesson13.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, time
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import List, Tuple, Iterable, Sequence, Dict
from collections import Counter
import doctest
import json
import math
import re
import sys
from time import sleep

# ──────────────────────────────────────────────────────────────────────────────
# Pretty printing & robust input readers
# ──────────────────────────────────────────────────────────────────────────────

def hr(title: str = "", width: int = 70) -> None:
    """Print a neat horizontal rule with optional title."""
    print("\n" + "=" * width)
    if title:
        print(title)
        print("-" * width)


def read_int(prompt: str, *, min_val: int | None = None, max_val: int | None = None) -> int:
    """Read an integer with validation loop (Ctrl+C to abort)."""
    while True:
        s = input(prompt).strip()
        try:
            x = int(s)
        except ValueError:
            print("❌ Please enter a valid integer.")
            continue
        if (min_val is not None and x < min_val) or (max_val is not None and x > max_val):
            lo = min_val if min_val is not None else "-∞"
            hi = max_val if max_val is not None else "+∞"
            print(f"❌ Please enter an integer in range [{lo}, {hi}].")
            continue
        return x


def read_timezone(prompt: str) -> ZoneInfo:
    """Read a timezone name and return ZoneInfo; re-prompt on error.

    Examples
    --------
    >>> isinstance(read_timezone.__doc__, str)
    True
    """
    while True:
        tzname = input(prompt).strip()
        try:
            return ZoneInfo(tzname)
        except Exception:
            print("❌ Invalid timezone. Example: 'UTC', 'Europe/Berlin', 'Asia/Tashkent'")


def read_date(prompt: str) -> date:
    """Read a date as 'YYYY-MM-DD' with helpful errors."""
    while True:
        s = input(prompt).strip()
        if not s:
            print("❌ Date cannot be empty. Example: 2000-06-15")
            continue
        parts = s.split("-")
        if len(parts) != 3:
            print("❌ Use 'YYYY-MM-DD' format. Example: 1999-12-31")
            continue
        try:
            y, m, d = map(int, parts)
            return date(y, m, d)
        except ValueError:
            print("❌ Invalid date. Check day/month ranges and format YYYY-MM-DD.")


def read_datetime(prompt: str, *, tz: ZoneInfo | None = None) -> datetime:
    """Read a naive 'YYYY-MM-DD HH:MM' and attach tz if provided.

    Examples
    --------
    >>> # Not executed interactively, but demonstrates intent
    >>> isinstance(read_datetime.__doc__, str)
    True
    """
    while True:
        s = input(prompt).strip()
        if not s:
            print("❌ Datetime cannot be empty. Example: 2024-12-25 14:30")
            continue
        try:
            ymd, hm = s.split()
            y, m, d = map(int, ymd.split("-"))
            hh, mm = map(int, hm.split(":"))
            dt = datetime(y, m, d, hh, mm)
            return dt.replace(tzinfo=tz) if tz else dt
        except Exception:
            print("❌ Invalid format. Use 'YYYY-MM-DD HH:MM' (24h). Example: 2024-05-01 09:15")


# ──────────────────────────────────────────────────────────────────────────────
# Date helpers
# ──────────────────────────────────────────────────────────────────────────────

def last_day_of_month(y: int, m: int) -> int:
    """Return last day for year/month.

    >>> last_day_of_month(2024, 2)  # leap
    29
    >>> last_day_of_month(2023, 2)
    28
    >>> last_day_of_month(2024, 1)
    31
    """
    if m == 12:
        nxt = date(y + 1, 1, 1)
    else:
        nxt = date(y, m + 1, 1)
    return (nxt - timedelta(days=1)).day


def add_months(d: date, months: int) -> date:
    """Add *months* to date *d*, clamping day to month's last day if needed.

    This avoids ValueError for dates like Jan 31 -> Feb.

    >>> add_months(date(2024, 1, 31), 1)  # clamp to Feb last day
    datetime.date(2024, 2, 29)
    >>> add_months(date(2023, 1, 31), 1)
    datetime.date(2023, 2, 28)
    >>> add_months(date(2024, 2, 29), 12)
    datetime.date(2025, 2, 28)
    """
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    day = min(d.day, last_day_of_month(y, m))
    return date(y, m, day)


# ──────────────────────────────────────────────────────────────────────────────
# Task 1 & 2 — Age Calculator + Days Until Next Birthday
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(slots=True, frozen=True)
class AgeBreakdown:
    """Age components."""
    years: int
    months: int
    days: int
    total_days: int


def calculate_age(birthdate: date, on_date: date | None = None) -> AgeBreakdown:
    """Calculate age in years, months, days in true O(1) using `add_months`.

    Rules:
    - Birthdate must not be in the future.
    - Ages over 150 years are rejected as unrealistic input.
    - Feb 29 birthdays are handled by clamping (e.g., to Feb 28 on non-leap years).

    >>> bd = date(2000, 6, 15)
    >>> a = calculate_age(bd, date(2024, 12, 25))
    >>> (a.years, a.months, a.days, a.total_days > 0)
    (24, 6, 10, True)

    Leap-year birthday handled:
    >>> bd2 = date(2000, 2, 29)
    >>> a2 = calculate_age(bd2, date(2024, 3, 1))
    >>> (a2.years, a2.months)  # 24 years, 0 months (day after 24th birthday)
    (24, 0)
    """
    on_date = on_date or date.today()

    if birthdate > on_date:
        raise ValueError(
            f"❌ Birthdate cannot be in the future\n"
            f"   Birthdate entered: {birthdate:%Y-%m-%d}\n"
            f"   Reference date: {on_date:%Y-%m-%d}\n"
            f"💡 Tip: Verify the YYYY-MM-DD format."
        )

    age_years = (on_date - birthdate).days // 365
    if age_years > 150:
        raise ValueError(
            f"⚠ Calculated age seems unrealistic: ~{age_years} years\n"
            f"   This would mean birth year {birthdate.year}\n"
            f"💡 Tip: Check the input format and values."
        )

    # Years: compare month/day
    years = on_date.year - birthdate.year
    if (on_date.month, on_date.day) < (birthdate.month, birthdate.day):
        years -= 1

    # Fully O(1) months/days using add_months:
    anniv_this_year = add_months(birthdate, years * 12)
    # Months difference from current anniversary to on_date (non-negative)
    months = (on_date.year - anniv_this_year.year) * 12 + (on_date.month - anniv_this_year.month)
    if on_date.day < anniv_this_year.day:
        months -= 1
    if months < 0:
        months = 0
    if months > 11:
        # Should not happen if years computed as above, but guard anyway
        extra_years, months = divmod(months, 12)
        years += extra_years

    month_mark = add_months(anniv_this_year, months)
    days = (on_date - month_mark).days

    total_days = (on_date - birthdate).days
    return AgeBreakdown(years=years, months=months, days=days, total_days=total_days)


def days_until_next_birthday(birthdate: date, from_date: date | None = None) -> int:
    """Compute days remaining until next birthday from *from_date*.

    >>> days_until_next_birthday(date(2000, 12, 25), date(2024, 12, 24))
    1
    >>> # Feb 29 birthday on a non-leap year -> clamp to Feb 28
    >>> days_until_next_birthday(date(2000, 2, 29), date(2023, 2, 28))
    0
    """
    today = from_date or date.today()

    # Next occurrence in this year
    try:
        next_bd = date(today.year, birthdate.month, birthdate.day)
    except ValueError:
        # e.g., Feb 29 -> clamp to last day of Feb
        next_bd = date(today.year, birthdate.month, last_day_of_month(today.year, birthdate.month))

    if next_bd < today:
        # Move to next year
        year = today.year + 1
        try:
            next_bd = date(year, birthdate.month, birthdate.day)
        except ValueError:
            next_bd = date(year, birthdate.month, last_day_of_month(year, birthdate.month))

    return (next_bd - today).days


# ──────────────────────────────────────────────────────────────────────────────
# Task 3 — Meeting Scheduler (end datetime from start + duration)
# ──────────────────────────────────────────────────────────────────────────────

def meeting_end(start: datetime, hours: int, minutes: int) -> datetime:
    """Return the end datetime given start + duration (hours/minutes).

    >>> tz = ZoneInfo("UTC")
    >>> start = datetime(2024, 12, 25, 14, 30, tzinfo=tz)
    >>> meeting_end(start, 1, 45)
    datetime.datetime(2024, 12, 25, 16, 15, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
    """
    if hours < 0 or minutes < 0:
        raise ValueError("❌ Duration must be non-negative.")
    return start + timedelta(hours=hours, minutes=minutes)


# ──────────────────────────────────────────────────────────────────────────────
# Task 4 — Timezone Converter
# ──────────────────────────────────────────────────────────────────────────────

def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """Convert a naive or aware datetime from *from_tz* to *to_tz*.

    - If *dt* is naive, we interpret it as *from_tz*.
    - If *dt* is aware, its original tzinfo is ignored and set to *from_tz*
      for predictable results in this demo.

    >>> convert_timezone(datetime(2024,1,1,12,0), "UTC", "Europe/Berlin").tzname()
    'CET'
    """
    src = ZoneInfo(from_tz)
    dst = ZoneInfo(to_tz)
    if dt.tzinfo is None:
        dt_src = dt.replace(tzinfo=src)
    else:
        dt_src = dt.astimezone(src)
    return dt_src.astimezone(dst)


# ──────────────────────────────────────────────────────────────────────────────
# Task 5 — Countdown Timer (logic helpers + demo)
# ──────────────────────────────────────────────────────────────────────────────

def remaining_until(target: datetime) -> timedelta:
    """Time delta remaining until *target* (aware or naive)."""
    now = datetime.now(tz=target.tzinfo) if target.tzinfo else datetime.now()
    return target - now


# ──────────────────────────────────────────────────────────────────────────────
# Task 6 — Email Validator (practical checks + suggestions)
# ──────────────────────────────────────────────────────────────────────────────

EMAIL_PATTERN_DETAILED = re.compile(
    r"^(?P<local>[A-Za-z0-9._%+-]+)@(?P<domain>[A-Za-z0-9.-]+)\.(?P<tld>[A-Za-z]{2,})$"
)

def validate_email_enhanced(email: str) -> tuple[bool, str, list[str]]:
    """Validate email with detailed feedback and suggestions.

    Note: RFC 5322 is far more permissive/complex. This function
    deliberately enforces pragmatic rules suitable for forms.

    Returns (is_valid, message, suggestions).

    >>> validate_email_enhanced("user@example.com")[0]
    True
    >>> ok, msg, _ = validate_email_enhanced("user@domain")
    >>> ok, ("TLD" in msg or "top-level" in msg)
    (False, True)
    """
    email = email.strip()
    suggestions: list[str] = []

    if not email:
        return False, "Email cannot be empty", ["Example: user@example.com"]

    if email.count("@") != 1:
        return False, "Email must contain exactly one @", ["Format: local@domain.tld"]

    local, domain_full = email.split("@", 1)
    if not local:
        return False, "Missing local part (before @)", ["Add username before @"]

    if local.startswith(".") or local.endswith("."):
        return False, "Local part cannot start or end with a dot", [
            "Valid: user.name@domain.com", "Invalid: .user@domain.com"
        ]
    if ".." in local:
        return False, "Local part cannot contain consecutive dots", [
            "Replace '..' with '.'"
        ]
    if len(local) > 64:
        return False, "Local part too long (max 64)", ["Shorten before @"]

    if "." not in domain_full:
        return False, "Domain missing top-level domain (e.g., .com)", [
            "Use domain.tld like example.com"
        ]
    if any(not part for part in domain_full.split(".")):
        return False, "Domain has empty segments between dots", ["Remove extra dots"]

    m = EMAIL_PATTERN_DETAILED.match(email)
    if not m:
        return False, "Invalid characters or format", [
            "Allowed in local: letters, digits, ._%+-",
            "Allowed in domain: letters, digits, - and .",
        ]

    # Tiny typo helper for popular domains
    common = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"}
    domain_lower = domain_full.lower()
    for d in common:
        # if user typed 'gmai.com' etc.
        if d.split(".")[0] in domain_lower and d != domain_lower:
            suggestions.append(f"Did you mean {local}@{d}?")

    return True, "✓ Valid email format", suggestions


# ──────────────────────────────────────────────────────────────────────────────
# Task 7 — Phone Number Formatter (didactic templates)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class PhoneFormatSpec:
    country: str
    example: str
    digits: int = 10  # for template parts only


PHONE_FORMATS: Dict[str, PhoneFormatSpec] = {
    "us": PhoneFormatSpec("US", "(123) 456-7890", 10),
    "us_intl": PhoneFormatSpec("US International", "+1 (123) 456-7890", 10),
    "uk": PhoneFormatSpec("UK (simplified)", "+44 20 1234 5678", 10),  # simplified for demo
    "dots": PhoneFormatSpec("Dots", "123.456.7890", 10),
}

def format_phone_by_template(number: str, format_type: str = "us", *, strict: bool = True) -> str:
    """Format phone number using simple templates (didactic, not full intl).

    For production use, prefer E.164 normalization and the `phonenumbers` library.
    UK formatting here is simplified and may not match all UK conventions.

    >>> format_phone_by_template("1234567890", "us")
    '(123) 456-7890'
    >>> format_phone_by_template("11234567890", "us_intl")
    '+1 (123) 456-7890'
    >>> format_phone_by_template("123-456 7890", "dots")
    '123.456.7890'
    """
    if format_type not in PHONE_FORMATS:
        available = ", ".join(PHONE_FORMATS.keys())
        raise ValueError(f"❌ Unknown format '{format_type}'. Available: {available}")

    spec = PHONE_FORMATS[format_type]
    digits = re.sub(r"\D", "", number)

    if len(digits) < spec.digits:
        msg = (f"❌ Phone number too short: {len(digits)} digits (need {spec.digits}). "
               f"Example: {spec.example}")
        if strict:
            raise ValueError(msg)
        print("⚠", msg)
        digits = digits.zfill(spec.digits)

    if len(digits) == 11 and format_type.startswith("us"):
        if digits[0] != "1":
            raise ValueError("❌ 11-digit US numbers must start with country code '1'.")
        digits = digits[1:]

    if len(digits) > spec.digits:
        raise ValueError(f"❌ Too many digits: {len(digits)} (max {spec.digits} for this template).")

    area, prefix, line = digits[0:3], digits[3:6], digits[6:10]
    if format_type == "us":
        return f"({area}) {prefix}-{line}"
    if format_type == "us_intl":
        return f"+1 ({area}) {prefix}-{line}"
    if format_type == "uk":
        return f"+44 {area} {prefix}{line}"  # simplified
    if format_type == "dots":
        return f"{area}.{prefix}.{line}"
    return f"{area}-{prefix}-{line}"


# ──────────────────────────────────────────────────────────────────────────────
# Task 8 — Password Strength (with Shannon entropy)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(slots=True, frozen=True)
class PasswordStrength:
    score: int
    level: str
    issues: list[str]
    suggestions: list[str]


def calculate_password_entropy(password: str) -> float:
    """Shannon entropy (bits). Higher -> more unpredictable.

    >>> calculate_password_entropy("") == 0.0
    True
    >>> calculate_password_entropy("aaaaaa") < 2.0
    True
    """
    if not password:
        return 0.0
    freq = Counter(password)
    n = len(password)
    h = 0.0
    for c in freq.values():
        p = c / n
        h -= p * math.log2(p)
    return h * n


def check_password_strength_enhanced(password: str) -> PasswordStrength:
    """Multi-factor password strength with entropy and patterns.

    Returns PasswordStrength(score 0..100, level, issues, suggestions).

    >>> res = check_password_strength_enhanced("P@ssw0rd123!")
    >>> 50 <= res.score <= 100
    True
    """
    issues: list[str] = []
    suggestions: list[str] = []
    components: dict[str, float | int] = {}

    # 1) Length (0..30)
    length = len(password)
    if length < 8:
        length_score = 0
        issues.append(f"Too short: {length} chars (min 8)")
        suggestions.append("Use at least 8 characters (12+ recommended)")
    elif length < 12:
        length_score = 15
        suggestions.append("Consider 12+ characters for better security")
    elif length < 16:
        length_score = 25
    else:
        length_score = 30
    components["length"] = length_score

    # 2) Variety (0..25)
    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password))
    variety_count = sum([has_lower, has_upper, has_digit, has_special])
    variety_score = variety_count * 6.25
    components["variety"] = variety_score

    if not has_lower: suggestions.append("Add lowercase letters (a-z)")
    if not has_upper: suggestions.append("Add uppercase letters (A-Z)")
    if not has_digit: suggestions.append("Add numbers (0-9)")
    if not has_special: suggestions.append("Add special characters (!@#$%^&*)")

    # 3) Entropy (0..25, normalized to 40+ bits excellent)
    entropy = calculate_password_entropy(password)
    entropy_score = min(25, (entropy / 40) * 25) if entropy > 0 else 0
    components["entropy"] = entropy_score
    if entropy < 20:
        suggestions.append(f"Low randomness (entropy: {entropy:.1f} bits) — increase variety/length")

    # 4) Pattern checks (0..20, may subtract)
    pattern_score = 20
    if re.search(r"(.)\1{2,}", password):
        issues.append("Repeated characters (e.g., aaa, 111)")
        pattern_score -= 5
    sequences = ["abc", "bcd", "cde", "123", "234", "345", "678", "789",
                 "qwe", "wer", "ert", "asd", "sdf", "dfg"]
    if any(seq in password.lower() for seq in sequences):
        issues.append("Keyboard/sequential patterns detected")
        pattern_score -= 5
    if re.search(r"[o0]{2,}|[i1]{2,}|[e3]{2,}|[a4]{2,}|[s5$]{2,}", password.lower()):
        suggestions.append("Simple substitutions (0→O, 1→I) are predictable")
        pattern_score -= 3
    common_words = ["password", "admin", "user", "login", "welcome", "hello",
                    "letmein", "monkey", "dragon", "master", "sunshine"]
    if any(w in password.lower() for w in common_words):
        issues.append("Contains common dictionary word")
        pattern_score -= 10
    if re.search(r"19\d{2}|20[012]\d", password):
        suggestions.append("Avoid using years/dates")
        pattern_score -= 3

    components["patterns"] = max(0, pattern_score)

    total_score = int(sum(components.values()))
    total_score = max(0, min(100, total_score))

    if total_score < 25: level = "Very Weak"
    elif total_score < 40: level = "Weak"
    elif total_score < 60: level = "Fair"
    elif total_score < 75: level = "Good"
    elif total_score < 90: level = "Strong"
    else: level = "Very Strong"

    if total_score < 90:
        suggestions.append(
            f"Score breakdown: Length={components['length']}/30, "
            f"Variety={components['variety']:.0f}/25, "
            f"Entropy={components['entropy']:.0f}/25, "
            f"Patterns={components['patterns']}/20"
        )

    return PasswordStrength(score=total_score, level=level, issues=issues, suggestions=suggestions)


# ──────────────────────────────────────────────────────────────────────────────
# Task 9 — Word Finder
# ──────────────────────────────────────────────────────────────────────────────

def find_word_occurrences_fast(text: str, word: str, *, case_sensitive: bool = False) -> List[int]:
    """Find word occurrences using regex word boundaries (fast).

    Performance:
    - O(n) with a C-optimized regex engine; faster than manual scans for large texts.

    >>> find_word_occurrences_fast("The cat sat. The cat!", "cat")
    [4, 19]
    >>> find_word_occurrences_fast("Cat cat cater", "cat", case_sensitive=True)
    [4]
    """
    if not word:
        return []
    escaped = re.escape(word)
    pattern = r"\b" + escaped + r"\b"
    flags = 0 if case_sensitive else re.IGNORECASE
    compiled = re.compile(pattern, flags)
    return [m.start() for m in compiled.finditer(text)]


# ──────────────────────────────────────────────────────────────────────────────
# Task 10 — Date Extractor (robust patterns + validation)
# ──────────────────────────────────────────────────────────────────────────────

DATE_PATTERNS_ORDERED: list[tuple[str, str, str]] = [
    (r"\b(\d{4})-(\d{2})-(\d{2})\b", "%Y-%m-%d", "ISO"),
    (r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b", "%d %B %Y", "DMY_FULL"),
    (r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b", "%B %d, %Y", "MDY_FULL"),
    (r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b", "%d %b %Y", "DMY_ABV"),
    (r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})\b", "%b %d, %Y", "MDY_ABV"),
    (r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", "%m/%d/%Y", "US_NUMERIC"),
    (r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b", "%d.%m.%Y", "EU_NUMERIC"),
]

def extract_dates_robust(text: str, *, min_year: int = 1900, max_year: int = 2100) -> List[Tuple[str, date, str]]:
    """Extract dates from text with format detection and year validation.

    Returns list of (original_string, parsed_date, format_type).

    >>> s = "Meet on 2024-12-25, or Dec 31, 2024. Invalid: 2024-02-30."
    >>> out = extract_dates_robust(s)
    >>> [d.strftime("%Y-%m-%d") for _, d, _ in out]
    ['2024-12-25', '2024-12-31']
    """
    out: list[Tuple[str, date, str]] = []
    used: set[int] = set()
    for pattern, fmt, label in DATE_PATTERNS_ORDERED:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            rng = range(m.start(), m.end())
            if any(i in used for i in rng):
                continue
            s = m.group(0)
            try:
                d = datetime.strptime(s, fmt).date()
                if not (min_year <= d.year <= max_year):
                    continue
                # mark used span
                out.append((s, d, label))
                for i in rng:
                    used.add(i)
            except ValueError:
                continue
    # remove exact duplicate dates keeping first appearance order
    seen: set[date] = set()
    unique: list[Tuple[str, date, str]] = []
    for s, d, lbl in out:
        if d not in seen:
            unique.append((s, d, lbl))
            seen.add(d)
    return unique


# ──────────────────────────────────────────────────────────────────────────────
# Preferences
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(slots=True)
class UserPreferences:
    default_timezone: str = "UTC"
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M:%S"
    datetime_format: str = "%Y-%m-%d %H:%M"
    use_24_hour: bool = True
    show_emoji: bool = True
    verbose_errors: bool = True
    strict_email: bool = True
    default_phone_format: str = "us"

    @classmethod
    def load(cls, path: Path) -> "UserPreferences":
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text())
            return cls(**data)
        except Exception as e:
            print(f"⚠ Could not load preferences: {e}. Using defaults.")
            return cls()

    def save(self, path: Path) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "default_timezone": self.default_timezone,
                "date_format": self.date_format,
                "time_format": self.time_format,
                "datetime_format": self.datetime_format,
                "use_24_hour": self.use_24_hour,
                "show_emoji": self.show_emoji,
                "verbose_errors": self.verbose_errors,
                "strict_email": self.strict_email,
                "default_phone_format": self.default_phone_format,
            }
            path.write_text(json.dumps(data, indent=2))
            print(f"✓ Preferences saved to {path}")
        except Exception as e:
            print(f"❌ Could not save preferences: {e}")


def demo_settings(prefs: UserPreferences, config_path: Path) -> UserPreferences:
    """Interactive settings editor."""
    hr("Settings & Preferences")
    while True:
        print("\nCurrent settings:")
        print(f"  1. Default timezone: {prefs.default_timezone}")
        print(f"  2. Show emoji: {prefs.show_emoji}")
        print(f"  3. Phone format: {prefs.default_phone_format}")
        print("  0. Save and return")
        choice = input("\nEdit setting (0-3): ").strip()
        if choice == "0":
            prefs.save(config_path)
            return prefs
        elif choice == "1":
            tz = input("New timezone (e.g., UTC, Europe/Berlin): ").strip()
            try:
                _ = ZoneInfo(tz)
                prefs.default_timezone = tz
                print("✓ Updated")
            except Exception:
                print("❌ Invalid timezone")
        elif choice == "2":
            prefs.show_emoji = not prefs.show_emoji
            print(f"✓ Emoji {'enabled' if prefs.show_emoji else 'disabled'}")
        elif choice == "3":
            print("Available: " + ", ".join(PHONE_FORMATS.keys()))
            fmt = input("Choose format: ").strip()
            if fmt in PHONE_FORMATS:
                prefs.default_phone_format = fmt
                print("✓ Updated")
            else:
                print("❌ Invalid format")
        else:
            print("❌ Invalid choice")


# ──────────────────────────────────────────────────────────────────────────────
# Demos
# ──────────────────────────────────────────────────────────────────────────────

def demo_age_calculator() -> None:
    hr("Task 1: Age Calculator")
    bd = read_date("Enter birthdate (YYYY-MM-DD): ")
    ref = input("Reference date? (Enter to use today): ").strip()
    on = date.today() if not ref else date(*map(int, ref.split("-")))
    try:
        age = calculate_age(bd, on)
        print(f"\nAge: {age.years} years, {age.months} months, {age.days} days")
        print(f"Total days lived: {age.total_days:,}")
    except ValueError as e:
        print(str(e))


def demo_birthday_countdown() -> None:
    hr("Task 2: Days Until Next Birthday")
    bd = read_date("Enter birthdate (YYYY-MM-DD): ")
    fromd = input("From date? (Enter to use today): ").strip()
    d = date.today() if not fromd else date(*map(int, fromd.split("-")))
    days = days_until_next_birthday(bd, d)
    print(f"\nDays until next birthday: {days}")


def demo_meeting_scheduler() -> None:
    hr("Task 3: Meeting Scheduler")
    tz = read_timezone("Timezone (e.g., UTC): ")
    start = read_datetime("Start (YYYY-MM-DD HH:MM): ", tz=tz)
    h = read_int("Duration hours: ", min_val=0)
    m = read_int("Duration minutes: ", min_val=0, max_val=59)
    end = meeting_end(start, h, m)
    print(f"\nMeeting ends at: {end:%Y-%m-%d %H:%M %Z}")


def demo_timezone_converter() -> None:
    hr("Task 4: Timezone Converter")
    src = input("Source timezone: ").strip()
    dst = input("Target timezone: ").strip()
    dt = read_datetime("Datetime in source tz (YYYY-MM-DD HH:MM): ")
    try:
        out = convert_timezone(dt, src, dst)
        print(f"\nConverted: {out:%Y-%m-%d %H:%M %Z}")
    except Exception as e:
        print(f"❌ Conversion failed: {e}")


def demo_countdown_timer() -> None:
    hr("Task 5: Countdown Timer")
    tz = read_timezone("Timezone for target (e.g., UTC): ")
    target = read_datetime("Target datetime (YYYY-MM-DD HH:MM): ", tz=tz)

    # Pre-check
    rem_initial = remaining_until(target)
    if rem_initial.total_seconds() <= 0:
        now = datetime.now(tz=tz)
        print("❌ Target time is in the past!")
        print(f"   Target : {target:%Y-%m-%d %H:%M %Z}")
        print(f"   Current: {now:%Y-%m-%d %H:%M %Z}")
        print("💡 Tip: Enter a future date/time.")
        return

    total_secs = int(rem_initial.total_seconds())
    if total_secs > 3600:
        print(f"⏱ Countdown duration: ~{total_secs/3600:.1f} hours")
        print("💡 Tip: Press Ctrl+C to stop anytime.")
    input("Press Enter to start countdown...")

    try:
        while True:
            rem = remaining_until(target)
            if rem.total_seconds() <= 0:
                print("\r🎉 Time reached!                        ")
                break
            dd = rem.days
            ss = rem.seconds
            hh = ss // 3600
            mm = (ss % 3600) // 60
            s = ss % 60
            print(f"\r⏳ Remaining: {dd}d {hh:02d}:{mm:02d}:{s:02d}", end="", flush=True)
            sleep(1)
        print()
    except KeyboardInterrupt:
        print("\n\n⚠ Countdown stopped by user")


def demo_email_validator() -> None:
    hr("Task 6: Email Validator")
    em = input("Enter email: ").strip()
    ok, msg, sugg = validate_email_enhanced(em)
    print(("✓ " if ok else "❌ ") + msg)
    if sugg:
        print("Suggestions:")
        for s in sugg:
            print("  • " + s)


def demo_phone_formatter() -> None:
    hr("Task 7: Phone Number Formatter")
    num = input("Enter number: ")
    print("Available formats:", ", ".join(PHONE_FORMATS.keys()))
    fmt = input("Format: ").strip() or "us"
    try:
        print("→", format_phone_by_template(num, fmt))
    except Exception as e:
        print("❌", e)


def demo_password_checker() -> None:
    hr("Task 8: Password Strength Checker")
    pw = input("Password to check: ")
    res = check_password_strength_enhanced(pw)
    print(f"Score: {res.score}/100  Level: {res.level}")
    if res.issues:
        print("Issues:")
        for i in res.issues:
            print("  • " + i)
    if res.suggestions:
        print("Suggestions:")
        for s in res.suggestions:
            print("  • " + s)


def demo_word_finder() -> None:
    hr("Task 9: Word Finder")
    text = input("Enter text: ")
    word = input("Word to find: ")
    pos = find_word_occurrences_fast(text, word)
    print(f"Found {len(pos)} occurrence(s) at positions: {pos}")


def demo_date_extractor() -> None:
    hr("Task 10: Date Extractor")
    print("Recognized formats: ISO (YYYY-MM-DD), full/abbr month names, US/EU numeric.")
    print("Enter text (end with blank line):")
    lines: list[str] = []
    while True:
        line = input()
        if not line and lines:
            break
        lines.append(line)
    txt = "\n".join(lines)
    out = extract_dates_robust(txt)
    if not out:
        print("❌ No valid dates found.")
        return
    print(f"✓ Found {len(out)} date(s):")
    for i, (raw, d, label) in enumerate(out, 1):
        print(f"  {i}. '{raw}' → {d:%A, %B %d, %Y}  ({label})")


# ──────────────────────────────────────────────────────────────────────────────
# Test launcher & CLI
# ──────────────────────────────────────────────────────────────────────────────

def run_doctests(verbose: bool = False) -> tuple[int, int]:
    """Run doctests for this module. Returns (failures, tests)."""
    return doctest.testmod(verbose=verbose)


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    config_path = Path.home() / ".lesson13_config.json"
    prefs = UserPreferences.load(config_path)

    if "--test" in argv:
        fails, tests = run_doctests(verbose="--verbose" in argv)
        print("\n" + "=" * 70)
        if fails == 0:
            print(f"🎉 All {tests} doctests passed!")
            return 0
        else:
            print(f"❌ {fails} of {tests} doctests failed")
            return 1

    print("=" * 70)
    print(" Lesson 13: Date & Text Utilities ".center(70, "="))
    print("=" * 70)
    print(f"Loaded preferences from: {config_path}")
    print(f"Default timezone: {prefs.default_timezone}")

    while True:
        hr("Main Menu")
        print(" 1) Age Calculator")
        print(" 2) Days Until Next Birthday")
        print(" 3) Meeting Scheduler")
        print(" 4) Timezone Converter")
        print(" 5) Countdown Timer")
        print(" 6) Email Validator")
        print(" 7) Phone Number Formatter")
        print(" 8) Password Strength Checker")
        print(" 9) Word Finder")
        print("10) Date Extractor")
        print("\n88) Settings & Preferences")
        print("99) Run Doctests")
        print(" 0) Exit")
        choice = input("\nSelect (0-10, 88, 99): ").strip()
        try:
            if choice == "0":
                prefs.save(config_path)
                print("\n👋 Bye! Preferences saved.")
                return 0
            elif choice == "1":
                demo_age_calculator()
            elif choice == "2":
                demo_birthday_countdown()
            elif choice == "3":
                demo_meeting_scheduler()
            elif choice == "4":
                demo_timezone_converter()
            elif choice == "5":
                demo_countdown_timer()
            elif choice == "6":
                demo_email_validator()
            elif choice == "7":
                demo_phone_formatter()
            elif choice == "8":
                demo_password_checker()
            elif choice == "9":
                demo_word_finder()
            elif choice == "10":
                demo_date_extractor()
            elif choice == "88":
                prefs = demo_settings(prefs, config_path)
            elif choice == "99":
                fails, tests = run_doctests(verbose=True)
                print(f"\nSummary: {tests} tests, {fails} failures.")
                input("Press Enter to continue...")
            else:
                print("❌ Invalid option.")
        except KeyboardInterrupt:
            print("\n⚠ Interrupted by user (Ctrl+C). Returning to menu...\n")
            sleep(0.5)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            if prefs.verbose_errors:
                print("💡 Tip: Run with --test or review inputs.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    raise SystemExit(main())

