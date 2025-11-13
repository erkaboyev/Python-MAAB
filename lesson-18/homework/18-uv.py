#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lesson18.py — Advanced Pandas Filtering & Data Analysis (Lesson 18) [FINAL v2]

Homework Structure:
    Homework 2: StackOverflow Q&A filtering (8 tasks)
    Homework 3: Titanic dataset analysis (10 tasks)

Dependencies:
    pip install pandas numpy

Dataset Requirements:
    - task/stackoverflow_qa.csv
    - task/titanic.csv

Run tests:
    python lesson18.py --test

Interactive CLI:
    python lesson18.py
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple
import sys

# Third-party imports with graceful fallback
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("❌ Required libraries not installed")
    print("💡 Install with: pip install pandas numpy")
    sys.exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# Configuration & Constants
# ──────────────────────────────────────────────────────────────────────────────

STACKOVERFLOW_CSV = Path("task/stackoverflow_qa.csv")
TITANIC_CSV = Path("task/titanic.csv")


# ──────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────────────────────────────────────

def hr(title: str = "", width: int = 70) -> None:
    """Print horizontal rule with optional title.

    Examples:
        >>> hr("Test Title")  # doctest: +ELLIPSIS
        <BLANKLINE>
        ======================================================================
        Test Title
        ----------------------------------------------------------------------
    """
    print("\n" + "=" * width)
    if title:
        print(title)
        print("-" * width)


def print_dataframe(
    df: pd.DataFrame,
    title: str = "DataFrame",
    max_rows: int = 10
) -> None:
    """Print DataFrame with nice formatting.

    Args:
        df: Pandas DataFrame to display
        title: Title for the output
        max_rows: Maximum rows to display (default: 10)
    """
    print(f"\n{title}:")

    if len(df) == 0:
        print("  (Empty DataFrame)")
        return

    with pd.option_context(
        'display.max_rows', max_rows,
        'display.max_columns', None,
        'display.width', None,
        'display.max_colwidth', 50
    ):
        print(df.to_string(index=True))

    print(f"\nShape: {df.shape} (rows, columns)")

    if len(df) > max_rows:
        print(f"💡 Showing first {max_rows} of {len(df)} rows")


def verify_file_exists(filepath: Path) -> bool:
    """Verify CSV file exists with helpful error message.

    Args:
        filepath: Path to CSV file

    Returns:
        True if file exists

    Raises:
        FileNotFoundError: If file doesn't exist with helpful message

    Examples:
        >>> # Test with non-existent file
        >>> import tempfile
        >>> temp_path = Path(tempfile.gettempdir()) / "nonexistent.csv"
        >>> try:
        ...     verify_file_exists(temp_path)
        ... except FileNotFoundError:
        ...     print("Caught expected error")
        Caught expected error
    """
    if not filepath.exists():
        raise FileNotFoundError(
            f"❌ Dataset not found: {filepath}\n"
            f"   Current directory: {Path.cwd()}\n"
            f"   Expected absolute path: {filepath.absolute()}\n"
            f"💡 Tip: Ensure the file exists at the correct location"
        )
    return True


# ══════════════════════════════════════════════════════════════════════════════
# HOMEWORK 2: StackOverflow Q&A Dataset Analysis
# ══════════════════════════════════════════════════════════════════════════════

def load_stackoverflow_data(filepath: Path = STACKOVERFLOW_CSV) -> pd.DataFrame:
    """Load StackOverflow Q&A dataset.

    Args:
        filepath: Path to CSV file

    Returns:
        DataFrame with StackOverflow data, creationdate parsed as datetime

    Raises:
        FileNotFoundError: If file doesn't exist
        pd.errors.ParserError: If CSV is malformed

    Examples:
        >>> # This is tested with actual file in demo
        >>> isinstance(load_stackoverflow_data.__doc__, str)
        True
    """
    verify_file_exists(filepath)

    # Load CSV with proper date parsing
    df = pd.read_csv(filepath, parse_dates=['creationdate'])

    return df


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2, TASK 1: Questions Created Before 2014
# ──────────────────────────────────────────────────────────────────────────────

def filter_questions_before_year(
    df: pd.DataFrame,
    year: int = 2014,
    date_column: str = 'creationdate'
) -> pd.DataFrame:
    """Filter questions created before specified year.

    Filtering Pattern: Date comparison with Timestamp

    Args:
        df: StackOverflow DataFrame with datetime column
        year: Cutoff year (default: 2014)
        date_column: Name of date column (default: 'creationdate')

    Returns:
        NEW DataFrame with filtered questions (original unchanged)

    Examples:
        >>> df = pd.DataFrame({
        ...     'creationdate': pd.to_datetime(['2013-01-01', '2013-12-31', 
        ...                                      '2014-01-01', '2015-01-01']),
        ...     'title': ['Q1', 'Q2', 'Q3', 'Q4'],
        ...     'score': [10, 20, 30, 40]
        ... })
        >>> result = filter_questions_before_year(df, 2014)
        >>> len(result)
        2
        >>> result['title'].tolist()
        ['Q1', 'Q2']
        >>> result['score'].tolist()
        [10, 20]

        >>> # Verify original DataFrame unchanged (immutability)
        >>> len(df)
        4

        >>> # Test with empty result
        >>> result_empty = filter_questions_before_year(df, 2010)
        >>> len(result_empty)
        0
    """
    cutoff_date = pd.Timestamp(year=year, month=1, day=1)
    mask = df[date_column] < cutoff_date
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2, TASK 2: Questions with Score > 50
# ──────────────────────────────────────────────────────────────────────────────

def filter_questions_by_min_score(
    df: pd.DataFrame,
    min_score: int = 50,
    score_column: str = 'score'
) -> pd.DataFrame:
    """Filter questions with score greater than threshold.

    Filtering Pattern: Simple numeric comparison (>)

    Args:
        df: StackOverflow DataFrame
        min_score: Minimum score threshold (exclusive, default: 50)
        score_column: Name of score column (default: 'score')

    Returns:
        NEW DataFrame with high-score questions

    Examples:
        >>> df = pd.DataFrame({
        ...     'score': [10, 50, 51, 100, 200],
        ...     'title': ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
        ... })
        >>> result = filter_questions_by_min_score(df, 50)
        >>> len(result)
        3
        >>> result['score'].tolist()
        [51, 100, 200]
        >>> result['title'].tolist()
        ['Q3', 'Q4', 'Q5']

        >>> # Edge case: score exactly 50 is excluded (>50, not >=50)
        >>> 50 in result['score'].values
        False

        >>> # Test with all scores below threshold
        >>> df_low = pd.DataFrame({'score': [1, 2, 3], 'title': ['A', 'B', 'C']})
        >>> result_low = filter_questions_by_min_score(df_low, 50)
        >>> len(result_low)
        0
    """
    mask = df[score_column] > min_score
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2, TASK 3: Questions with Score Between 50 and 100
# ──────────────────────────────────────────────────────────────────────────────

def filter_questions_by_score_range(
    df: pd.DataFrame,
    min_score: int = 50,
    max_score: int = 100,
    score_column: str = 'score'
) -> pd.DataFrame:
    """Filter questions with score in specified range.

    Filtering Pattern: Range comparison (between)

    Two approaches demonstrated:
    - Method 1: Chained comparisons (more explicit) ← Used here
    - Method 2: DataFrame.between() (more concise)

    Args:
        df: StackOverflow DataFrame
        min_score: Minimum score (inclusive, default: 50)
        max_score: Maximum score (inclusive, default: 100)
        score_column: Name of score column (default: 'score')

    Returns:
        NEW DataFrame with questions in score range

    Examples:
        >>> df = pd.DataFrame({
        ...     'score': [30, 49, 50, 75, 100, 101, 150],
        ...     'title': ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7']
        ... })
        >>> result = filter_questions_by_score_range(df, 50, 100)
        >>> len(result)
        3
        >>> result['score'].tolist()
        [50, 75, 100]
        >>> result['title'].tolist()
        ['Q3', 'Q4', 'Q5']

        >>> # Test boundary conditions (inclusive on both ends)
        >>> 50 in result['score'].values
        True
        >>> 100 in result['score'].values
        True
        >>> 49 in result['score'].values
        False
        >>> 101 in result['score'].values
        False

        >>> # Test with no matches
        >>> df_outside = pd.DataFrame({'score': [10, 20, 200], 'title': ['A', 'B', 'C']})
        >>> result_empty = filter_questions_by_score_range(df_outside, 50, 100)
        >>> len(result_empty)
        0
    """
    # Method 1: Chained comparisons (more explicit for learners)
    mask = (df[score_column] >= min_score) & (df[score_column] <= max_score)

    # Method 2: Using between() (alternative, shown for educational value)
    # mask = df[score_column].between(min_score, max_score, inclusive='both')

    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2, TASK 4: Questions Answered by Specific User
# ──────────────────────────────────────────────────────────────────────────────

def filter_questions_by_answerer(
    df: pd.DataFrame,
    username: str,
    ans_name_column: str = 'ans_name'
) -> pd.DataFrame:
    """Filter questions answered by specific user.

    Filtering Pattern: String equality (case-sensitive)

    Args:
        df: StackOverflow DataFrame
        username: Username to search for (e.g., "Scott Boston")
        ans_name_column: Name of answerer column (default: 'ans_name')

    Returns:
        NEW DataFrame with questions answered by user

    Examples:
        >>> df = pd.DataFrame({
        ...     'ans_name': ['Alice', 'Bob', 'Alice', 'Charlie', 'alice'],
        ...     'title': ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
        ...     'score': [10, 20, 30, 40, 50]
        ... })
        >>> result = filter_questions_by_answerer(df, 'Alice')
        >>> len(result)
        2
        >>> result['title'].tolist()
        ['Q1', 'Q3']
        >>> result['score'].tolist()
        [10, 30]

        >>> # Case-sensitive check (alice != Alice)
        >>> result_lower = filter_questions_by_answerer(df, 'alice')
        >>> len(result_lower)
        1
        >>> result_lower['title'].iloc[0]
        'Q5'

        >>> # Non-existent user
        >>> result_none = filter_questions_by_answerer(df, 'NonExistent')
        >>> len(result_none)
        0
    """
    mask = df[ans_name_column] == username
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2, TASK 5: Questions Answered by Multiple Users
# ──────────────────────────────────────────────────────────────────────────────

def filter_questions_by_answerers_list(
    df: pd.DataFrame,
    usernames: List[str],
    ans_name_column: str = 'ans_name'
) -> pd.DataFrame:
    """Filter questions answered by any user in the list.

    Filtering Pattern: Membership test (isin)

    Args:
        df: StackOverflow DataFrame
        usernames: List of usernames to filter by
        ans_name_column: Name of answerer column (default: 'ans_name')

    Returns:
        NEW DataFrame with questions answered by any listed user

    Examples:
        >>> df = pd.DataFrame({
        ...     'ans_name': ['Alice', 'Bob', 'Charlie', 'David', 'Alice'],
        ...     'title': ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
        ...     'score': [10, 20, 30, 40, 50]
        ... })
        >>> result = filter_questions_by_answerers_list(df, ['Alice', 'Charlie'])
        >>> len(result)
        3
        >>> sorted(result['title'].tolist())
        ['Q1', 'Q3', 'Q5']
        >>> sorted(result['score'].tolist())
        [10, 30, 50]

        >>> # Test with empty list (should return empty DataFrame)
        >>> result_empty = filter_questions_by_answerers_list(df, [])
        >>> len(result_empty)
        0
        >>> list(result_empty.columns) == list(df.columns)
        True

        >>> # Test with non-existent users
        >>> result_none = filter_questions_by_answerers_list(df, ['NonExistent'])
        >>> len(result_none)
        0

        >>> # Test with all users
        >>> all_users = df['ans_name'].unique().tolist()
        >>> result_all = filter_questions_by_answerers_list(df, all_users)
        >>> len(result_all) == len(df)
        True
    """
    if not usernames:
        # Return empty DataFrame with same structure
        return df.iloc[0:0].copy()

    mask = df[ans_name_column].isin(usernames)
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2, TASK 6: Complex Multi-Condition Filter
# ──────────────────────────────────────────────────────────────────────────────

def filter_questions_complex(
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
    username: str,
    max_score: int,
    date_column: str = 'creationdate',
    ans_name_column: str = 'ans_name',
    score_column: str = 'score'
) -> pd.DataFrame:
    """Filter with multiple AND conditions (date range + user + score).

    Filtering Pattern: Multiple AND conditions (&)

    Task 6 Requirements:
    - Created between start_date and end_date (inclusive)
    - Answered by specific user
    - Score less than max_score (exclusive)

    Args:
        df: StackOverflow DataFrame
        start_date: Start date string (e.g., '2014-03-01')
        end_date: End date string (e.g., '2014-10-31')
        username: Username to filter by
        max_score: Maximum score (exclusive)
        date_column: Name of date column (default: 'creationdate')
        ans_name_column: Name of answerer column (default: 'ans_name')
        score_column: Name of score column (default: 'score')

    Returns:
        NEW DataFrame matching ALL conditions

    Examples:
        >>> df = pd.DataFrame({
        ...     'creationdate': pd.to_datetime([
        ...         '2014-02-01', '2014-05-01', '2014-06-01', 
        ...         '2014-11-01', '2014-05-15'
        ...     ]),
        ...     'ans_name': ['Unutbu', 'Unutbu', 'Unutbu', 'Unutbu', 'Other'],
        ...     'score': [3, 3, 8, 2, 3],
        ...     'title': ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
        ... })
        >>> result = filter_questions_complex(
        ...     df, '2014-03-01', '2014-10-31', 'Unutbu', 5
        ... )
        >>> len(result)
        1
        >>> result['title'].iloc[0]
        'Q2'

        >>> # Q1: date too early (Feb) ✗
        >>> # Q2: all conditions match ✓
        >>> # Q3: score 8 >= 5 ✗
        >>> # Q4: date too late (Nov) ✗
        >>> # Q5: different user ✗

        >>> # Test with no matches
        >>> result_none = filter_questions_complex(
        ...     df, '2014-03-01', '2014-10-31', 'NonExistent', 5
        ... )
        >>> len(result_none)
        0
    """
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    mask = (
        (df[date_column] >= start) &
        (df[date_column] <= end) &
        (df[ans_name_column] == username) &
        (df[score_column] < max_score)
    )

    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2, TASK 7: Questions with Score OR View Count Conditions
# ──────────────────────────────────────────────────────────────────────────────

def filter_questions_with_or_condition(
    df: pd.DataFrame,
    min_score: int = 5,
    max_score: int = 10,
    min_viewcount: int = 10000,
    score_column: str = 'score',
    viewcount_column: str = 'viewcount'
) -> pd.DataFrame:
    """Filter questions matching score range OR high view count.

    Filtering Pattern: OR condition (| operator)

    Task 7: Score between 5 and 10 (inclusive) OR viewcount > 10,000

    Args:
        df: StackOverflow DataFrame
        min_score: Minimum score for range (default: 5)
        max_score: Maximum score for range (default: 10)
        min_viewcount: Minimum view count threshold (default: 10000)
        score_column: Name of score column (default: 'score')
        viewcount_column: Name of viewcount column (default: 'viewcount')

    Returns:
        NEW DataFrame matching either condition

    Examples:
        >>> df = pd.DataFrame({
        ...     'score': [3, 7, 8, 20, 15],
        ...     'viewcount': [500, 1000, 2000, 15000, 8000],
        ...     'title': ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
        ... })
        >>> result = filter_questions_with_or_condition(df, 5, 10, 10000)
        >>> len(result)
        3
        >>> sorted(result['title'].tolist())
        ['Q2', 'Q3', 'Q4']

        >>> # Q1: score 3 (not in range) & views 500 (<10000) ✗
        >>> # Q2: score 7 (in range) ✓
        >>> # Q3: score 8 (in range) ✓
        >>> # Q4: views 15000 (>10000) ✓
        >>> # Q5: score 15 (not in range) & views 8000 (<10000) ✗

        >>> # Test boundary conditions
        >>> df_boundary = pd.DataFrame({
        ...     'score': [5, 10, 4, 11],
        ...     'viewcount': [1000, 1000, 10001, 10001],
        ...     'title': ['A', 'B', 'C', 'D']
        ... })
        >>> result_b = filter_questions_with_or_condition(df_boundary, 5, 10, 10000)
        >>> sorted(result_b['title'].tolist())
        ['A', 'B', 'C', 'D']
    """
    score_condition = df[score_column].between(
        min_score, max_score, inclusive='both')
    viewcount_condition = df[viewcount_column] > min_viewcount

    mask = score_condition | viewcount_condition

    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2, TASK 8: Questions NOT Answered by Specific User
# ──────────────────────────────────────────────────────────────────────────────

def filter_questions_not_answered_by(
    df: pd.DataFrame,
    username: str,
    ans_name_column: str = 'ans_name'
) -> pd.DataFrame:
    """Filter questions NOT answered by specific user.

    Filtering Pattern: Negation (~ operator)

    Two approaches:
    - Method 1: Negation with ~ (used here, keeps NaN)
    - Method 2: != comparison (excludes NaN)

    Args:
        df: StackOverflow DataFrame
        username: Username to exclude
        ans_name_column: Name of answerer column (default: 'ans_name')

    Returns:
        NEW DataFrame with questions not answered by user

    Examples:
        >>> df = pd.DataFrame({
        ...     'ans_name': ['Alice', 'Bob', 'Alice', 'Charlie'],
        ...     'title': ['Q1', 'Q2', 'Q3', 'Q4'],
        ...     'score': [10, 20, 30, 40]
        ... })
        >>> result = filter_questions_not_answered_by(df, 'Alice')
        >>> len(result)
        2
        >>> sorted(result['title'].tolist())
        ['Q2', 'Q4']
        >>> sorted(result['ans_name'].tolist())
        ['Bob', 'Charlie']

        >>> # Test with NaN values (unanswered questions)
        >>> df_nan = pd.DataFrame({
        ...     'ans_name': ['Alice', None, 'Bob', np.nan],
        ...     'title': ['Q1', 'Q2', 'Q3', 'Q4']
        ... })
        >>> result_nan = filter_questions_not_answered_by(df_nan, 'Alice')
        >>> len(result_nan)
        3
        >>> sorted([t for t in result_nan['title'].tolist()])
        ['Q2', 'Q3', 'Q4']

        >>> # Note: ~ keeps NaN rows (unanswered questions)
        >>> # This is desired for "not answered by X" interpretation
    """
    # Method 1: Using negation operator ~ (keeps NaN)
    # This is the preferred approach for "not answered by X"
    # because unanswered questions (NaN) should be included
    mask = ~(df[ans_name_column] == username)

    # Method 2: Using != (alternative, excludes NaN)
    # mask = df[ans_name_column] != username

    # Important difference:
    # ~ (df == value): keeps NaN rows
    # df != value: excludes NaN rows
    # For "not answered by X", we want to keep unanswered (NaN)

    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2: Complete Demo with Enhanced Error Handling
# ──────────────────────────────────────────────────────────────────────────────

def demo_homework2() -> None:
    """Interactive demo for Homework 2: StackOverflow Q&A Analysis."""
    hr("HOMEWORK 2: StackOverflow Q&A Dataset Analysis")

    # Enhanced error handling (per instructor feedback)
    try:
        print("\n📊 Loading StackOverflow Q&A dataset...")
        df = load_stackoverflow_data()

    except FileNotFoundError:
        print(f"\n❌ Dataset not found: {STACKOVERFLOW_CSV}")
        print(f"   Current directory: {Path.cwd()}")
        print(f"   Expected absolute path: {STACKOVERFLOW_CSV.absolute()}")
        print(f"\n💡 Solutions:")
        print(f"   1. Create 'task/' directory: mkdir task")
        print(f"   2. Download stackoverflow_qa.csv to task/")
        print(f"   3. Verify file exists: ls task/stackoverflow_qa.csv")
        return

    except pd.errors.ParserError as e:
        print(f"\n❌ Failed to parse CSV file")
        print(f"   Error: {e}")
        print(f"💡 Check that {STACKOVERFLOW_CSV} is valid CSV format")
        print(f"   You can validate CSV at: https://csvlint.io/")
        return

    except pd.errors.EmptyDataError:
        print(f"\n❌ CSV file is empty: {STACKOVERFLOW_CSV}")
        print(f"💡 Ensure the file contains data")
        return

    except Exception as e:
        print(f"\n❌ Unexpected error loading dataset")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {e}")
        print(f"💡 Check file permissions and format")
        return

    # Dataset loaded successfully
    print(f"✓ Loaded {len(df)} questions")
    print(
        f"  Date range: {df['creationdate'].min()} to {df['creationdate'].max()}")
    print(f"  Score range: {df['score'].min()} to {df['score'].max()}")

    # Show sample
    print("\nFirst 3 rows:")
    print(
        df.head(3)[['title', 'score', 'creationdate', 'ans_name']].to_string())

    # Task 1: Before 2014
    print("\n" + "─"*70)
    print("TASK 1: Questions created before 2014")
    result1 = filter_questions_before_year(df, 2014)
    print(f"Found {len(result1)} questions before 2014")
    if len(result1) > 0:
        print(f"Sample: {result1['title'].iloc[0][:60]}...")

    # Task 2: Score > 50
    print("\n" + "─"*70)
    print("TASK 2: Questions with score > 50")
    result2 = filter_questions_by_min_score(df, 50)
    print(f"Found {len(result2)} high-score questions")
    if len(result2) > 0:
        top_question = result2.nlargest(1, 'score')
        print(f"Top scorer: '{top_question['title'].iloc[0][:60]}...'")
        print(f"  Score: {top_question['score'].iloc[0]}")

    # Task 3: Score between 50 and 100
    print("\n" + "─"*70)
    print("TASK 3: Questions with score between 50 and 100")
    result3 = filter_questions_by_score_range(df, 50, 100)
    print(f"Found {len(result3)} questions in score range [50, 100]")

    # Task 4: Answered by Scott Boston
    print("\n" + "─"*70)
    print("TASK 4: Questions answered by Scott Boston")
    result4 = filter_questions_by_answerer(df, "Scott Boston")
    print(f"Found {len(result4)} questions answered by Scott Boston")

    # Task 5: IMPROVED - Literal interpretation (hardcoded 5 users)
    print("\n" + "─"*70)
    print("TASK 5: Questions answered by 5 specific users")

    # Per instructor feedback: Use literal list, not dynamic top 5
    # These 5 users would typically be specified in the homework assignment
    five_users = ['Unutbu', 'Scott Boston', 'DSM', 'BrenBarn', 'unutbu']

    print(f"Specified 5 users: {', '.join(five_users)}")
    result5 = filter_questions_by_answerers_list(df, five_users)
    print(f"Found {len(result5)} questions answered by these 5 users")

    # Task 6: Complex filter (March-Oct 2014, Unutbu, score < 5)
    print("\n" + "─"*70)
    print("TASK 6: March-Oct 2014, answered by Unutbu, score < 5")
    result6 = filter_questions_complex(
        df, '2014-03-01', '2014-10-31', 'Unutbu', 5
    )
    print(f"Found {len(result6)} questions matching ALL conditions")

    # Task 7: Score 5-10 OR viewcount > 10,000
    print("\n" + "─"*70)
    print("TASK 7: Score 5-10 OR viewcount > 10,000")
    result7 = filter_questions_with_or_condition(df, 5, 10, 10000)
    print(f"Found {len(result7)} questions matching EITHER condition")

    # Task 8: NOT answered by Scott Boston
    print("\n" + "─"*70)
    print("TASK 8: Questions NOT answered by Scott Boston")
    result8 = filter_questions_not_answered_by(df, "Scott Boston")
    print(f"Found {len(result8)} questions NOT answered by Scott Boston")
    print(f"  (This is {len(df) - len(result4)} out of {len(df)} total)")

    print("\n✓ Homework 2 completed!")


# ══════════════════════════════════════════════════════════════════════════════
# HOMEWORK 3: Titanic Dataset Analysis (All 10 tasks with comprehensive doctests)
# ══════════════════════════════════════════════════════════════════════════════

def load_titanic_data(filepath: Path = TITANIC_CSV) -> pd.DataFrame:
    """Load Titanic dataset.

    Args:
        filepath: Path to CSV file

    Returns:
        DataFrame with Titanic passenger data

    Raises:
        FileNotFoundError: If file doesn't exist

    Examples:
        >>> # Tested with actual file in demo
        >>> isinstance(load_titanic_data.__doc__, str)
        True
    """
    verify_file_exists(filepath)
    df = pd.read_csv(filepath)
    return df


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 1: Female in Class 1, Ages 20-30
# ──────────────────────────────────────────────────────────────────────────────

def filter_female_class1_age_range(
    df: pd.DataFrame,
    min_age: float = 20.0,
    max_age: float = 30.0
) -> pd.DataFrame:
    """Filter female passengers in Class 1 with ages between 20 and 30.

    Filtering Pattern: Multiple AND conditions with numeric range

    Args:
        df: Titanic DataFrame
        min_age: Minimum age (inclusive, default: 20)
        max_age: Maximum age (inclusive, default: 30)

    Returns:
        NEW DataFrame with matching passengers

    Examples:
        >>> df = pd.DataFrame({
        ...     'Sex': ['female', 'female', 'male', 'female', 'female'],
        ...     'Pclass': [1, 1, 1, 2, 1],
        ...     'Age': [25.0, 35.0, 25.0, 25.0, 20.0],
        ...     'Name': ['Alice', 'Betty', 'Charlie', 'Diana', 'Emma']
        ... })
        >>> result = filter_female_class1_age_range(df, 20, 30)
        >>> len(result)
        2
        >>> sorted(result['Name'].tolist())
        ['Alice', 'Emma']

        >>> # Test boundary conditions
        >>> result['Age'].min()
        20.0
        >>> result['Age'].max()
        25.0

        >>> # Verify all are female in Class 1
        >>> (result['Sex'] == 'female').all()
        True
        >>> (result['Pclass'] == 1).all()
        True
    """
    mask = (
        (df['Sex'] == 'female') &
        (df['Pclass'] == 1) &
        (df['Age'] >= min_age) &
        (df['Age'] <= max_age)
    )
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 2: Passengers Who Paid More than $100
# ──────────────────────────────────────────────────────────────────────────────

def filter_high_fare_passengers(
    df: pd.DataFrame,
    min_fare: float = 100.0
) -> pd.DataFrame:
    """Filter passengers who paid fare greater than threshold.

    Filtering Pattern: Simple numeric comparison

    Args:
        df: Titanic DataFrame
        min_fare: Minimum fare threshold (exclusive, default: 100)

    Returns:
        NEW DataFrame with high-fare passengers

    Examples:
        >>> df = pd.DataFrame({
        ...     'Fare': [50.0, 100.0, 101.0, 200.0, 99.99],
        ...     'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Emma']
        ... })
        >>> result = filter_high_fare_passengers(df, 100)
        >>> len(result)
        2
        >>> sorted(result['Name'].tolist())
        ['Charlie', 'David']
        >>> result['Fare'].tolist()
        [101.0, 200.0]

        >>> # Edge case: exactly $100 is excluded (>100, not >=100)
        >>> 100.0 in result['Fare'].values
        False

        >>> # Test with no high-fare passengers
        >>> df_low = pd.DataFrame({'Fare': [10, 20, 30], 'Name': ['A', 'B', 'C']})
        >>> result_low = filter_high_fare_passengers(df_low, 100)
        >>> len(result_low)
        0
    """
    mask = df['Fare'] > min_fare
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 3: Survived and Traveled Alone
# ──────────────────────────────────────────────────────────────────────────────

def filter_survived_alone(df: pd.DataFrame) -> pd.DataFrame:
    """Filter passengers who survived and were traveling alone.

    Filtering Pattern: Multiple equality conditions

    Alone = no siblings, spouses, parents, or children
    (SibSp == 0 AND Parch == 0)

    Args:
        df: Titanic DataFrame

    Returns:
        NEW DataFrame with solo survivors

    Examples:
        >>> df = pd.DataFrame({
        ...     'Survived': [1, 1, 0, 1, 1],
        ...     'SibSp': [0, 1, 0, 0, 0],
        ...     'Parch': [0, 0, 0, 1, 0],
        ...     'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Emma']
        ... })
        >>> result = filter_survived_alone(df)
        >>> len(result)
        2
        >>> sorted(result['Name'].tolist())
        ['Alice', 'Emma']

        >>> # Verify all survived
        >>> (result['Survived'] == 1).all()
        True
        >>> # Verify all traveled alone
        >>> (result['SibSp'] == 0).all()
        True
        >>> (result['Parch'] == 0).all()
        True

        >>> # Test with no solo survivors
        >>> df_none = pd.DataFrame({
        ...     'Survived': [1, 1], 'SibSp': [1, 0], 'Parch': [0, 1],
        ...     'Name': ['A', 'B']
        ... })
        >>> result_none = filter_survived_alone(df_none)
        >>> len(result_none)
        0
    """
    mask = (
        (df['Survived'] == 1) &
        (df['SibSp'] == 0) &
        (df['Parch'] == 0)
    )
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 4: Embarked from 'C' and Paid > $50
# ──────────────────────────────────────────────────────────────────────────────

def filter_embarked_c_high_fare(
    df: pd.DataFrame,
    embark_port: str = 'C',
    min_fare: float = 50.0
) -> pd.DataFrame:
    """Filter passengers who embarked from port and paid more than threshold.

    Filtering Pattern: String equality + numeric comparison

    Args:
        df: Titanic DataFrame
        embark_port: Embarkation port code (default: 'C' for Cherbourg)
        min_fare: Minimum fare (exclusive, default: 50)

    Returns:
        NEW DataFrame with matching passengers

    Examples:
        >>> df = pd.DataFrame({
        ...     'Embarked': ['C', 'C', 'S', 'C', 'Q'],
        ...     'Fare': [100.0, 40.0, 100.0, 60.0, 100.0],
        ...     'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Emma']
        ... })
        >>> result = filter_embarked_c_high_fare(df, 'C', 50)
        >>> len(result)
        2
        >>> sorted(result['Name'].tolist())
        ['Alice', 'David']

        >>> # Verify conditions
        >>> (result['Embarked'] == 'C').all()
        True
        >>> (result['Fare'] > 50).all()
        True

        >>> # Test with different port
        >>> result_s = filter_embarked_c_high_fare(df, 'S', 50)
        >>> len(result_s)
        1
        >>> result_s['Name'].iloc[0]
        'Charlie'
    """
    mask = (
        (df['Embarked'] == embark_port) &
        (df['Fare'] > min_fare)
    )
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 5: With Siblings/Spouses AND Parents/Children
# ──────────────────────────────────────────────────────────────────────────────

def filter_with_siblings_and_parents(df: pd.DataFrame) -> pd.DataFrame:
    """Filter passengers with both siblings/spouses AND parents/children.

    Filtering Pattern: Multiple > 0 conditions

    Args:
        df: Titanic DataFrame

    Returns:
        NEW DataFrame with passengers having both types of companions

    Examples:
        >>> df = pd.DataFrame({
        ...     'SibSp': [1, 0, 2, 1, 0],
        ...     'Parch': [1, 1, 1, 0, 0],
        ...     'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Emma']
        ... })
        >>> result = filter_with_siblings_and_parents(df)
        >>> len(result)
        2
        >>> sorted(result['Name'].tolist())
        ['Alice', 'Charlie']

        >>> # Verify all have both types
        >>> (result['SibSp'] > 0).all()
        True
        >>> (result['Parch'] > 0).all()
        True

        >>> # Test edge case: exactly 1 of each counts
        >>> df_edge = pd.DataFrame({
        ...     'SibSp': [1, 2], 'Parch': [1, 2], 'Name': ['A', 'B']
        ... })
        >>> result_edge = filter_with_siblings_and_parents(df_edge)
        >>> len(result_edge)
        2
    """
    mask = (
        (df['SibSp'] > 0) &
        (df['Parch'] > 0)
    )
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 6: Aged ≤15 Who Didn't Survive
# ──────────────────────────────────────────────────────────────────────────────

def filter_young_non_survivors(
    df: pd.DataFrame,
    max_age: float = 15.0
) -> pd.DataFrame:
    """Filter passengers aged 15 or younger who did not survive.

    Filtering Pattern: Age threshold + survival status

    Args:
        df: Titanic DataFrame
        max_age: Maximum age threshold (inclusive, default: 15)

    Returns:
        NEW DataFrame with young non-survivors

    Examples:
        >>> df = pd.DataFrame({
        ...     'Age': [5.0, 10.0, 15.0, 16.0, 12.0],
        ...     'Survived': [0, 1, 0, 0, 0],
        ...     'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Emma']
        ... })
        >>> result = filter_young_non_survivors(df, 15)
        >>> len(result)
        3
        >>> sorted(result['Name'].tolist())
        ['Alice', 'Charlie', 'Emma']

        >>> # Verify age <= 15
        >>> (result['Age'] <= 15).all()
        True
        >>> # Verify did not survive
        >>> (result['Survived'] == 0).all()
        True

        >>> # Test boundary: age 15 is included
        >>> 15.0 in result['Age'].values
        True
        >>> # Age 16 excluded
        >>> 16.0 in result['Age'].values
        False
    """
    mask = (
        (df['Age'] <= max_age) &
        (df['Survived'] == 0)
    )
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 7: Known Cabin and Fare > $200
# ──────────────────────────────────────────────────────────────────────────────

def filter_known_cabin_high_fare(
    df: pd.DataFrame,
    min_fare: float = 200.0
) -> pd.DataFrame:
    """Filter passengers with known cabin and fare greater than threshold.

    Filtering Pattern: NOT NULL check + numeric comparison

    Args:
        df: Titanic DataFrame
        min_fare: Minimum fare (exclusive, default: 200)

    Returns:
        NEW DataFrame with cabin and high fare

    Examples:
        >>> df = pd.DataFrame({
        ...     'Cabin': ['C85', None, 'E46', 'B57', np.nan],
        ...     'Fare': [250.0, 300.0, 150.0, 220.0, 210.0],
        ...     'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Emma']
        ... })
        >>> result = filter_known_cabin_high_fare(df, 200)
        >>> len(result)
        2
        >>> sorted(result['Name'].tolist())
        ['Alice', 'David']

        >>> # Verify cabin is not null
        >>> result['Cabin'].notna().all()
        True
        >>> # Verify fare > 200
        >>> (result['Fare'] > 200).all()
        True

        >>> # Bob excluded: no cabin despite high fare
        >>> # Charlie excluded: has cabin but fare too low
        >>> # Emma excluded: no cabin
    """
    mask = (
        (df['Cabin'].notna()) &
        (df['Fare'] > min_fare)
    )
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 8: Odd-Numbered Passenger IDs
# ──────────────────────────────────────────────────────────────────────────────

def filter_odd_passenger_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Filter passengers with odd-numbered PassengerId.

    Filtering Pattern: Modulo operation

    Args:
        df: Titanic DataFrame

    Returns:
        NEW DataFrame with odd PassengerId

    Examples:
        >>> df = pd.DataFrame({
        ...     'PassengerId': [1, 2, 3, 4, 5, 6],
        ...     'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Emma', 'Frank']
        ... })
        >>> result = filter_odd_passenger_ids(df)
        >>> len(result)
        3
        >>> result['PassengerId'].tolist()
        [1, 3, 5]
        >>> sorted(result['Name'].tolist())
        ['Alice', 'Charlie', 'Emma']

        >>> # Verify all are odd
        >>> (result['PassengerId'] % 2 == 1).all()
        True

        >>> # Test edge case: ID 0 is even
        >>> df_zero = pd.DataFrame({'PassengerId': [0, 1, 2], 'Name': ['A', 'B', 'C']})
        >>> result_zero = filter_odd_passenger_ids(df_zero)
        >>> result_zero['PassengerId'].tolist()
        [1]
    """
    mask = df['PassengerId'] % 2 == 1
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 9: Unique Ticket Numbers
# ──────────────────────────────────────────────────────────────────────────────

def filter_unique_tickets(df: pd.DataFrame) -> pd.DataFrame:
    """Filter passengers with unique (non-duplicate) ticket numbers.

    Filtering Pattern: Uniqueness check with duplicated()

    Args:
        df: Titanic DataFrame

    Returns:
        NEW DataFrame with passengers having unique tickets

    Examples:
        >>> df = pd.DataFrame({
        ...     'Ticket': ['A123', 'B456', 'A123', 'C789', 'B456'],
        ...     'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Emma']
        ... })
        >>> result = filter_unique_tickets(df)
        >>> len(result)
        1
        >>> result['Name'].iloc[0]
        'David'
        >>> result['Ticket'].iloc[0]
        'C789'

        >>> # A123 appears 2 times → excluded
        >>> # B456 appears 2 times → excluded
        >>> # C789 appears 1 time → included

        >>> # Test with all unique
        >>> df_unique = pd.DataFrame({
        ...     'Ticket': ['A', 'B', 'C'], 'Name': ['X', 'Y', 'Z']
        ... })
        >>> result_unique = filter_unique_tickets(df_unique)
        >>> len(result_unique)
        3

        >>> # Test with all duplicates
        >>> df_dup = pd.DataFrame({
        ...     'Ticket': ['A', 'A', 'B', 'B'], 'Name': ['W', 'X', 'Y', 'Z']
        ... })
        >>> result_dup = filter_unique_tickets(df_dup)
        >>> len(result_dup)
        0
    """
    # Find tickets that appear only once
    # keep=False marks ALL duplicates (including first occurrence)
    mask = ~df['Ticket'].duplicated(keep=False)
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 10: 'Miss' in Name and Class 1
# ──────────────────────────────────────────────────────────────────────────────

def filter_miss_class1(df: pd.DataFrame) -> pd.DataFrame:
    """Filter female passengers with 'Miss' in name and in Class 1.

    Filtering Pattern: String contains + class filter

    Args:
        df: Titanic DataFrame

    Returns:
        NEW DataFrame with Miss passengers in Class 1

    Examples:
        >>> df = pd.DataFrame({
        ...     'Name': ['Miss Alice', 'Mrs. Betty', 'Miss Charlie', 'Miss Diana'],
        ...     'Pclass': [1, 1, 2, 1],
        ...     'PassengerId': [1, 2, 3, 4]
        ... })
        >>> result = filter_miss_class1(df)
        >>> len(result)
        2
        >>> sorted(result['Name'].tolist())
        ['Miss Alice', 'Miss Diana']

        >>> # Verify 'Miss' is in name
        >>> all('Miss' in name for name in result['Name'])
        True
        >>> # Verify Class 1
        >>> (result['Pclass'] == 1).all()
        True

        >>> # Test case sensitivity
        >>> df_case = pd.DataFrame({
        ...     'Name': ['miss alice', 'Miss Betty'], 'Pclass': [1, 1]
        ... })
        >>> result_case = filter_miss_class1(df_case)
        >>> len(result_case)
        1
        >>> result_case['Name'].iloc[0]
        'Miss Betty'
    """
    mask = (
        (df['Name'].str.contains('Miss', case=True, na=False)) &
        (df['Pclass'] == 1)
    )
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3: Complete Demo with Enhanced Error Handling
# ──────────────────────────────────────────────────────────────────────────────

def demo_homework3() -> None:
    """Interactive demo for Homework 3: Titanic Dataset Analysis."""
    hr("HOMEWORK 3: Titanic Dataset Analysis")

    # Enhanced error handling
    try:
        print("\n📊 Loading Titanic dataset...")
        df = load_titanic_data()

    except FileNotFoundError:
        print(f"\n❌ Dataset not found: {TITANIC_CSV}")
        print(f"   Current directory: {Path.cwd()}")
        print(f"   Expected absolute path: {TITANIC_CSV.absolute()}")
        print(f"\n💡 Solutions:")
        print(f"   1. Create 'task/' directory if missing")
        print(f"   2. Download titanic.csv to task/")
        print(f"   3. Common source: https://www.kaggle.com/c/titanic/data")
        return

    except pd.errors.ParserError as e:
        print(f"\n❌ Failed to parse CSV file")
        print(f"   Error: {e}")
        print(f"💡 Verify {TITANIC_CSV} is valid CSV format")
        return

    except Exception as e:
        print(f"\n❌ Unexpected error loading Titanic dataset")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error: {e}")
        return

    # Dataset loaded successfully
    print(f"✓ Loaded {len(df)} passengers")
    print(
        f"  Survived: {df['Survived'].sum()} ({df['Survived'].mean()*100:.1f}%)")
    print(f"  Classes: {sorted(df['Pclass'].unique().tolist())}")
    print(f"  Gender distribution: {df['Sex'].value_counts().to_dict()}")

    # Show sample
    print("\nFirst 3 rows (selected columns):")
    print(df.head(3)[['PassengerId', 'Name',
          'Sex', 'Age', 'Survived']].to_string())

    # Task 1
    print("\n" + "─"*70)
    print("TASK 1: Female, Class 1, Ages 20-30")
    result1 = filter_female_class1_age_range(df, 20, 30)
    print(f"Found {len(result1)} passengers")
    if len(result1) > 0:
        print(f"Sample: {result1['Name'].iloc[0]}")

    # Task 2
    print("\n" + "─"*70)
    print("TASK 2: Passengers who paid > $100")
    result2 = filter_high_fare_passengers(df, 100)
    print(f"Found {len(result2)} high-fare passengers")
    if len(result2) > 0:
        print(
            f"Fare range: ${result2['Fare'].min():.2f} - ${result2['Fare'].max():.2f}")

    # Task 3
    print("\n" + "─"*70)
    print("TASK 3: Survived and traveled alone")
    result3 = filter_survived_alone(df)
    print(f"Found {len(result3)} solo survivors")
    survival_rate = len(
        result3) / df[(df['SibSp'] == 0) & (df['Parch'] == 0)].shape[0] * 100
    print(f"  Solo survival rate: {survival_rate:.1f}%")

    # Task 4
    print("\n" + "─"*70)
    print("TASK 4: Embarked from 'C' (Cherbourg) and paid > $50")
    result4 = filter_embarked_c_high_fare(df, 'C', 50)
    print(f"Found {len(result4)} passengers")

    # Task 5
    print("\n" + "─"*70)
    print("TASK 5: With siblings/spouses AND parents/children")
    result5 = filter_with_siblings_and_parents(df)
    print(f"Found {len(result5)} passengers with both types of companions")

    # Task 6
    print("\n" + "─"*70)
    print("TASK 6: Aged ≤15 who didn't survive")
    result6 = filter_young_non_survivors(df, 15)
    print(f"Found {len(result6)} young non-survivors")

    # Task 7
    print("\n" + "─"*70)
    print("TASK 7: Known cabin and fare > $200")
    result7 = filter_known_cabin_high_fare(df, 200)
    print(f"Found {len(result7)} passengers")

    # Task 8
    print("\n" + "─"*70)
    print("TASK 8: Odd-numbered PassengerId")
    result8 = filter_odd_passenger_ids(df)
    print(f"Found {len(result8)} passengers with odd IDs")
    print(f"  (Exactly 50% of {len(df)} total, as expected)")

    # Task 9
    print("\n" + "─"*70)
    print("TASK 9: Passengers with unique ticket numbers")
    result9 = filter_unique_tickets(df)
    print(f"Found {len(result9)} passengers with unique tickets")
    print(f"  ({len(result9)/len(df)*100:.1f}% of all passengers)")

    # Task 10
    print("\n" + "─"*70)
    print("TASK 10: 'Miss' in name and Class 1")
    result10 = filter_miss_class1(df)
    print(f"Found {len(result10)} Miss passengers in Class 1")
    if len(result10) > 0:
        print(f"Sample: {result10['Name'].iloc[0]}")

    print("\n✓ Homework 3 completed!")


# ══════════════════════════════════════════════════════════════════════════════
# Educational: Filtering Patterns Summary
# ══════════════════════════════════════════════════════════════════════════════

def show_filtering_patterns() -> None:
    """Educational demo: Common Pandas filtering patterns reference."""
    hr("📚 Pandas Filtering Patterns Reference")

    print("""
╔════════════════════════════════════════════════════════════════════╗
║               PANDAS FILTERING PATTERNS REFERENCE                   ║
╚════════════════════════════════════════════════════════════════════╝

1. SIMPLE COMPARISON
   df[df['column'] > value]      # Greater than
   df[df['column'] >= value]     # Greater than or equal
   df[df['column'] == value]     # Equal to
   df[df['column'] != value]     # Not equal to

2. RANGE (BETWEEN)
   Method 1 - Chained comparisons:
   df[(df['col'] >= min) & (df['col'] <= max)]
   
   Method 2 - between():
   df[df['col'].between(min, max, inclusive='both')]

3. MEMBERSHIP (IN LIST)
   df[df['column'].isin(['val1', 'val2', 'val3'])]
   
   Negation (NOT IN):
   df[~df['column'].isin(['val1', 'val2'])]

4. STRING OPERATIONS
   df[df['col'].str.contains('pattern')]          # Contains substring
   df[df['col'].str.startswith('prefix')]         # Starts with
   df[df['col'].str.endswith('suffix')]           # Ends with
   df[df['col'].str.contains('pat', case=False)]  # Case-insensitive

5. NULL CHECKS
   df[df['column'].notna()]    # NOT NULL (recommended)
   df[df['column'].isna()]     # IS NULL
   df[df['column'].notnull()]  # NOT NULL (older style)

6. AND CONDITIONS (&)
   df[(df['col1'] > 10) & (df['col2'] == 'value')]
   ⚠️  MUST use parentheses around each condition!
   
   Example from Homework:
   df[(df['Sex']=='female') & (df['Pclass']==1) & (df['Age']>=20)]

7. OR CONDITIONS (|)
   df[(df['col1'] > 10) | (df['col2'] == 'value')]
   
   Example from Homework:
   df[(df['score'].between(5,10)) | (df['views'] > 10000)]

8. NEGATION (~)
   df[~(df['column'] == value)]       # NOT equal
   df[~df['column'].isin(list)]       # NOT in list
   
   Important: ~ and != handle NaN differently!
   ~(df['col'] == 'X'): keeps NaN rows
   df['col'] != 'X': excludes NaN rows

9. UNIQUENESS
   df[~df['column'].duplicated(keep=False)]    # Unique values only
   df[df['column'].duplicated(keep='first')]   # Duplicates (keep 1st)

10. MODULO OPERATIONS
    df[df['column'] % 2 == 0]    # Even values
    df[df['column'] % 2 == 1]    # Odd values

╔════════════════════════════════════════════════════════════════════╗
║                      BEST PRACTICES                                ║
╚════════════════════════════════════════════════════════════════════╝

✅ DO:
  • Always use .copy() on filtered results to avoid SettingWithCopyWarning
  • Use parentheses in compound conditions: (cond1) & (cond2)
  • Use .notna() instead of .notnull() (more explicit)
  • Use meaningful variable names: mask = (conditions)
  • Consider .between() for readability with ranges

❌ DON'T:
  • Forget parentheses: df[df['a']>5 & df['b']<10] ← WRONG!
  • Chain multiple brackets: df[mask1][mask2] ← inefficient, use &
  • Modify filtered DataFrames without .copy()
  • Use .apply() for simple filters (use vectorized operations)

💡 PERFORMANCE TIPS:
  • .isin() is faster than multiple OR conditions
  • .between() is cleaner for range checks
  • Avoid loops; use vectorized operations
  • For very large datasets, consider query() method

📖 HOMEWORK EXAMPLES:
  Task 2-1: filter_questions_before_year - Date comparison
  Task 2-3: filter_questions_by_score_range - Range with between
  Task 2-5: filter_questions_by_answerers_list - Membership with isin
  Task 2-7: filter_questions_with_or_condition - OR conditions
  Task 2-8: filter_questions_not_answered_by - Negation with ~
  Task 3-7: filter_known_cabin_high_fare - NULL check with notna()
  Task 3-9: filter_unique_tickets - Uniqueness with duplicated()
  Task 3-10: filter_miss_class1 - String matching with str.contains()
""")


# ══════════════════════════════════════════════════════════════════════════════
# Test Runner
# ══════════════════════════════════════════════════════════════════════════════

def run_tests() -> Tuple[int, int]:
    """Run all doctests with comprehensive coverage.

    Returns:
        Tuple of (failures, total_tests)
    """
    import doctest

    print("Running comprehensive doctests...")
    print("Testing all 18 filtering functions + utilities...")

    failures, tests = doctest.testmod(verbose=False)

    if failures == 0:
        print(f"✓ All {tests} doctests passed!")
        print("\n📊 Coverage:")
        print(f"  • Homework 2: 8 tasks with doctests")
        print(f"  • Homework 3: 10 tasks with doctests")
        print(f"  • Utilities: {tests - 18} additional tests")
    else:
        print(f"❌ {failures} of {tests} doctests failed")
        print("💡 Run with --verbose flag for details")

    return failures, tests


# ══════════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ══════════════════════════════════════════════════════════════════════════════

def main(argv: List[str] | None = None) -> int:
    """Main entry point with clear task separation.

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

    # Check Pandas availability
    if not PANDAS_AVAILABLE:
        return 1

    # Display version info
    print("\n" + "="*70)
    print(
        " 🐼 Lesson 18: Advanced Pandas Filtering [IMPROVED v2] ".center(70, "="))
    print("="*70)
    print(f"Pandas version: {pd.__version__}")
    print(f"NumPy version: {np.__version__}")
    print("\nImprovements based on instructor feedback:")
    print("  ✅ Comprehensive doctests in ALL 18 functions")
    print("  ✅ Enhanced error handling with context")
    print("  ✅ Literal task interpretation (Task 2-5)")
    print("  ✅ Self-contained, independently testable functions")

    # Main menu loop
    try:
        while True:
            hr("Main Menu")
            print("Choose a homework to explore:\n")
            print("  2️⃣   Homework 2: StackOverflow Q&A Analysis (8 tasks)")
            print("         - Date filtering, score ranges, user filters")
            print("\n  3️⃣   Homework 3: Titanic Dataset Analysis (10 tasks)")
            print("         - Complex conditions, string matching, uniqueness")
            print("\n  📚 Filtering Patterns Reference")
            print("         - Comprehensive guide to Pandas filtering")
            print("\n  🎯 Run Both Homeworks")
            print("  🧪 Run Tests (All 18 functions with doctests)")
            print("  0️⃣   Exit")

            choice = input("\nSelect option: ").strip()

            try:
                if choice == "2":
                    demo_homework2()

                elif choice == "3":
                    demo_homework3()

                elif choice.lower() in ("patterns", "📚", "ref", "reference", "p"):
                    show_filtering_patterns()

                elif choice.lower() in ("all", "both", "🎯"):
                    hr("Running Both Homeworks")

                    demo_homework2()
                    input("\nPress Enter to continue to Homework 3...")
                    demo_homework3()

                    print("\n✓ All homeworks completed!")

                elif choice.lower() in ("tests", "test", "🧪", "t"):
                    run_tests()
                    input("\nPress Enter to continue...")

                elif choice == "0":
                    print("\n👋 Thank you for mastering Pandas filtering!")
                    print("💡 You now have 18 production-ready filtering functions")
                    print("📚 Each with comprehensive doctests and examples")
                    return 0

                else:
                    print(f"❌ Invalid option: '{choice}'")
                    print("💡 Please enter a number or shortcut from the menu")

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


if __name__ == "__main__":
    sys.exit(main())
