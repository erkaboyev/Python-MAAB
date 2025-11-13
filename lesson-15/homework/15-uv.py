#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lesson15.py — SQLite Database Operations (Lesson 15)

This module implements comprehensive SQLite database operations with:
- Educational error handling (following L8-L13 feedback)
- Type-safe database interactions with dataclasses
- Transaction management with rollback
- SQL injection prevention using parameterized queries
- Interactive CLI with CRUD operations
- Comprehensive testing with doctests

Tasks:
    1. Create database with Roster table (Name, Species, Age)
    2. Populate table with initial data
    3. Update Jadzia Dax → Ezri Dax
    4. Query and display Bajoran species

Database Schema:
    Roster Table:
        - Name (TEXT, NOT NULL)
        - Species (TEXT, NOT NULL)
        - Age (INTEGER, NOT NULL)
        - id (INTEGER PRIMARY KEY AUTOINCREMENT) — added for best practices

Design Principles (from L1-L14 feedback):
    - Path objects for file handling (L11)
    - Specific exceptions with educational messages (L8, L11, L13)
    - Dataclasses for structured data (L9, L13, L14)
    - Comprehensive validation (L9-L14)
    - Inline comments for complex logic (L13)
    - Production best practices (backups, transactions, etc.)

Run tests:
    python lesson15.py --test

Interactive CLI:
    python lesson15.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import doctest
import sqlite3
import sys

# ──────────────────────────────────────────────────────────────────────────────
# Configuration & Constants
# ──────────────────────────────────────────────────────────────────────────────

DATABASE_FILE = Path("roster.db")
BACKUP_DIR = Path("backups")


# ──────────────────────────────────────────────────────────────────────────────
# Utility Functions: Pretty printing, input validation
# ──────────────────────────────────────────────────────────────────────────────

def hr(title: str = "", width: int = 70) -> None:
    """Print horizontal rule with optional title.

    Following L1-L14 feedback: consistent utility functions.

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
    """Read integer with validation loop and educational error messages.

    Following L8-L13 feedback: emoji, context, specific error messages.
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


def confirm(prompt: str = "Continue?") -> bool:
    """Ask for yes/no confirmation.

    >>> # Interactive function, not easily testable
    >>> isinstance(confirm.__doc__, str)
    True
    """
    response = input(f"{prompt} (y/n): ").strip().lower()
    return response in ('y', 'yes')


# ──────────────────────────────────────────────────────────────────────────────
# Data Models (using dataclasses for type safety)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class RosterMember:
    """Roster member with validation.

    Following L9-L14 feedback: dataclasses for structured data,
    validation in __post_init__, type hints.

    Attributes:
        name: Full name of the crew member
        species: Species classification
        age: Age in years
        id: Database ID (auto-assigned, None for new records)
    """
    name: str
    species: str
    age: int
    id: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate roster member data.

        Following L9-L13 feedback: comprehensive validation with
        educational error messages.
        """
        # Name validation
        if not self.name.strip():
            raise ValueError(
                "❌ Name cannot be empty\n"
                "💡 Tip: Enter a valid crew member name"
            )

        if len(self.name) > 100:
            raise ValueError(
                f"❌ Name too long: {len(self.name)} chars (max 100)\n"
                "💡 Tip: Use a shorter name or abbreviation"
            )

        # Species validation
        if not self.species.strip():
            raise ValueError(
                "❌ Species cannot be empty\n"
                "💡 Tip: Enter species (e.g., Human, Vulcan, Bajoran)"
            )

        if len(self.species) > 50:
            raise ValueError(
                f"❌ Species name too long: {len(self.species)} chars (max 50)"
            )

        # Age validation
        if not (0 <= self.age <= 1000):
            raise ValueError(
                f"❌ Invalid age: {self.age}\n"
                "💡 Tip: Age must be between 0 and 1000 years\n"
                "   (Some species like Trill live very long!)"
            )

    def to_tuple(self) -> Tuple[str, str, int]:
        """Convert to tuple for database insertion (without id).

        >>> member = RosterMember("Benjamin Sisko", "Human", 40)
        >>> member.to_tuple()
        ('Benjamin Sisko', 'Human', 40)
        """
        return (self.name, self.species, self.age)

    @classmethod
    def from_row(cls, row: Tuple) -> 'RosterMember':
        """Create RosterMember from database row.

        Expected row format: (id, name, species, age)

        >>> row = (1, "Jadzia Dax", "Trill", 300)
        >>> member = RosterMember.from_row(row)
        >>> member.name
        'Jadzia Dax'
        >>> member.id
        1
        """
        return cls(
            id=row[0],
            name=row[1],
            species=row[2],
            age=row[3]
        )

    def display(self, detailed: bool = False) -> None:
        """Display roster member information formatted.

        Args:
            detailed: If True, show additional metadata
        """
        print(f"\n{'─'*60}")
        print(f"👤 Name: {self.name}")
        print(f"🧬 Species: {self.species}")
        print(f"🎂 Age: {self.age} years")

        if detailed and self.id is not None:
            print(f"🆔 Database ID: {self.id}")

        # Add contextual emoji based on species
        species_emoji = {
            "human": "🧑",
            "vulcan": "🖖",
            "bajoran": "🙏",
            "trill": "🔄",
            "klingon": "⚔️",
            "romulan": "🏛️",
            "ferengi": "💰"
        }
        emoji = species_emoji.get(self.species.lower(), "👽")
        print(f"   {emoji} {self.species} crew member")


# ──────────────────────────────────────────────────────────────────────────────
# Database Manager (production-ready with transactions & error handling)
# ──────────────────────────────────────────────────────────────────────────────

class DatabaseError(Exception):
    """Base exception for database operations.

    Following L8 feedback: specific exception types for better error handling.
    """
    pass


class RosterDatabase:
    """SQLite database manager for Roster table.

    Design principles (from L11-L14 feedback):
    - Context manager for automatic connection handling
    - Transaction support with rollback on errors
    - Parameterized queries to prevent SQL injection
    - Backup functionality before destructive operations
    - Educational error messages
    - Path objects for file handling

    Example:
        >>> db = RosterDatabase(":memory:")
        >>> db.create_table()
        >>> member = RosterMember("Test", "Human", 30)
        >>> created = db.create(member)
        >>> created.name
        'Test'
        >>> db.close()
    """

    def __init__(self, db_path: Path | str = DATABASE_FILE):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file (use ":memory:" for testing)

        Note:
            Connection is opened immediately. Use context manager or call
            close() explicitly to ensure proper cleanup.
        """
        self.db_path = Path(db_path) if db_path != ":memory:" else db_path

        try:
            # Enable foreign keys and row factory for easier data access
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()

            # Enable foreign key support (best practice for data integrity)
            self.cursor.execute("PRAGMA foreign_keys = ON")

        except sqlite3.Error as e:
            raise DatabaseError(
                f"❌ Failed to connect to database: {self.db_path}\n"
                f"   Error: {e}\n"
                f"💡 Tip: Check file permissions and disk space"
            ) from e

    def __enter__(self) -> 'RosterDatabase':
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with automatic cleanup."""
        self.close()

    def close(self) -> None:
        """Close database connection safely."""
        if hasattr(self, 'conn'):
            self.conn.close()

    def backup(self) -> Path:
        """Create backup of database file.

        Following L11-L14 feedback: Path objects, backups before modifications.

        Returns:
            Path to backup file

        Raises:
            DatabaseError: If backup fails
        """
        if self.db_path == ":memory:":
            # Cannot backup in-memory databases
            return Path(":memory:")

        try:
            # Create backup directory if needed
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)

            # Generate timestamped backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = BACKUP_DIR / f"roster_backup_{timestamp}.db"

            # Perform backup using SQLite's backup API (more reliable than file copy)
            backup_conn = sqlite3.connect(str(backup_path))
            with backup_conn:
                self.conn.backup(backup_conn)
            backup_conn.close()

            print(f"✓ Database backed up to: {backup_path}")
            return backup_path

        except Exception as e:
            raise DatabaseError(
                f"❌ Backup failed: {e}\n"
                f"💡 Tip: Check disk space and permissions"
            ) from e

    def create_table(self) -> None:
        """Create Roster table if it doesn't exist.

        Schema (following assignment requirements + best practices):
            - id: INTEGER PRIMARY KEY AUTOINCREMENT (added for best practices)
            - Name: TEXT NOT NULL
            - Species: TEXT NOT NULL
            - Age: INTEGER NOT NULL

        Note:
            Added 'id' column for proper database design, even though not
            required by assignment. This follows production best practices
            and makes updates/deletes safer.

        Raises:
            DatabaseError: If table creation fails
        """
        try:
            # SQL query with inline documentation
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS Roster (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    Species TEXT NOT NULL,
                    Age INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """

            self.cursor.execute(create_table_sql)
            self.conn.commit()

            # Verify table was created
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='Roster'"
            )
            if self.cursor.fetchone():
                print("✓ Roster table created successfully")

        except sqlite3.Error as e:
            raise DatabaseError(
                f"❌ Failed to create table: {e}\n"
                f"💡 Tip: Check database file permissions"
            ) from e

    def create(self, member: RosterMember) -> RosterMember:
        """Insert new roster member (CREATE operation).

        Following L14 feedback: transaction management, rollback on error.

        Args:
            member: RosterMember to insert

        Returns:
            RosterMember with assigned id

        Raises:
            DatabaseError: If insertion fails

        Example:
            >>> db = RosterDatabase(":memory:")
            >>> db.create_table()
            >>> member = RosterMember("Jean-Luc Picard", "Human", 59)
            >>> created = db.create(member)
            >>> created.id is not None
            True
            >>> db.close()
        """
        try:
            # Parameterized query to prevent SQL injection (security best practice)
            insert_sql = """
                INSERT INTO Roster (Name, Species, Age)
                VALUES (?, ?, ?)
            """

            self.cursor.execute(insert_sql, member.to_tuple())
            self.conn.commit()

            # Get the assigned ID
            member.id = self.cursor.lastrowid

            print(f"✓ Added: {member.name} (ID: {member.id})")
            return member

        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(
                f"❌ Failed to insert roster member\n"
                f"   Error: {e}\n"
                f"   Member: {member.name}\n"
                f"💡 Tip: Check for duplicate entries or database constraints"
            ) from e

    def read_all(self) -> List[RosterMember]:
        """Retrieve all roster members (READ operation).

        Returns:
            List of all RosterMember objects

        Example:
            >>> db = RosterDatabase(":memory:")
            >>> db.create_table()
            >>> members = db.read_all()
            >>> isinstance(members, list)
            True
            >>> db.close()
        """
        try:
            self.cursor.execute(
                "SELECT id, Name, Species, Age FROM Roster ORDER BY Name")
            rows = self.cursor.fetchall()
            return [RosterMember.from_row(row) for row in rows]

        except sqlite3.Error as e:
            raise DatabaseError(
                f"❌ Failed to read roster: {e}\n"
                f"💡 Tip: Check database integrity"
            ) from e

    def read_by_id(self, member_id: int) -> Optional[RosterMember]:
        """Retrieve roster member by ID.

        Args:
            member_id: Database ID of member

        Returns:
            RosterMember or None if not found
        """
        try:
            self.cursor.execute(
                "SELECT id, Name, Species, Age FROM Roster WHERE id = ?",
                (member_id,)
            )
            row = self.cursor.fetchone()
            return RosterMember.from_row(row) if row else None

        except sqlite3.Error as e:
            raise DatabaseError(
                f"❌ Failed to read member #{member_id}: {e}") from e

    def find_by_name(self, name: str) -> Optional[RosterMember]:
        """Find roster member by exact name (case-sensitive).

        Args:
            name: Full name to search for

        Returns:
            RosterMember or None if not found

        Example:
            >>> db = RosterDatabase(":memory:")
            >>> db.create_table()
            >>> member = RosterMember("Spock", "Vulcan", 62)
            >>> db.create(member)  # doctest: +ELLIPSIS
            <...>
            >>> found = db.find_by_name("Spock")
            >>> found.species if found else None
            'Vulcan'
            >>> db.close()
        """
        try:
            self.cursor.execute(
                "SELECT id, Name, Species, Age FROM Roster WHERE Name = ?",
                (name,)
            )
            row = self.cursor.fetchone()
            return RosterMember.from_row(row) if row else None

        except sqlite3.Error as e:
            raise DatabaseError(f"❌ Failed to search for '{name}': {e}") from e

    def find_by_species(self, species: str) -> List[RosterMember]:
        """Find all roster members of specified species.

        Args:
            species: Species to search for (case-insensitive)

        Returns:
            List of matching RosterMember objects

        Example:
            >>> db = RosterDatabase(":memory:")
            >>> db.create_table()
            >>> db.create(RosterMember("Worf", "Klingon", 40))  # doctest: +ELLIPSIS
            <...>
            >>> db.create(RosterMember("Gowron", "Klingon", 55))  # doctest: +ELLIPSIS
            <...>
            >>> klingons = db.find_by_species("Klingon")
            >>> len(klingons)
            2
            >>> db.close()
        """
        try:
            # Case-insensitive search using COLLATE NOCASE
            self.cursor.execute(
                "SELECT id, Name, Species, Age FROM Roster "
                "WHERE Species = ? COLLATE NOCASE ORDER BY Name",
                (species,)
            )
            rows = self.cursor.fetchall()
            return [RosterMember.from_row(row) for row in rows]

        except sqlite3.Error as e:
            raise DatabaseError(
                f"❌ Failed to search for species '{species}': {e}"
            ) from e

    def update(self, member_id: int, **updates) -> RosterMember:
        """Update roster member fields (UPDATE operation).

        Following L13-L14 feedback: transaction management, validation, rollback.

        Args:
            member_id: ID of member to update
            **updates: Fields to update (name, species, age)

        Returns:
            Updated RosterMember

        Raises:
            DatabaseError: If member not found or update fails
            ValueError: If updates contain invalid data

        Example:
            >>> db = RosterDatabase(":memory:")
            >>> db.create_table()
            >>> member = db.create(RosterMember("Old Name", "Human", 30))
            >>> updated = db.update(member.id, name="New Name", age=31)
            >>> updated.name
            'New Name'
            >>> db.close()
        """
        # Verify member exists
        member = self.read_by_id(member_id)
        if not member:
            raise DatabaseError(
                f"❌ Roster member not found: ID {member_id}\n"
                f"💡 Tip: Use 'View all members' to see valid IDs"
            )

        # Map user-friendly field names to database columns
        field_mapping = {
            'name': 'Name',
            'species': 'Species',
            'age': 'Age'
        }

        # Validate update fields
        valid_fields = set(field_mapping.keys())
        invalid_fields = set(updates.keys()) - valid_fields
        if invalid_fields:
            raise ValueError(
                f"❌ Invalid fields: {', '.join(invalid_fields)}\n"
                f"💡 Valid fields: {', '.join(valid_fields)}"
            )

        if not updates:
            raise ValueError("❌ No fields to update")

        try:
            # Create backup before modification (production best practice)
            if self.db_path != ":memory:":
                self.backup()

            # Build dynamic UPDATE query with parameterized values
            set_clauses = [f"{field_mapping[k]} = ?" for k in updates.keys()]
            update_sql = f"UPDATE Roster SET {', '.join(set_clauses)} WHERE id = ?"

            # Prepare parameters in same order as SET clauses
            params = list(updates.values()) + [member_id]

            self.cursor.execute(update_sql, params)
            self.conn.commit()

            # Fetch and return updated member
            updated_member = self.read_by_id(member_id)
            if updated_member:
                print(f"✓ Updated: {updated_member.name} (ID: {member_id})")
                return updated_member
            else:
                raise DatabaseError(
                    "Update succeeded but member not found afterward")

        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(
                f"❌ Failed to update member #{member_id}\n"
                f"   Error: {e}\n"
                f"💡 Tip: Check update values are valid"
            ) from e

    def delete(self, member_id: int) -> RosterMember:
        """Delete roster member (DELETE operation).

        Following L14 feedback: backup before destructive operations.

        Args:
            member_id: ID of member to delete

        Returns:
            Deleted RosterMember

        Raises:
            DatabaseError: If member not found or deletion fails
        """
        # Verify member exists
        member = self.read_by_id(member_id)
        if not member:
            raise DatabaseError(
                f"❌ Roster member not found: ID {member_id}\n"
                f"💡 Tip: Use 'View all members' to see valid IDs"
            )

        try:
            # Create backup before destructive operation
            if self.db_path != ":memory:":
                self.backup()

            self.cursor.execute(
                "DELETE FROM Roster WHERE id = ?", (member_id,))
            self.conn.commit()

            print(f"✓ Deleted: {member.name} (ID: {member_id})")
            return member

        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(
                f"❌ Failed to delete member #{member_id}\n"
                f"   Error: {e}"
            ) from e

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns dict with total members, species breakdown, age ranges, etc.
        """
        try:
            stats = {}

            # Total members
            self.cursor.execute("SELECT COUNT(*) FROM Roster")
            stats['total'] = self.cursor.fetchone()[0]

            if stats['total'] == 0:
                return stats

            # Species breakdown
            self.cursor.execute("""
                SELECT Species, COUNT(*) as count
                FROM Roster
                GROUP BY Species
                ORDER BY count DESC
            """)
            stats['species'] = {row[0]: row[1]
                                for row in self.cursor.fetchall()}

            # Age statistics
            self.cursor.execute("""
                SELECT MIN(Age) as min_age, MAX(Age) as max_age, AVG(Age) as avg_age
                FROM Roster
            """)
            row = self.cursor.fetchone()
            stats['age_min'] = row[0]
            stats['age_max'] = row[1]
            stats['age_avg'] = round(row[2], 1) if row[2] else 0

            return stats

        except sqlite3.Error as e:
            raise DatabaseError(f"❌ Failed to get statistics: {e}") from e


# ──────────────────────────────────────────────────────────────────────────────
# Task Implementations (matching assignment requirements exactly)
# ──────────────────────────────────────────────────────────────────────────────

def task1_create_database() -> RosterDatabase:
    """Task 1: Create database with Roster table.

    Assignment: "Create a new database with a table named Roster that has
    three fields: Name, Species, and Age."

    Returns:
        Initialized RosterDatabase with Roster table created
    """
    hr("Task 1: Create Database & Roster Table")

    print("Creating roster.db database...")
    print("Table schema:")
    print("  - Name (TEXT, NOT NULL)")
    print("  - Species (TEXT, NOT NULL)")
    print("  - Age (INTEGER, NOT NULL)")
    print("  - id (INTEGER PRIMARY KEY) — added for best practices")

    db = RosterDatabase(DATABASE_FILE)
    db.create_table()

    return db


def task2_populate_table(db: RosterDatabase) -> None:
    """Task 2: Populate table with initial crew members.

    Assignment: "Populate your new table with the following values:
    - Benjamin Sisko, Human, 40
    - Jadzia Dax, Trill, 300
    - Kira Nerys, Bajoran, 29"

    Args:
        db: RosterDatabase to populate
    """
    hr("Task 2: Populate Table with Initial Data")

    # Initial crew members (exactly as specified in assignment)
    initial_crew = [
        RosterMember("Benjamin Sisko", "Human", 40),
        RosterMember("Jadzia Dax", "Trill", 300),
        RosterMember("Kira Nerys", "Bajoran", 29)
    ]

    print(f"\nAdding {len(initial_crew)} crew members:")
    for member in initial_crew:
        try:
            db.create(member)
        except Exception as e:
            print(f"⚠ Warning: Could not add {member.name}: {e}")


def task3_update_jadzia(db: RosterDatabase) -> None:
    """Task 3: Update Jadzia Dax → Ezri Dax.

    Assignment: "Update the Name of Jadzia Dax to be Ezri Dax"

    Args:
        db: RosterDatabase to update
    """
    hr("Task 3: Update Jadzia Dax → Ezri Dax")

    # Find Jadzia Dax
    jadzia = db.find_by_name("Jadzia Dax")

    if not jadzia:
        print("❌ Jadzia Dax not found in roster")
        print("💡 Tip: Run Task 2 first to populate the table")
        return

    print(f"\nFound: {jadzia.name} (ID: {jadzia.id})")
    print("Updating to: Ezri Dax")

    # Update the name
    try:
        updated = db.update(jadzia.id, name="Ezri Dax")
        print(f"\n✓ Update successful!")
        updated.display(detailed=True)
    except Exception as e:
        print(f"❌ Update failed: {e}")


def task4_display_bajorans(db: RosterDatabase) -> None:
    """Task 4: Display Name and Age of all Bajorans.

    Assignment: "Display the Name and Age of everyone in the table
    classified as Bajoran."

    Args:
        db: RosterDatabase to query
    """
    hr("Task 4: Display Bajoran Crew Members")

    # Query for Bajorans
    bajorans = db.find_by_species("Bajoran")

    if not bajorans:
        print("📭 No Bajoran crew members found in roster")
        print("💡 Tip: Run Task 2 first to populate the table")
        return

    print(f"\n✓ Found {len(bajorans)} Bajoran crew member(s):")
    print("\n" + "="*60)
    print(f"{'Name':<30} {'Age':>10}")
    print("-"*60)

    for member in bajorans:
        print(f"{member.name:<30} {member.age:>10} years")

    print("="*60)


# ──────────────────────────────────────────────────────────────────────────────
# Interactive CLI & Demo Functions
# ──────────────────────────────────────────────────────────────────────────────

def demo_all_tasks() -> None:
    """Run all assignment tasks in sequence.

    This demonstrates the complete assignment solution.
    """
    hr("Running All Assignment Tasks")

    try:
        # Task 1: Create database
        db = task1_create_database()

        input("\nPress Enter to continue to Task 2...")

        # Task 2: Populate table
        task2_populate_table(db)

        input("\nPress Enter to continue to Task 3...")

        # Task 3: Update Jadzia → Ezri
        task3_update_jadzia(db)

        input("\nPress Enter to continue to Task 4...")

        # Task 4: Display Bajorans
        task4_display_bajorans(db)

        print("\n✓ All tasks completed successfully!")

        db.close()

    except Exception as e:
        print(f"\n❌ Error during task execution: {e}")


def interactive_crud_demo() -> None:
    """Interactive CRUD operations demo.

    Provides full database management interface beyond basic assignment.
    """
    hr("Interactive CRUD Operations")

    try:
        with RosterDatabase(DATABASE_FILE) as db:
            # Ensure table exists
            db.create_table()

            while True:
                print("\n" + "─"*60)
                print("Roster Database Operations:")
                print("  1. View all members")
                print("  2. Add new member")
                print("  3. Update member")
                print("  4. Delete member")
                print("  5. Search by species")
                print("  6. Database statistics")
                print("  0. Back to main menu")

                choice = input("\nChoose operation: ").strip()

                try:
                    if choice == "1":
                        # View all
                        members = db.read_all()
                        if not members:
                            print("\n📭 Roster is empty")
                        else:
                            print(f"\n📋 Roster ({len(members)} members):")
                            for member in members:
                                member.display(detailed=True)

                    elif choice == "2":
                        # Add new member
                        print("\n➕ Add New Member")
                        print("─"*60)

                        name = input("Name: ").strip()
                        if not name:
                            print("❌ Name cannot be empty")
                            continue

                        species = input("Species: ").strip()
                        if not species:
                            print("❌ Species cannot be empty")
                            continue

                        age = read_int("Age: ", min_val=0, max_val=1000)

                        member = RosterMember(name, species, age)
                        created = db.create(member)

                        print("\n✓ Member added successfully:")
                        created.display(detailed=True)

                    elif choice == "3":
                        # Update member
                        member_id = read_int(
                            "\nEnter member ID to update: ", min_val=1)

                        member = db.read_by_id(member_id)
                        if not member:
                            print(f"❌ Member #{member_id} not found")
                            continue

                        print("\nCurrent information:")
                        member.display(detailed=True)

                        print("\nEnter new values (press Enter to keep current):")

                        updates = {}

                        new_name = input(f"Name [{member.name}]: ").strip()
                        if new_name:
                            updates["name"] = new_name

                        new_species = input(
                            f"Species [{member.species}]: ").strip()
                        if new_species:
                            updates["species"] = new_species

                        new_age_str = input(f"Age [{member.age}]: ").strip()
                        if new_age_str:
                            updates["age"] = int(new_age_str)

                        if not updates:
                            print("💡 No changes made")
                            continue

                        updated = db.update(member_id, **updates)
                        print("\n✓ Member updated successfully:")
                        updated.display(detailed=True)

                    elif choice == "4":
                        # Delete member
                        member_id = read_int(
                            "\nEnter member ID to delete: ", min_val=1)

                        member = db.read_by_id(member_id)
                        if not member:
                            print(f"❌ Member #{member_id} not found")
                            continue

                        print("\nMember to delete:")
                        member.display(detailed=True)

                        if confirm("\n⚠️  Are you sure you want to delete this member?"):
                            db.delete(member_id)
                        else:
                            print("💡 Deletion cancelled")

                    elif choice == "5":
                        # Search by species
                        species = input("\nEnter species to search: ").strip()
                        if not species:
                            print("❌ Species cannot be empty")
                            continue

                        members = db.find_by_species(species)
                        if not members:
                            print(
                                f"❌ No members found with species '{species}'")
                        else:
                            print(f"\n✓ Found {len(members)} member(s):")
                            for member in members:
                                member.display(detailed=True)

                    elif choice == "6":
                        # Statistics
                        stats = db.get_statistics()

                        print("\n" + "="*60)
                        print("📊 Database Statistics")
                        print("="*60)
                        print(f"Total members: {stats['total']}")

                        if stats['total'] > 0:
                            print(
                                f"\nAge range: {stats['age_min']} - {stats['age_max']} years")
                            print(f"Average age: {stats['age_avg']} years")

                            print("\nSpecies distribution:")
                            for species, count in sorted(stats['species'].items(),
                                                         key=lambda x: x[1], reverse=True):
                                bar = "█" * count
                                print(f"  {species:20s}: {bar} ({count})")

                    elif choice == "0":
                        return

                    else:
                        print(f"❌ Invalid choice: '{choice}'")

                except Exception as e:
                    print(f"\n❌ Error: {e}")

    except Exception as e:
        print(f"❌ Database error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Test Runner
# ──────────────────────────────────────────────────────────────────────────────

def run_tests() -> Tuple[int, int]:
    """Run all doctests.

    Returns:
        Tuple of (failures, total_tests)
    """
    print("Running doctests...")
    failures, tests = doctest.testmod(verbose=False)

    if failures == 0:
        print(f"✓ All {tests} doctests passed!")
    else:
        print(f"❌ {failures} of {tests} doctests failed")

    return failures, tests


# ──────────────────────────────────────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────────────────────────────────────

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
    print(" 🗄️  Lesson 15: SQLite Database Operations ".center(70, "="))
    print("="*70)

    # Main menu loop
    try:
        while True:
            hr("Main Menu")
            print("Choose an option:\n")
            print("  📝 Assignment Tasks:")
            print("     1) Task 1: Create Database & Table")
            print("     2) Task 2: Populate Table")
            print("     3) Task 3: Update Jadzia → Ezri")
            print("     4) Task 4: Display Bajorans")
            print("     5) Run All Tasks (1-4)")
            print("\n  🔧 Additional Features:")
            print("     6) Interactive CRUD Operations")
            print("     7) View Database Info")
            print("\n  🧪 Tests — Run doctests")
            print("  0️⃣  Exit")

            choice = input("\nSelect option: ").strip()

            try:
                if choice == "1":
                    with task1_create_database() as db:
                        pass

                elif choice == "2":
                    with RosterDatabase(DATABASE_FILE) as db:
                        db.create_table()
                        task2_populate_table(db)

                elif choice == "3":
                    with RosterDatabase(DATABASE_FILE) as db:
                        task3_update_jadzia(db)

                elif choice == "4":
                    with RosterDatabase(DATABASE_FILE) as db:
                        task4_display_bajorans(db)

                elif choice == "5":
                    demo_all_tasks()

                elif choice == "6":
                    interactive_crud_demo()

                elif choice == "7":
                    # Database info
                    hr("Database Information")
                    print(f"Database file: {DATABASE_FILE.absolute()}")
                    print(
                        f"File exists: {'Yes' if DATABASE_FILE.exists() else 'No'}")

                    if DATABASE_FILE.exists():
                        size_bytes = DATABASE_FILE.stat().st_size
                        size_kb = size_bytes / 1024
                        print(
                            f"File size: {size_kb:.2f} KB ({size_bytes:,} bytes)")

                        with RosterDatabase(DATABASE_FILE) as db:
                            stats = db.get_statistics()
                            print(f"Total members: {stats['total']}")

                            if stats['total'] > 0:
                                print(f"\nSpecies:")
                                for species, count in stats['species'].items():
                                    print(f"  - {species}: {count}")

                elif choice.lower() in ("tests", "test", "🧪", "t"):
                    run_tests()
                    input("\nPress Enter to continue...")

                elif choice == "0":
                    print("\n👋 Thank you for using Lesson 15!")
                    return 0

                else:
                    print(f"❌ Invalid option: '{choice}'")
                    print("💡 Please enter a number from the menu")

            except KeyboardInterrupt:
                print("\n⚠ Operation cancelled")
                continue

            except Exception as e:
                print(f"\n❌ Error: {e}")
                if "--debug" in argv:
                    import traceback
                    traceback.print_exc()

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
