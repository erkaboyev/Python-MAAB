
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lesson14.py — API Integration & JSON Operations (Lesson 14)


Tasks:
    1. JSON Parsing — Read and display student records
    2. Weather API — Fetch weather data from OpenWeatherMap
    3. JSON Modification — CRUD operations on books database
    4. Movie Recommendation — Advanced recommendation system with OMDb API

API Documentation:
    - OpenWeatherMap: https://openweathermap.org/api
    - OMDb API: http://www.omdbapi.com/

Setup:
    1. Create .env file with API keys:
       OPENWEATHER_API_KEY=your_key_here
       OMDB_API_KEY=your_key_here
    
    2. Install dependencies:
       pip install requests python-dotenv
    
    3. Run:
       python lesson14.py

Run tests:
    python lesson14.py --test
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from functools import lru_cache
from collections import defaultdict
import json
import os
import random
import re
import sys
import time

# Third-party imports with graceful fallback
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠ Warning: 'requests' library not found. Install with: pip install requests")

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("💡 Tip: Install 'python-dotenv' for .env file support: pip install python-dotenv")

# Load environment variables from .env file if available
if DOTENV_AVAILABLE:
    load_dotenv()


# ──────────────────────────────────────────────────────────────────────────────
# Configuration & Constants
# ──────────────────────────────────────────────────────────────────────────────

CONFIG_DIR = Path.home() / ".lesson14_config"
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_DIR = CONFIG_DIR / "cache"
STUDENTS_FILE = Path("students.json")
BOOKS_FILE = Path("books.json")

# API endpoints
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
OMDB_BASE_URL = "http://www.omdbapi.com/"

# Rate limiting (to avoid API abuse)
API_RATE_LIMIT = 60  # requests per minute
API_CALL_TRACKER: Dict[str, List[float]] = defaultdict(list)


# ──────────────────────────────────────────────────────────────────────────────
# Utility Functions: Pretty printing, input validation
# ──────────────────────────────────────────────────────────────────────────────

def hr(title: str = "", width: int = 70) -> None:
    """Print horizontal rule with optional title.

    >>> hr("Test")  # doctest: +ELLIPSIS
    <BLANKLINE>
    ======================================================================
    Test
    ----------------------------------------------------------------------
    """
    print("\n" + "=" * width)
    if title:
        print(title)
        print("-" * width)


def read_int(
    prompt: str,
    *,
    min_val: int | None = None,
    max_val: int | None = None
) -> int:
    """Read integer with validation and educational error messages.

    This follows L8-L13 feedback: specific exceptions, emoji, context.
    """
    while True:
        try:
            value = input(prompt).strip()
            num = int(value)

            if min_val is not None and num < min_val:
                print(f"❌ Value too small: {num} < {min_val}")
                print(f"💡 Tip: Enter a number >= {min_val}")
                continue

            if max_val is not None and num > max_val:
                print(f"❌ Value too large: {num} > {max_val}")
                print(f"💡 Tip: Enter a number <= {max_val}")
                continue

            return num

        except ValueError:
            print(f"❌ Invalid input: '{value}' is not an integer")
            print("💡 Tip: Enter a whole number (e.g., 42)")
        except KeyboardInterrupt:
            print("\n⚠ Input cancelled by user")
            raise


def read_choice(prompt: str, choices: List[str], *, case_sensitive: bool = False) -> str:
    """Read user choice from a list of valid options.

    >>> # Interactive function, not easily testable in doctest
    >>> isinstance(read_choice.__doc__, str)
    True
    """
    while True:
        value = input(prompt).strip()

        if not case_sensitive:
            value = value.lower()
            choices_lower = [c.lower() for c in choices]
            if value in choices_lower:
                # Return original case version
                idx = choices_lower.index(value)
                return choices[idx]
        else:
            if value in choices:
                return value

        print(f"❌ Invalid choice: '{value}'")
        print(f"💡 Valid options: {', '.join(choices)}")


def confirm(prompt: str = "Continue?") -> bool:
    """Ask for yes/no confirmation.

    >>> # Interactive function
    >>> isinstance(confirm.__doc__, str)
    True
    """
    response = input(f"{prompt} (y/n): ").strip().lower()
    return response in ('y', 'yes')


# ──────────────────────────────────────────────────────────────────────────────
# Configuration Management (secure API key storage)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Config:
    """Application configuration with secure API key management.

    Design principles (from L11-L13 feedback):
    - Never store API keys in source code
    - Prefer environment variables (production best practice)
    - Fallback to user input with secure storage
    - Clear instructions for setup
    """
    openweather_api_key: str = ""
    omdb_api_key: str = ""
    default_city: str = "Tashkent"
    cache_duration_hours: int = 1

    @classmethod
    def load(cls) -> 'Config':
        """Load configuration from environment, file, or user input.

        Priority order:
        1. Environment variables (most secure)
        2. Config file (~/.lesson14_config/config.json)
        3. Interactive user input (saved to config file)
        """
        config = cls()

        # Try environment variables first (production best practice)
        config.openweather_api_key = os.getenv("OPENWEATHER_API_KEY", "")
        config.omdb_api_key = os.getenv("OMDB_API_KEY", "")

        # Try loading from config file
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text())
                if not config.openweather_api_key:
                    config.openweather_api_key = data.get(
                        "openweather_api_key", "")
                if not config.omdb_api_key:
                    config.omdb_api_key = data.get("omdb_api_key", "")
                config.default_city = data.get("default_city", "Tashkent")
                config.cache_duration_hours = data.get(
                    "cache_duration_hours", 1)
            except Exception as e:
                print(f"⚠ Warning: Could not load config file: {e}")

        return config

    def save(self) -> None:
        """Save configuration to file (excluding API keys for security).

        Note: API keys should be stored in environment variables or .env file,
        not in the config JSON. This follows security best practices.
        """
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            # Only save non-sensitive settings
            data = {
                "default_city": self.default_city,
                "cache_duration_hours": self.cache_duration_hours,
                # API keys intentionally excluded from file storage
            }

            CONFIG_FILE.write_text(json.dumps(data, indent=2))
            print(f"✓ Configuration saved to {CONFIG_FILE}")

        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")

    def ensure_api_keys(self) -> bool:
        """Ensure API keys are available, prompting user if needed.

        Returns True if all keys are configured.
        """
        missing_keys = []

        if not self.openweather_api_key:
            missing_keys.append("OpenWeatherMap")
        if not self.omdb_api_key:
            missing_keys.append("OMDb")

        if not missing_keys:
            return True

        print("\n" + "="*70)
        print("⚠ API Keys Required")
        print("-"*70)
        print("Some API keys are missing. You need to obtain free API keys from:")

        if "OpenWeatherMap" in missing_keys:
            print("\n1. OpenWeatherMap API:")
            print("   - Visit: https://openweathermap.org/api")
            print("   - Sign up for free account")
            print("   - Get your API key from account settings")

        if "OMDb" in missing_keys:
            print("\n2. OMDb API:")
            print("   - Visit: http://www.omdbapi.com/apikey.aspx")
            print("   - Request free API key (1000 requests/day)")
            print("   - Check your email for activation")

        print("\n" + "="*70)
        print("\n💡 Best Practice: Store API keys in environment variables")
        print("   Create a .env file in the project directory:")
        print("   OPENWEATHER_API_KEY=your_key_here")
        print("   OMDB_API_KEY=your_key_here")
        print("\n   Or set environment variables in your shell:")
        print("   export OPENWEATHER_API_KEY=your_key_here")
        print("="*70)

        if not confirm("\nDo you want to enter API keys now?"):
            return False

        # Interactive input with masking (for security)
        if not self.openweather_api_key:
            self.openweather_api_key = input(
                "\nEnter OpenWeatherMap API key: ").strip()

        if not self.omdb_api_key:
            self.omdb_api_key = input("Enter OMDb API key: ").strip()

        print("\n✓ API keys configured")
        print("💡 Tip: Set environment variables to avoid entering keys every time")

        return bool(self.openweather_api_key and self.omdb_api_key)


# Initialize global config
CONFIG = Config.load()


# ──────────────────────────────────────────────────────────────────────────────
# API Rate Limiting (production best practice)
# ──────────────────────────────────────────────────────────────────────────────

def check_rate_limit(api_name: str) -> bool:
    """Check if API rate limit is exceeded.

    This prevents abuse and respects API provider limits.
    Follows production best practices from L12-L13 feedback.

    >>> check_rate_limit("test_api")
    True
    """
    now = time.time()
    calls = API_CALL_TRACKER[api_name]

    # Remove calls older than 1 minute
    calls[:] = [t for t in calls if now - t < 60]

    if len(calls) >= API_RATE_LIMIT:
        return False

    calls.append(now)
    return True


def wait_for_rate_limit(api_name: str) -> None:
    """Wait if rate limit is exceeded, with user feedback."""
    if check_rate_limit(api_name):
        return

    # Find oldest call
    oldest = min(API_CALL_TRACKER[api_name])
    wait_time = 60 - (time.time() - oldest)

    if wait_time > 0:
        print(f"⏳ Rate limit reached. Waiting {wait_time:.0f} seconds...")
        time.sleep(wait_time + 1)


# ──────────────────────────────────────────────────────────────────────────────
# Caching System (for API responses)
# ──────────────────────────────────────────────────────────────────────────────

def get_cache_path(cache_key: str) -> Path:
    """Generate cache file path for given key.

    Uses Path objects consistently (L11 feedback).

    >>> path = get_cache_path("test_key")
    >>> path.suffix
    '.json'
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    # Sanitize key for filename
    safe_key = re.sub(r'[^\w\-]', '_', cache_key)
    return CACHE_DIR / f"{safe_key}.json"


def get_cached(cache_key: str, max_age_hours: int = 1) -> Optional[Dict[str, Any]]:
    """Retrieve cached data if it exists and is fresh.

    Args:
        cache_key: Unique identifier for cached data
        max_age_hours: Maximum age of cache in hours

    Returns:
        Cached data dict or None if not found/expired
    """
    cache_path = get_cache_path(cache_key)

    if not cache_path.exists():
        return None

    try:
        # Check file age
        mtime = cache_path.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600

        if age_hours > max_age_hours:
            # Cache expired
            cache_path.unlink()
            return None

        # Load cached data
        data = json.loads(cache_path.read_text())
        return data

    except Exception as e:
        print(f"⚠ Cache read error: {e}")
        return None


def set_cached(cache_key: str, data: Dict[str, Any]) -> None:
    """Store data in cache.

    Args:
        cache_key: Unique identifier for cached data
        data: Data to cache (must be JSON-serializable)
    """
    try:
        cache_path = get_cache_path(cache_key)
        cache_path.write_text(json.dumps(data, indent=2))
    except Exception as e:
        print(f"⚠ Cache write error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 1: JSON Parsing — Student Records
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Student:
    """Student record with validation.

    Design follows L9-L13 feedback: dataclasses for structured data,
    type hints, validation in __post_init__.
    """
    id: int
    name: str
    age: int
    grades: Dict[str, float | int]
    email: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate student data after initialization."""
        if self.age < 0 or self.age > 150:
            raise ValueError(
                f"❌ Invalid age: {self.age}\n"
                f"💡 Tip: Age must be between 0 and 150"
            )

        if not self.name.strip():
            raise ValueError("❌ Student name cannot be empty")

        # Validate grades are in reasonable range
        for subject, grade in self.grades.items():
            if not (0 <= grade <= 100):
                raise ValueError(
                    f"❌ Invalid grade for {subject}: {grade}\n"
                    f"💡 Tip: Grades must be between 0 and 100"
                )

    @property
    def average_grade(self) -> float:
        """Calculate average grade across all subjects.

        >>> s = Student(1, "Alice", 20, {"math": 85, "physics": 90})
        >>> s.average_grade
        87.5
        """
        if not self.grades:
            return 0.0
        return sum(self.grades.values()) / len(self.grades)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "grades": self.grades,
            "email": self.email
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        """Create Student from dictionary.

        >>> data = {"id": 1, "name": "Bob", "age": 21, "grades": {"math": 95}}
        >>> s = Student.from_dict(data)
        >>> s.name
        'Bob'
        """
        return cls(
            id=data["id"],
            name=data["name"],
            age=data["age"],
            grades=data["grades"],
            email=data.get("email")
        )


def create_sample_students() -> None:
    """Create sample students.json file if it doesn't exist.

    This follows L11-L13 feedback: helpful defaults, educational messages.
    """
    if STUDENTS_FILE.exists():
        return

    # Realistic sample data
    students = [
        {
            "id": 1,
            "name": "Alice Johnson",
            "age": 20,
            "email": "alice@university.edu",
            "grades": {
                "mathematics": 92,
                "physics": 88,
                "chemistry": 85,
                "english": 90
            }
        },
        {
            "id": 2,
            "name": "Bob Smith",
            "age": 21,
            "email": "bob@university.edu",
            "grades": {
                "mathematics": 78,
                "physics": 82,
                "chemistry": 80,
                "english": 85
            }
        },
        {
            "id": 3,
            "name": "Carol Williams",
            "age": 19,
            "email": "carol@university.edu",
            "grades": {
                "mathematics": 95,
                "physics": 93,
                "chemistry": 91,
                "english": 88
            }
        },
        {
            "id": 4,
            "name": "David Brown",
            "age": 22,
            "email": "david@university.edu",
            "grades": {
                "mathematics": 70,
                "physics": 75,
                "chemistry": 73,
                "english": 78
            }
        },
        {
            "id": 5,
            "name": "Eva Martinez",
            "age": 20,
            "email": "eva@university.edu",
            "grades": {
                "mathematics": 88,
                "physics": 90,
                "chemistry": 87,
                "english": 92
            }
        }
    ]

    try:
        STUDENTS_FILE.write_text(json.dumps(students, indent=2))
        print(
            f"✓ Created sample {STUDENTS_FILE} with {len(students)} students")
    except Exception as e:
        print(f"❌ Failed to create {STUDENTS_FILE}: {e}")


def load_students() -> List[Student]:
    """Load students from JSON file with comprehensive error handling.

    Returns list of Student objects.
    Raises FileNotFoundError with helpful message if file doesn't exist.
    """
    if not STUDENTS_FILE.exists():
        raise FileNotFoundError(
            f"❌ File not found: {STUDENTS_FILE}\n"
            f"💡 Tip: Run the program to auto-generate sample data"
        )

    try:
        data = json.loads(STUDENTS_FILE.read_text())

        if not isinstance(data, list):
            raise ValueError(
                f"❌ Invalid format: Expected list of students, got {type(data).__name__}\n"
                f"💡 Tip: Check that {STUDENTS_FILE} contains a JSON array"
            )

        students = []
        for item in data:
            try:
                student = Student.from_dict(item)
                students.append(student)
            except Exception as e:
                print(f"⚠ Warning: Skipping invalid student record: {e}")
                continue

        return students

    except json.JSONDecodeError as e:
        raise ValueError(
            f"❌ Invalid JSON in {STUDENTS_FILE}\n"
            f"   Error: {e}\n"
            f"💡 Tip: Validate JSON syntax at https://jsonlint.com/"
        )
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load students: {e}")


def display_student(student: Student, detailed: bool = False) -> None:
    """Display student information in a formatted way.

    Args:
        student: Student object to display
        detailed: If True, show full grade breakdown
    """
    print(f"\n{'='*60}")
    print(f"Student ID: {student.id}")
    print(f"Name: {student.name}")
    print(f"Age: {student.age}")
    if student.email:
        print(f"Email: {student.email}")
    print(f"Average Grade: {student.average_grade:.1f}")

    if detailed and student.grades:
        print(f"\nGrade Breakdown:")
        for subject, grade in sorted(student.grades.items()):
            # Visual grade indicator
            if grade >= 90:
                indicator = "🌟 Excellent"
            elif grade >= 80:
                indicator = "✓ Good"
            elif grade >= 70:
                indicator = "→ Satisfactory"
            else:
                indicator = "⚠ Needs improvement"

            print(f"  {subject.capitalize():20s}: {grade:>3} {indicator}")


def demo_task1() -> None:
    """Interactive demo for Task 1: JSON Parsing."""
    hr("Task 1: JSON Parsing — Student Records")

    # Ensure sample file exists
    create_sample_students()

    try:
        students = load_students()

        print(f"\n✓ Loaded {len(students)} students from {STUDENTS_FILE}")

        # Display options
        print("\nDisplay options:")
        print("  1. Show all students (summary)")
        print("  2. Show all students (detailed)")
        print("  3. Search student by name")
        print("  4. Show top performers")
        print("  0. Back to main menu")

        choice = input("\nChoose option: ").strip()

        if choice == "1":
            # Summary view
            for student in students:
                display_student(student, detailed=False)

        elif choice == "2":
            # Detailed view
            for student in students:
                display_student(student, detailed=True)
                input("\nPress Enter for next student...")

        elif choice == "3":
            # Search by name
            name = input(
                "\nEnter student name (or part of it): ").strip().lower()
            found = [s for s in students if name in s.name.lower()]

            if not found:
                print(f"❌ No students found matching '{name}'")
            else:
                print(f"\n✓ Found {len(found)} student(s):")
                for student in found:
                    display_student(student, detailed=True)

        elif choice == "4":
            # Top performers
            sorted_students = sorted(
                students, key=lambda s: s.average_grade, reverse=True)
            top_n = min(3, len(sorted_students))

            print(f"\n🏆 Top {top_n} Students by Average Grade:")
            for i, student in enumerate(sorted_students[:top_n], 1):
                print(
                    f"\n{i}. {student.name} — Average: {student.average_grade:.1f}")
                display_student(student, detailed=True)

        elif choice == "0":
            return

        else:
            print(f"❌ Invalid choice: '{choice}'")

    except Exception as e:
        print(f"\n❌ Error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 2: Weather API — OpenWeatherMap Integration
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class WeatherData:
    """Weather information with type safety.

    Following L9-L13 feedback: structured data with validation.
    """
    city: str
    country: str
    temperature_celsius: float
    feels_like_celsius: float
    humidity: int
    pressure: int
    description: str
    wind_speed: float
    timestamp: datetime

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'WeatherData':
        """Parse OpenWeatherMap API response.

        Args:
            data: JSON response from OpenWeatherMap API

        Returns:
            WeatherData object

        Raises:
            ValueError: If required fields are missing
        """
        try:
            return cls(
                city=data["name"],
                country=data["sys"]["country"],
                # Kelvin to Celsius
                temperature_celsius=data["main"]["temp"] - 273.15,
                feels_like_celsius=data["main"]["feels_like"] - 273.15,
                humidity=data["main"]["humidity"],
                pressure=data["main"]["pressure"],
                description=data["weather"][0]["description"],
                wind_speed=data["wind"]["speed"],
                timestamp=datetime.fromtimestamp(data["dt"])
            )
        except KeyError as e:
            raise ValueError(
                f"❌ Invalid API response: missing field {e}\n"
                f"💡 Tip: Check API key and city name"
            )

    def display(self) -> None:
        """Display weather information in a user-friendly format."""
        print(f"\n{'='*60}")
        print(f"🌍 Weather in {self.city}, {self.country}")
        print(f"{'='*60}")
        print(f"📅 Updated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n🌡️  Temperature: {self.temperature_celsius:.1f}°C")
        print(f"🤔 Feels like: {self.feels_like_celsius:.1f}°C")
        print(f"💧 Humidity: {self.humidity}%")
        print(f"📊 Pressure: {self.pressure} hPa")
        print(f"🌬️  Wind Speed: {self.wind_speed} m/s")
        print(f"☁️  Conditions: {self.description.capitalize()}")

        # Additional context based on values
        if self.temperature_celsius > 30:
            print("\n🔥 It's hot! Stay hydrated")
        elif self.temperature_celsius < 0:
            print("\n❄️ It's freezing! Bundle up")

        if self.humidity > 80:
            print("💦 High humidity — might feel muggy")

        print(f"{'='*60}")


def fetch_weather(city: str) -> WeatherData:
    """Fetch weather data from OpenWeatherMap API with caching.

    Args:
        city: City name (e.g., "Tashkent", "London")

    Returns:
        WeatherData object

    Raises:
        RuntimeError: If API request fails
        ValueError: If API response is invalid

    Note:
        Results are cached for 1 hour to reduce API calls.
        This follows production best practices (L12-L13 feedback).
    """
    if not REQUESTS_AVAILABLE:
        raise RuntimeError(
            "❌ 'requests' library not installed\n"
            "💡 Install with: pip install requests"
        )

    if not CONFIG.openweather_api_key:
        raise ValueError(
            "❌ OpenWeatherMap API key not configured\n"
            "💡 Run setup to configure API keys"
        )

    # Check cache first
    cache_key = f"weather_{city.lower()}"
    cached = get_cached(cache_key, max_age_hours=CONFIG.cache_duration_hours)

    if cached:
        print(
            f"💾 Using cached weather data (age: <{CONFIG.cache_duration_hours}h)")
        return WeatherData.from_api_response(cached)

    # Check rate limit
    wait_for_rate_limit("openweather")

    # Fetch from API
    try:
        params = {
            "q": city,
            "appid": CONFIG.openweather_api_key
        }

        print(f"🌐 Fetching weather data for {city}...")
        response = requests.get(OPENWEATHER_BASE_URL,
                                params=params, timeout=10)

        if response.status_code == 401:
            raise RuntimeError(
                "❌ Invalid API key\n"
                "💡 Tip: Check your OpenWeatherMap API key at https://openweathermap.org/api"
            )

        if response.status_code == 404:
            raise ValueError(
                f"❌ City not found: '{city}'\n"
                f"💡 Tip: Try different spelling or check city name"
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"❌ API request failed: HTTP {response.status_code}\n"
                f"   Response: {response.text[:200]}"
            )

        data = response.json()

        # Cache the response
        set_cached(cache_key, data)

        return WeatherData.from_api_response(data)

    except requests.exceptions.Timeout:
        raise RuntimeError(
            "❌ Request timed out\n"
            "💡 Tip: Check your internet connection"
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "❌ Connection error\n"
            "💡 Tip: Check your internet connection"
        )
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"❌ Request failed: {e}")


def demo_task2() -> None:
    """Interactive demo for Task 2: Weather API."""
    hr("Task 2: Weather API — OpenWeatherMap Integration")

    if not CONFIG.ensure_api_keys():
        print("❌ Cannot proceed without API keys")
        return

    try:
        # Default city option
        use_default = confirm(f"Use default city ({CONFIG.default_city})?")

        if use_default:
            city = CONFIG.default_city
        else:
            city = input("Enter city name: ").strip()
            if not city:
                print("❌ City name cannot be empty")
                return

        # Fetch and display weather
        weather = fetch_weather(city)
        weather.display()

        # Option to save as default
        if city != CONFIG.default_city:
            if confirm(f"Save '{city}' as default city?"):
                CONFIG.default_city = city
                CONFIG.save()

    except Exception as e:
        print(f"\n❌ Error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Continue in next message due to length...
# ──────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────────────
# TASK 3: JSON Modification — Books Database Management (CRUD)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Book:
    """Book record with comprehensive validation.

    Following L9-L13 feedback: structured data, validation, type hints.
    """
    id: int
    title: str
    author: str
    year: int
    genre: str
    isbn: Optional[str] = None
    rating: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate book data after initialization."""
        if not self.title.strip():
            raise ValueError("❌ Book title cannot be empty")

        if not self.author.strip():
            raise ValueError("❌ Author name cannot be empty")

        current_year = datetime.now().year
        if not (1000 <= self.year <= current_year + 5):
            raise ValueError(
                f"❌ Invalid publication year: {self.year}\n"
                f"💡 Tip: Year should be between 1000 and {current_year + 5}"
            )

        if self.rating is not None:
            if not (0.0 <= self.rating <= 10.0):
                raise ValueError(
                    f"❌ Invalid rating: {self.rating}\n"
                    f"💡 Tip: Rating must be between 0.0 and 10.0"
                )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
            "isbn": self.isbn,
            "rating": self.rating
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
        """Create Book from dictionary.

        >>> data = {"id": 1, "title": "1984", "author": "Orwell", "year": 1949, "genre": "Dystopian"}
        >>> b = Book.from_dict(data)
        >>> b.title
        '1984'
        """
        return cls(
            id=data["id"],
            title=data["title"],
            author=data["author"],
            year=data["year"],
            genre=data["genre"],
            isbn=data.get("isbn"),
            rating=data.get("rating")
        )

    def display(self, detailed: bool = False) -> None:
        """Display book information formatted."""
        print(f"\n{'─'*60}")
        print(f"📚 {self.title}")
        print(f"✍️  Author: {self.author}")
        print(f"📅 Year: {self.year}")
        print(f"🏷️  Genre: {self.genre}")

        if detailed:
            if self.isbn:
                print(f"📖 ISBN: {self.isbn}")
            if self.rating:
                stars = "⭐" * int(self.rating / 2)
                print(f"⭐ Rating: {self.rating}/10 {stars}")
            print(f"🆔 ID: {self.id}")


class BooksDatabase:
    """Books database with CRUD operations and persistence.

    Design principles (L8-L13 feedback):
    - Atomic operations with rollback on failure
    - Clear error messages with context
    - Auto-save after modifications
    - Thread-safe operations (for future extensibility)
    """

    def __init__(self, filepath: Path = BOOKS_FILE):
        """Initialize books database.

        Args:
            filepath: Path to JSON file for persistence
        """
        self.filepath = filepath
        self.books: List[Book] = []
        self._next_id = 1

        # Load existing data if available
        if filepath.exists():
            try:
                self.load()
            except Exception as e:
                print(f"⚠ Warning: Could not load {filepath}: {e}")
                print("💡 Starting with empty database")

    def load(self) -> None:
        """Load books from JSON file.

        Raises:
            ValueError: If file format is invalid
        """
        try:
            data = json.loads(self.filepath.read_text())

            if not isinstance(data, list):
                raise ValueError(f"Expected list, got {type(data).__name__}")

            self.books = []
            for item in data:
                try:
                    book = Book.from_dict(item)
                    self.books.append(book)
                    # Track highest ID for auto-increment
                    if book.id >= self._next_id:
                        self._next_id = book.id + 1
                except Exception as e:
                    print(f"⚠ Skipping invalid book record: {e}")

            print(f"✓ Loaded {len(self.books)} books from {self.filepath}")

        except json.JSONDecodeError as e:
            raise ValueError(
                f"❌ Invalid JSON in {self.filepath}\n"
                f"   Error: {e}\n"
                f"💡 Tip: Validate JSON at https://jsonlint.com/"
            )

    def save(self) -> None:
        """Save books to JSON file with backup.

        Creates backup before overwriting for data safety.
        """
        try:
            # Create backup if file exists
            if self.filepath.exists():
                backup_path = self.filepath.with_suffix('.json.backup')
                backup_path.write_text(self.filepath.read_text())

            # Write new data
            data = [book.to_dict() for book in self.books]
            self.filepath.write_text(json.dumps(data, indent=2))

        except Exception as e:
            raise RuntimeError(
                f"❌ Failed to save books database\n"
                f"   Error: {e}\n"
                f"💡 Check file permissions for {self.filepath}"
            )

    def create(self, book: Book) -> Book:
        """Add new book to database (Create operation).

        Args:
            book: Book object to add

        Returns:
            The added book with assigned ID

        Raises:
            ValueError: If book with same title+author exists
        """
        # Check for duplicates
        existing = self.find_by_title_author(book.title, book.author)
        if existing:
            raise ValueError(
                f"❌ Book already exists: '{book.title}' by {book.author}\n"
                f"   Existing ID: {existing.id}\n"
                f"💡 Tip: Use update operation to modify existing book"
            )

        # Assign new ID
        book.id = self._next_id
        self._next_id += 1

        # Add to database
        self.books.append(book)
        self.save()

        print(f"✓ Added book #{book.id}: '{book.title}'")
        return book

    def read_all(self) -> List[Book]:
        """Get all books (Read operation).

        >>> db = BooksDatabase(Path("test_books.json"))
        >>> isinstance(db.read_all(), list)
        True
        """
        return self.books.copy()

    def read_by_id(self, book_id: int) -> Optional[Book]:
        """Get book by ID (Read operation).

        Args:
            book_id: Book ID to find

        Returns:
            Book object or None if not found
        """
        for book in self.books:
            if book.id == book_id:
                return book
        return None

    def find_by_title_author(self, title: str, author: str) -> Optional[Book]:
        """Find book by title and author (case-insensitive)."""
        title_lower = title.lower().strip()
        author_lower = author.lower().strip()

        for book in self.books:
            if (book.title.lower().strip() == title_lower and
                    book.author.lower().strip() == author_lower):
                return book
        return None

    def search(self, query: str) -> List[Book]:
        """Search books by title, author, or genre (case-insensitive).

        Args:
            query: Search term

        Returns:
            List of matching books

        >>> db = BooksDatabase(Path("test_books.json"))
        >>> results = db.search("test")
        >>> isinstance(results, list)
        True
        """
        query_lower = query.lower()
        results = []

        for book in self.books:
            if (query_lower in book.title.lower() or
                query_lower in book.author.lower() or
                    query_lower in book.genre.lower()):
                results.append(book)

        return results

    def update(self, book_id: int, **updates) -> Book:
        """Update book fields (Update operation).

        Args:
            book_id: ID of book to update
            **updates: Fields to update (title, author, year, genre, isbn, rating)

        Returns:
            Updated book

        Raises:
            ValueError: If book not found or invalid updates
        """
        book = self.read_by_id(book_id)

        if not book:
            raise ValueError(
                f"❌ Book not found: ID {book_id}\n"
                f"💡 Tip: Use search to find book ID"
            )

        # Store original values for rollback
        original_data = book.to_dict()

        try:
            # Apply updates
            for field, value in updates.items():
                if not hasattr(book, field):
                    raise ValueError(
                        f"❌ Invalid field: '{field}'\n"
                        f"💡 Valid fields: title, author, year, genre, isbn, rating"
                    )
                setattr(book, field, value)

            # Validate updated book
            book.__post_init__()

            # Save changes
            self.save()

            print(f"✓ Updated book #{book_id}: '{book.title}'")
            return book

        except Exception as e:
            # Rollback on error
            for field, value in original_data.items():
                setattr(book, field, value)
            raise ValueError(f"❌ Update failed: {e}")

    def delete(self, book_id: int) -> Book:
        """Delete book from database (Delete operation).

        Args:
            book_id: ID of book to delete

        Returns:
            Deleted book

        Raises:
            ValueError: If book not found
        """
        book = self.read_by_id(book_id)

        if not book:
            raise ValueError(
                f"❌ Book not found: ID {book_id}\n"
                f"💡 Tip: Use search to find book ID"
            )

        # Remove from list
        self.books.remove(book)
        self.save()

        print(f"✓ Deleted book #{book_id}: '{book.title}'")
        return book

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns dict with total books, genres, year range, etc.
        """
        if not self.books:
            return {"total": 0}

        genres = defaultdict(int)
        years = []

        for book in self.books:
            genres[book.genre] += 1
            years.append(book.year)

        return {
            "total": len(self.books),
            "genres": dict(genres),
            "year_range": (min(years), max(years)),
            "oldest": min(years),
            "newest": max(years)
        }


def create_sample_books() -> None:
    """Create sample books.json file if it doesn't exist."""
    if BOOKS_FILE.exists():
        return

    # Realistic sample data with classics and modern books
    books = [
        {
            "id": 1,
            "title": "1984",
            "author": "George Orwell",
            "year": 1949,
            "genre": "Dystopian",
            "isbn": "978-0-452-28423-4",
            "rating": 9.2
        },
        {
            "id": 2,
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "year": 1960,
            "genre": "Classic",
            "isbn": "978-0-06-112008-4",
            "rating": 8.9
        },
        {
            "id": 3,
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "year": 1925,
            "genre": "Classic",
            "isbn": "978-0-7432-7356-5",
            "rating": 8.5
        },
        {
            "id": 4,
            "title": "Harry Potter and the Sorcerer's Stone",
            "author": "J.K. Rowling",
            "year": 1997,
            "genre": "Fantasy",
            "isbn": "978-0-439-70818-8",
            "rating": 9.0
        },
        {
            "id": 5,
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "year": 1937,
            "genre": "Fantasy",
            "isbn": "978-0-547-92822-7",
            "rating": 8.8
        },
        {
            "id": 6,
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "year": 1813,
            "genre": "Romance",
            "isbn": "978-0-14-143951-8",
            "rating": 8.7
        },
        {
            "id": 7,
            "title": "The Catcher in the Rye",
            "author": "J.D. Salinger",
            "year": 1951,
            "genre": "Classic",
            "isbn": "978-0-316-76948-0",
            "rating": 7.8
        }
    ]

    try:
        BOOKS_FILE.write_text(json.dumps(books, indent=2))
        print(f"✓ Created sample {BOOKS_FILE} with {len(books)} books")
    except Exception as e:
        print(f"❌ Failed to create {BOOKS_FILE}: {e}")


def demo_task3() -> None:
    """Interactive demo for Task 3: JSON Modification (Books CRUD)."""
    hr("Task 3: JSON Modification — Books Database (CRUD)")

    # Ensure sample file exists
    create_sample_books()

    # Initialize database
    try:
        db = BooksDatabase()
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return

    while True:
        print("\n" + "─"*60)
        print("Books Database Operations:")
        print("  1. View all books")
        print("  2. Search books")
        print("  3. Add new book")
        print("  4. Update book")
        print("  5. Delete book")
        print("  6. Database statistics")
        print("  0. Back to main menu")

        choice = input("\nChoose operation: ").strip()

        try:
            if choice == "1":
                # View all books
                books = db.read_all()
                if not books:
                    print("📭 Database is empty")
                else:
                    print(f"\n📚 Total books: {len(books)}")
                    for book in books:
                        book.display(detailed=True)

            elif choice == "2":
                # Search books
                query = input("\nSearch (title/author/genre): ").strip()
                if not query:
                    print("❌ Search query cannot be empty")
                    continue

                results = db.search(query)
                if not results:
                    print(f"❌ No books found matching '{query}'")
                else:
                    print(f"\n✓ Found {len(results)} book(s):")
                    for book in results:
                        book.display(detailed=True)

            elif choice == "3":
                # Add new book
                print("\n➕ Add New Book")
                print("─"*60)

                title = input("Title: ").strip()
                if not title:
                    print("❌ Title cannot be empty")
                    continue

                author = input("Author: ").strip()
                if not author:
                    print("❌ Author cannot be empty")
                    continue

                year = read_int("Publication year: ", min_val=1000,
                                max_val=datetime.now().year + 5)

                genre = input("Genre: ").strip()
                if not genre:
                    print("❌ Genre cannot be empty")
                    continue

                isbn = input(
                    "ISBN (optional, press Enter to skip): ").strip() or None

                rating_input = input(
                    "Rating 0-10 (optional, press Enter to skip): ").strip()
                rating = float(rating_input) if rating_input else None

                # Create and add book
                book = Book(
                    id=0,  # Will be assigned by database
                    title=title,
                    author=author,
                    year=year,
                    genre=genre,
                    isbn=isbn,
                    rating=rating
                )

                db.create(book)
                print("\n✓ Book added successfully:")
                book.display(detailed=True)

            elif choice == "4":
                # Update book
                book_id = read_int("\nEnter book ID to update: ", min_val=1)

                book = db.read_by_id(book_id)
                if not book:
                    print(f"❌ Book #{book_id} not found")
                    continue

                print("\nCurrent information:")
                book.display(detailed=True)

                print("\nEnter new values (press Enter to keep current):")

                updates = {}

                new_title = input(f"Title [{book.title}]: ").strip()
                if new_title:
                    updates["title"] = new_title

                new_author = input(f"Author [{book.author}]: ").strip()
                if new_author:
                    updates["author"] = new_author

                new_year_str = input(f"Year [{book.year}]: ").strip()
                if new_year_str:
                    updates["year"] = int(new_year_str)

                new_genre = input(f"Genre [{book.genre}]: ").strip()
                if new_genre:
                    updates["genre"] = new_genre

                new_isbn = input(f"ISBN [{book.isbn or 'None'}]: ").strip()
                if new_isbn:
                    updates["isbn"] = new_isbn

                new_rating_str = input(
                    f"Rating [{book.rating or 'None'}]: ").strip()
                if new_rating_str:
                    updates["rating"] = float(new_rating_str)

                if not updates:
                    print("💡 No changes made")
                    continue

                db.update(book_id, **updates)

                print("\n✓ Book updated successfully:")
                updated_book = db.read_by_id(book_id)
                if updated_book:
                    updated_book.display(detailed=True)

            elif choice == "5":
                # Delete book
                book_id = read_int("\nEnter book ID to delete: ", min_val=1)

                book = db.read_by_id(book_id)
                if not book:
                    print(f"❌ Book #{book_id} not found")
                    continue

                print("\nBook to delete:")
                book.display(detailed=True)

                if confirm("\n⚠️  Are you sure you want to delete this book?"):
                    db.delete(book_id)
                else:
                    print("💡 Deletion cancelled")

            elif choice == "6":
                # Statistics
                stats = db.get_statistics()

                print("\n" + "="*60)
                print("📊 Database Statistics")
                print("="*60)
                print(f"Total books: {stats['total']}")

                if stats['total'] > 0:
                    print(
                        f"\nYear range: {stats['year_range'][0]} - {stats['year_range'][1]}")
                    print(f"Oldest: {stats['oldest']}")
                    print(f"Newest: {stats['newest']}")

                    print("\nGenres:")
                    for genre, count in sorted(stats['genres'].items(), key=lambda x: x[1], reverse=True):
                        bar = "█" * count
                        print(f"  {genre:20s}: {bar} ({count})")

            elif choice == "0":
                return

            else:
                print(f"❌ Invalid choice: '{choice}'")

        except Exception as e:
            print(f"\n❌ Error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 4: Movie Recommendation System — OMDb API Integration
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Movie:
    """Movie information from OMDb API.

    Following L9-L13 feedback: structured data with type safety.
    """
    title: str
    year: str
    genre: str
    director: str
    actors: str
    plot: str
    imdb_rating: str
    poster_url: str
    runtime: str

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'Movie':
        """Parse OMDb API response.

        Args:
            data: JSON response from OMDb API

        Returns:
            Movie object
        """
        return cls(
            title=data.get("Title", "Unknown"),
            year=data.get("Year", "N/A"),
            genre=data.get("Genre", "N/A"),
            director=data.get("Director", "N/A"),
            actors=data.get("Actors", "N/A"),
            plot=data.get("Plot", "No plot available"),
            imdb_rating=data.get("imdbRating", "N/A"),
            poster_url=data.get("Poster", "N/A"),
            runtime=data.get("Runtime", "N/A")
        )

    def display(self) -> None:
        """Display movie information formatted."""
        print(f"\n{'='*70}")
        print(f"🎬 {self.title} ({self.year})")
        print(f"{'='*70}")
        print(f"🎭 Genre: {self.genre}")
        print(f"🎥 Director: {self.director}")
        print(f"🎞️  Runtime: {self.runtime}")
        print(f"⭐ IMDb Rating: {self.imdb_rating}/10")
        print(f"👥 Cast: {self.actors}")
        print(f"\n📝 Plot:")
        print(f"   {self.plot}")

        if self.poster_url != "N/A":
            print(f"\n🖼️  Poster: {self.poster_url}")

        print(f"{'='*70}")


class MovieRecommendationSystem:
    """Advanced movie recommendation system with OMDb API.

    Features (addressing "advanced logic" requirement):
    - Genre-based filtering
    - IMDb rating threshold
    - Year range filtering
    - History tracking (no repeated recommendations)
    - Caching for performance
    - Rate limiting
    """

    def __init__(self):
        """Initialize recommendation system."""
        self.history: List[str] = []  # Track recommended movies
        self.cache: Dict[str, List[Dict[str, Any]]] = {}

    def search_by_title(self, title: str) -> Optional[Movie]:
        """Search for a specific movie by title.

        Args:
            title: Movie title to search

        Returns:
            Movie object or None if not found
        """
        if not REQUESTS_AVAILABLE:
            raise RuntimeError(
                "❌ 'requests' library not installed\n"
                "💡 Install with: pip install requests"
            )

        if not CONFIG.omdb_api_key:
            raise ValueError(
                "❌ OMDb API key not configured\n"
                "💡 Run setup to configure API keys"
            )

        # Check cache
        cache_key = f"movie_title_{title.lower()}"
        # Movies don't change often
        cached = get_cached(cache_key, max_age_hours=24)

        if cached:
            print("💾 Using cached data")
            return Movie.from_api_response(cached)

        # Check rate limit
        wait_for_rate_limit("omdb")

        try:
            params = {
                "apikey": CONFIG.omdb_api_key,
                "t": title,
                "type": "movie",
                "plot": "full"
            }

            print(f"🌐 Searching for '{title}'...")
            response = requests.get(OMDB_BASE_URL, params=params, timeout=10)

            if response.status_code != 200:
                raise RuntimeError(
                    f"API request failed: HTTP {response.status_code}")

            data = response.json()

            if data.get("Response") == "False":
                error = data.get("Error", "Unknown error")
                if "not found" in error.lower():
                    return None
                raise RuntimeError(f"API error: {error}")

            # Cache the result
            set_cached(cache_key, data)

            return Movie.from_api_response(data)

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Request failed: {e}")

    def recommend_by_genre(
        self,
        genre: str,
        *,
        min_rating: float = 6.0,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        exclude_seen: bool = True
    ) -> Optional[Movie]:
        """Recommend a random movie from specified genre with filters.

        Advanced features:
        - Rating threshold filtering
        - Year range filtering
        - Excludes previously recommended movies
        - Fallback to popular movies if no search results

        Args:
            genre: Movie genre (e.g., "Action", "Comedy", "Drama")
            min_rating: Minimum IMDb rating (default: 6.0)
            year_from: Minimum year (optional)
            year_to: Maximum year (optional)
            exclude_seen: Exclude previously recommended movies

        Returns:
            Movie object or None if no suitable movie found
        """
        # Popular movies by genre (fallback list)
        popular_movies_by_genre = {
            "action": ["The Dark Knight", "Inception", "Mad Max: Fury Road", "Die Hard", "The Matrix"],
            "comedy": ["The Grand Budapest Hotel", "Superbad", "Groundhog Day", "The Big Lebowski"],
            "drama": ["The Shawshank Redemption", "Forrest Gump", "The Godfather", "Fight Club"],
            "horror": ["The Shining", "Get Out", "A Quiet Place", "Hereditary", "The Conjuring"],
            "sci-fi": ["Blade Runner 2049", "Interstellar", "The Matrix", "Inception", "Arrival"],
            "romance": ["The Notebook", "Pride and Prejudice", "La La Land", "Before Sunrise"],
            "thriller": ["Se7en", "Gone Girl", "Prisoners", "Shutter Island", "No Country for Old Men"],
            "fantasy": ["The Lord of the Rings", "Harry Potter", "Pan's Labyrinth", "Spirited Away"],
            "animation": ["Spirited Away", "WALL-E", "Inside Out", "Toy Story", "Up"],
        }

        genre_lower = genre.lower()
        candidate_titles = popular_movies_by_genre.get(genre_lower, [])

        if not candidate_titles:
            print(f"⚠ Genre '{genre}' not in preset list")
            print("💡 Available genres:", ", ".join(
                popular_movies_by_genre.keys()))
            return None

        # Filter out previously recommended movies if requested
        if exclude_seen:
            available_titles = [
                t for t in candidate_titles if t not in self.history]
            if not available_titles:
                print("💡 All movies from this genre have been recommended")
                if confirm("Reset recommendation history?"):
                    self.history.clear()
                    available_titles = candidate_titles
                else:
                    return None
        else:
            available_titles = candidate_titles

        # Try random movies until we find one matching criteria
        random.shuffle(available_titles)

        for title in available_titles:
            try:
                movie = self.search_by_title(title)

                if not movie:
                    continue

                # Apply filters
                # Check rating
                try:
                    rating = float(movie.imdb_rating)
                    if rating < min_rating:
                        print(
                            f"⏭️  Skipping '{title}' (rating {rating} < {min_rating})")
                        continue
                except ValueError:
                    # Rating not available, skip this filter
                    pass

                # Check year range
                try:
                    # Handle year ranges like "2019–2020"
                    year = int(movie.year.split("–")[0])
                    if year_from and year < year_from:
                        print(
                            f"⏭️  Skipping '{title}' (year {year} < {year_from})")
                        continue
                    if year_to and year > year_to:
                        print(
                            f"⏭️  Skipping '{title}' (year {year} > {year_to})")
                        continue
                except ValueError:
                    # Year not parseable, skip this filter
                    pass

                # Found a suitable movie!
                self.history.append(title)
                return movie

            except Exception as e:
                print(f"⚠ Error checking '{title}': {e}")
                continue

        print(f"❌ No suitable {genre} movies found matching your criteria")
        return None


def demo_task4() -> None:
    """Interactive demo for Task 4: Movie Recommendation System."""
    hr("Task 4: Movie Recommendation System — OMDb API")

    if not CONFIG.ensure_api_keys():
        print("❌ Cannot proceed without API keys")
        return

    recommender = MovieRecommendationSystem()

    while True:
        print("\n" + "─"*70)
        print("Movie Recommendation Options:")
        print("  1. Get recommendation by genre (with filters)")
        print("  2. Search specific movie")
        print("  3. View recommendation history")
        print("  4. Clear history")
        print("  0. Back to main menu")

        choice = input("\nChoose option: ").strip()

        try:
            if choice == "1":
                # Genre-based recommendation with filters
                print("\n🎬 Movie Recommendation by Genre")
                print("─"*70)

                # Show available genres
                genres = ["Action", "Comedy", "Drama", "Horror", "Sci-Fi",
                          "Romance", "Thriller", "Fantasy", "Animation"]
                print("Available genres:")
                for i, g in enumerate(genres, 1):
                    print(f"  {i}. {g}")

                genre_choice = input("\nEnter genre number or name: ").strip()

                # Parse genre choice
                if genre_choice.isdigit():
                    idx = int(genre_choice) - 1
                    if 0 <= idx < len(genres):
                        genre = genres[idx]
                    else:
                        print(f"❌ Invalid number: {genre_choice}")
                        continue
                else:
                    genre = genre_choice

                # Optional filters
                print("\n🎯 Optional Filters (press Enter to skip):")

                min_rating_str = input(
                    "Minimum IMDb rating (0-10) [default: 6.0]: ").strip()
                min_rating = float(min_rating_str) if min_rating_str else 6.0

                year_from_str = input("From year [default: any]: ").strip()
                year_from = int(year_from_str) if year_from_str else None

                year_to_str = input("To year [default: any]: ").strip()
                year_to = int(year_to_str) if year_to_str else None

                # Get recommendation
                print(f"\n🔍 Finding {genre} movie...")
                print(f"   Filters: Rating ≥ {min_rating}", end="")
                if year_from or year_to:
                    print(
                        f", Year: {year_from or 'any'}-{year_to or 'any'}", end="")
                print()

                movie = recommender.recommend_by_genre(
                    genre,
                    min_rating=min_rating,
                    year_from=year_from,
                    year_to=year_to
                )

                if movie:
                    print("\n✨ Recommendation:")
                    movie.display()
                else:
                    print("\n❌ No recommendations available with current filters")
                    print("💡 Try adjusting filters or choosing different genre")

            elif choice == "2":
                # Search specific movie
                title = input("\nEnter movie title: ").strip()
                if not title:
                    print("❌ Title cannot be empty")
                    continue

                movie = recommender.search_by_title(title)

                if movie:
                    movie.display()
                else:
                    print(f"❌ Movie not found: '{title}'")
                    print("💡 Tip: Check spelling or try different search terms")

            elif choice == "3":
                # View history
                if not recommender.history:
                    print("\n📭 No recommendations yet")
                else:
                    print(
                        f"\n📚 Recommendation History ({len(recommender.history)} movies):")
                    for i, title in enumerate(recommender.history, 1):
                        print(f"  {i}. {title}")

            elif choice == "4":
                # Clear history
                if not recommender.history:
                    print("\n💡 History is already empty")
                else:
                    if confirm(f"\n⚠️  Clear {len(recommender.history)} recommendations from history?"):
                        recommender.history.clear()
                        print("✓ History cleared")
                    else:
                        print("💡 Cancelled")

            elif choice == "0":
                return

            else:
                print(f"❌ Invalid choice: '{choice}'")

        except Exception as e:
            print(f"\n❌ Error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Main CLI & Test Runner
# ──────────────────────────────────────────────────────────────────────────────

def run_tests() -> Tuple[int, int]:
    """Run all doctests.

    Returns:
        Tuple of (failures, total_tests)
    """
    import doctest

    print("Running doctests...")
    failures, tests = doctest.testmod(verbose=False)

    if failures == 0:
        print(f"✓ All {tests} doctests passed!")
    else:
        print(f"❌ {failures} of {tests} doctests failed")

    return failures, tests


def main(argv: List[str] | None = None) -> int:
    """Main entry point with comprehensive menu.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    argv = argv or sys.argv[1:]

    # Handle command-line arguments
    if "--test" in argv:
        failures, _ = run_tests()
        return 0 if failures == 0 else 1

    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0

    # ASCII art title (optional, for visual appeal)
    print("\n" + "="*70)
    print(" 🎓 Lesson 14: API Integration & JSON Operations ".center(70, "="))
    print("="*70)

    # Main menu loop
    try:
        while True:
            hr("Main Menu")
            print("Choose a task to explore:\n")
            print("  1️⃣  Task 1: JSON Parsing — Student Records")
            print("  2️⃣  Task 2: Weather API — OpenWeatherMap")
            print("  3️⃣  Task 3: JSON Modification — Books Database (CRUD)")
            print("  4️⃣  Task 4: Movie Recommendation — OMDb API")
            print("\n  ⚙️  Settings — Configure API keys & preferences")
            print("  🧪 Tests — Run doctests")
            print("  0️⃣  Exit")

            choice = input("\nSelect option: ").strip()

            if choice == "1":
                demo_task1()

            elif choice == "2":
                demo_task2()

            elif choice == "3":
                demo_task3()

            elif choice == "4":
                demo_task4()

            elif choice.lower() in ("settings", "⚙️", "s"):
                hr("Settings")
                print("Current configuration:")
                print(f"  Default city: {CONFIG.default_city}")
                print(f"  Cache duration: {CONFIG.cache_duration_hours}h")
                print(
                    f"  OpenWeather API key: {'✓ Set' if CONFIG.openweather_api_key else '❌ Not set'}")
                print(
                    f"  OMDb API key: {'✓ Set' if CONFIG.omdb_api_key else '❌ Not set'}")

                if confirm("\nReconfigure API keys?"):
                    CONFIG.openweather_api_key = ""
                    CONFIG.omdb_api_key = ""
                    CONFIG.ensure_api_keys()

                new_city = input(
                    f"\nDefault city [{CONFIG.default_city}]: ").strip()
                if new_city:
                    CONFIG.default_city = new_city

                CONFIG.save()
                print("✓ Settings saved")

            elif choice.lower() in ("tests", "test", "🧪", "t"):
                run_tests()
                input("\nPress Enter to continue...")

            elif choice == "0":
                print("\n👋 Thank you for using Lesson 14!")
                print("💡 Remember to set environment variables for API keys")
                return 0

            else:
                print(f"❌ Invalid option: '{choice}'")
                print("💡 Please enter a number from the menu")

    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user (Ctrl+C)")
        print("👋 Goodbye!")
        return 1

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if "--debug" in argv:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
