#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lesson17.py — Pandas DataFrame Operations (Lesson 17)

Homework Structure:
    Homework 1: Basic DataFrame operations (rename, select, add columns)
    Homework 2: Sales and expenses analysis (max, min, average)
    Homework 3: Category-wise expense analysis with index operations

Design Principles (from L13-L16 feedback):
    - Modular structure with clear task demarcation
    - Core logic separate from CLI demos
    - Balance between simplicity and sophistication
    - Educational value without overwhelming complexity
    - Production practices without overengineering

Dependencies:
    pip install pandas numpy

Run tests:
    python lesson17.py --test

Interactive CLI:
    python lesson17.py
"""
from __future__ import annotations

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
# Utility Functions
# ──────────────────────────────────────────────────────────────────────────────

def hr(title: str = "", width: int = 70) -> None:
    """Print horizontal rule with optional title."""
    print("\n" + "=" * width)
    if title:
        print(title)
        print("-" * width)


def print_dataframe(df: pd.DataFrame, title: str = "DataFrame") -> None:
    """Print DataFrame with nice formatting.

    Args:
        df: Pandas DataFrame to display
        title: Title for the output
    """
    print(f"\n{title}:")
    print(df.to_string(index=True))
    print(f"\nShape: {df.shape} (rows, columns)")


# ══════════════════════════════════════════════════════════════════════════════
# HOMEWORK 1: Basic DataFrame Operations
# ══════════════════════════════════════════════════════════════════════════════

def create_people_dataframe() -> pd.DataFrame:
    """Create the initial DataFrame from Homework 1 specification.

    Returns:
        DataFrame with First Name, Age, and City columns

    Example:
        >>> df = create_people_dataframe()
        >>> df.shape
        (4, 3)
        >>> 'First Name' in df.columns
        True
    """
    data = {
        'First Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Age': [25, 30, 35, 40],
        'City': ['New York', 'San Francisco', 'Los Angeles', 'Chicago']
    }
    return pd.DataFrame(data)


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 1, TASK 1: Rename Columns
# ──────────────────────────────────────────────────────────────────────────────

def rename_columns_snake_case(df: pd.DataFrame) -> pd.DataFrame:
    """Rename DataFrame columns to snake_case.

    Converts column names like "First Name" to "first_name" and "Age" to "age".

    Args:
        df: DataFrame with original column names

    Returns:
        DataFrame with renamed columns (new copy)

    Example:
        >>> df = pd.DataFrame({'First Name': ['Alice'], 'Age': [25]})
        >>> renamed = rename_columns_snake_case(df)
        >>> list(renamed.columns)
        ['first_name', 'age']
    """
    # Method 1: Using rename with lambda (most flexible)
    # Convert to lowercase and replace spaces with underscores
    return df.rename(columns=lambda col: col.lower().replace(' ', '_'))


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 1, TASK 2: Print First 3 Rows
# ──────────────────────────────────────────────────────────────────────────────

def get_first_n_rows(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """Get first n rows of DataFrame.

    Args:
        df: Input DataFrame
        n: Number of rows to return (default: 3)

    Returns:
        DataFrame with first n rows

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3, 4]})
        >>> result = get_first_n_rows(df, 2)
        >>> len(result)
        2
    """
    return df.head(n)


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 1, TASK 3: Mean Age
# ──────────────────────────────────────────────────────────────────────────────

def calculate_mean_age(df: pd.DataFrame, age_column: str = 'age') -> float:
    """Calculate mean age from DataFrame.

    Args:
        df: DataFrame containing age data
        age_column: Name of the age column (default: 'age')

    Returns:
        Mean age as float

    Raises:
        KeyError: If age column doesn't exist

    Example:
        >>> df = pd.DataFrame({'age': [25, 30, 35, 40]})
        >>> calculate_mean_age(df)
        32.5
    """
    if age_column not in df.columns:
        raise KeyError(
            f"❌ Column '{age_column}' not found\n"
            f"   Available columns: {list(df.columns)}\n"
            f"💡 Tip: Check column name spelling"
        )

    return df[age_column].mean()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 1, TASK 4: Select Name and City Columns
# ──────────────────────────────────────────────────────────────────────────────

def select_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Select specific columns from DataFrame.

    Args:
        df: Input DataFrame
        columns: List of column names to select

    Returns:
        DataFrame with only selected columns

    Example:
        >>> df = pd.DataFrame({'A': [1], 'B': [2], 'C': [3]})
        >>> result = select_columns(df, ['A', 'C'])
        >>> list(result.columns)
        ['A', 'C']
    """
    missing_cols = set(columns) - set(df.columns)
    if missing_cols:
        raise KeyError(
            f"❌ Columns not found: {missing_cols}\n"
            f"   Available: {list(df.columns)}\n"
            f"💡 Tip: Check column names"
        )

    return df[columns]


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 1, TASK 5: Add Salary Column
# ──────────────────────────────────────────────────────────────────────────────

def add_random_salary_column(
    df: pd.DataFrame,
    min_salary: int = 50000,
    max_salary: int = 120000,
    seed: int | None = None
) -> pd.DataFrame:
    """Add a 'Salary' column with random values.

    Args:
        df: Input DataFrame
        min_salary: Minimum salary value (default: 50000)
        max_salary: Maximum salary value (default: 120000)
        seed: Random seed for reproducibility (default: None)

    Returns:
        DataFrame with added 'Salary' column (modifies in place)

    Example:
        >>> df = pd.DataFrame({'name': ['Alice', 'Bob']})
        >>> result = add_random_salary_column(df, 50000, 60000, seed=42)
        >>> 'Salary' in result.columns
        True
        >>> (result['Salary'] >= 50000).all() and (result['Salary'] <= 60000).all()
        True
    """
    if seed is not None:
        np.random.seed(seed)

    # Generate random salaries (rounded to nearest 100)
    n_rows = len(df)
    salaries = np.random.randint(min_salary, max_salary + 1, size=n_rows)

    # Round to nearest 100 for realistic salaries
    df['Salary'] = (salaries // 100) * 100

    return df


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 1, TASK 6: Summary Statistics
# ──────────────────────────────────────────────────────────────────────────────

def get_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Get summary statistics of DataFrame.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with summary statistics (count, mean, std, min, max, etc.)

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        >>> stats = get_summary_statistics(df)
        >>> 'mean' in stats.index
        True
    """
    return df.describe()


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 1: Complete Demo
# ──────────────────────────────────────────────────────────────────────────────

def demo_homework1() -> None:
    """Interactive demo for Homework 1: Basic DataFrame Operations."""
    hr("HOMEWORK 1: Basic DataFrame Operations")

    # Create initial DataFrame
    print("\n📊 Creating initial DataFrame...")
    df = create_people_dataframe()
    print_dataframe(df, "Original DataFrame")

    # Task 1: Rename columns
    print("\n" + "─"*70)
    print("TASK 1: Rename columns to snake_case")
    df = rename_columns_snake_case(df)
    print_dataframe(df, "After renaming columns")

    # Task 2: First 3 rows
    print("\n" + "─"*70)
    print("TASK 2: Print first 3 rows")
    first_3 = get_first_n_rows(df, 3)
    print_dataframe(first_3, "First 3 Rows")

    # Task 3: Mean age
    print("\n" + "─"*70)
    print("TASK 3: Calculate mean age")
    mean_age = calculate_mean_age(df)
    print(f"Mean age: {mean_age:.1f} years")

    # Task 4: Select Name and City
    print("\n" + "─"*70)
    print("TASK 4: Select 'first_name' and 'city' columns")
    selected = select_columns(df, ['first_name', 'city'])
    print_dataframe(selected, "Name and City Only")

    # Task 5: Add Salary column
    print("\n" + "─"*70)
    print("TASK 5: Add 'Salary' column with random values")
    df = add_random_salary_column(df, seed=42)  # Seed for reproducibility
    print_dataframe(df, "With Salary Column")

    # Task 6: Summary statistics
    print("\n" + "─"*70)
    print("TASK 6: Display summary statistics")
    stats = get_summary_statistics(df)
    print("\nSummary Statistics:")
    print(stats.to_string())

    print("\n✓ Homework 1 completed!")


# ══════════════════════════════════════════════════════════════════════════════
# HOMEWORK 2: Sales and Expenses Analysis
# ══════════════════════════════════════════════════════════════════════════════

def create_sales_expenses_dataframe() -> pd.DataFrame:
    """Create sales and expenses DataFrame from Homework 2 specification.

    Returns:
        DataFrame with Month, Sales, and Expenses columns

    Example:
        >>> df = create_sales_expenses_dataframe()
        >>> df.shape
        (4, 3)
        >>> list(df.columns)
        ['Month', 'Sales', 'Expenses']
    """
    data = {
        'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
        'Sales': [5000, 6000, 7500, 8000],
        'Expenses': [3000, 3500, 4000, 4500]
    }
    return pd.DataFrame(data)


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2, TASK 1: Create DataFrame (already implemented above)
# ──────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2, TASK 2: Maximum Sales and Expenses
# ──────────────────────────────────────────────────────────────────────────────

def calculate_max_values(df: pd.DataFrame, columns: List[str]) -> Dict[str, float]:
    """Calculate maximum values for specified columns.

    Args:
        df: Input DataFrame
        columns: List of column names to calculate max for

    Returns:
        Dictionary with column names as keys and max values as values

    Example:
        >>> df = pd.DataFrame({'Sales': [100, 200], 'Expenses': [50, 75]})
        >>> result = calculate_max_values(df, ['Sales', 'Expenses'])
        >>> result['Sales']
        200
    """
    return {col: df[col].max() for col in columns}


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2, TASK 3: Minimum Sales and Expenses
# ──────────────────────────────────────────────────────────────────────────────

def calculate_min_values(df: pd.DataFrame, columns: List[str]) -> Dict[str, float]:
    """Calculate minimum values for specified columns.

    Args:
        df: Input DataFrame
        columns: List of column names to calculate min for

    Returns:
        Dictionary with column names as keys and min values as values

    Example:
        >>> df = pd.DataFrame({'Sales': [100, 200], 'Expenses': [50, 75]})
        >>> result = calculate_min_values(df, ['Sales', 'Expenses'])
        >>> result['Sales']
        100
    """
    return {col: df[col].min() for col in columns}


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2, TASK 4: Average Sales and Expenses
# ──────────────────────────────────────────────────────────────────────────────

def calculate_avg_values(df: pd.DataFrame, columns: List[str]) -> Dict[str, float]:
    """Calculate average values for specified columns.

    Args:
        df: Input DataFrame
        columns: List of column names to calculate average for

    Returns:
        Dictionary with column names as keys and average values as values

    Example:
        >>> df = pd.DataFrame({'Sales': [100, 200], 'Expenses': [50, 75]})
        >>> result = calculate_avg_values(df, ['Sales', 'Expenses'])
        >>> result['Sales']
        150.0
    """
    return {col: df[col].mean() for col in columns}


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 2: Complete Demo
# ──────────────────────────────────────────────────────────────────────────────

def demo_homework2() -> None:
    """Interactive demo for Homework 2: Sales and Expenses Analysis."""
    hr("HOMEWORK 2: Sales and Expenses Analysis")

    # Task 1: Create DataFrame
    print("\n📊 Creating sales_and_expenses DataFrame...")
    df = create_sales_expenses_dataframe()
    print_dataframe(df, "Sales and Expenses Data")

    # Columns to analyze
    analysis_columns = ['Sales', 'Expenses']

    # Task 2: Maximum values
    print("\n" + "─"*70)
    print("TASK 2: Maximum sales and expenses")
    max_values = calculate_max_values(df, analysis_columns)
    print(f"Maximum Sales:    ${max_values['Sales']:,.0f}")
    print(f"Maximum Expenses: ${max_values['Expenses']:,.0f}")

    # Task 3: Minimum values
    print("\n" + "─"*70)
    print("TASK 3: Minimum sales and expenses")
    min_values = calculate_min_values(df, analysis_columns)
    print(f"Minimum Sales:    ${min_values['Sales']:,.0f}")
    print(f"Minimum Expenses: ${min_values['Expenses']:,.0f}")

    # Task 4: Average values
    print("\n" + "─"*70)
    print("TASK 4: Average sales and expenses")
    avg_values = calculate_avg_values(df, analysis_columns)
    print(f"Average Sales:    ${avg_values['Sales']:,.2f}")
    print(f"Average Expenses: ${avg_values['Expenses']:,.2f}")

    # Bonus: Summary table
    print("\n" + "─"*70)
    print("📊 Summary Statistics Table")
    summary = pd.DataFrame({
        'Sales': [min_values['Sales'], max_values['Sales'], avg_values['Sales']],
        'Expenses': [min_values['Expenses'], max_values['Expenses'], avg_values['Expenses']]
    }, index=['Minimum', 'Maximum', 'Average'])
    print(summary.to_string())

    print("\n✓ Homework 2 completed!")


# ══════════════════════════════════════════════════════════════════════════════
# HOMEWORK 3: Category-wise Expense Analysis with Index Operations
# ══════════════════════════════════════════════════════════════════════════════

def create_expenses_dataframe() -> pd.DataFrame:
    """Create expenses DataFrame from Homework 3 specification.

    Returns:
        DataFrame with Category and monthly expense columns

    Example:
        >>> df = create_expenses_dataframe()
        >>> df.shape
        (4, 5)
        >>> 'Category' in df.columns
        True
    """
    data = {
        'Category': ['Rent', 'Utilities', 'Groceries', 'Entertainment'],
        'January': [1200, 200, 300, 150],
        'February': [1300, 220, 320, 160],
        'March': [1400, 240, 330, 170],
        'April': [1500, 250, 350, 180]
    }
    return pd.DataFrame(data)


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 1: Create DataFrame with Category as Index
# ──────────────────────────────────────────────────────────────────────────────

def set_category_as_index(df: pd.DataFrame) -> pd.DataFrame:
    """Set 'Category' column as the DataFrame index.

    This demonstrates the .set_index() method as specified in the homework.

    Args:
        df: DataFrame with 'Category' column

    Returns:
        New DataFrame with 'Category' as index

    Example:
        >>> df = pd.DataFrame({'Category': ['Rent', 'Utilities'], 'Jan': [1200, 200]})
        >>> indexed = set_category_as_index(df)
        >>> indexed.index.name
        'Category'
        >>> 'Category' in indexed.columns
        False
    """
    return df.set_index('Category')


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 2: Maximum Expense per Category
# ──────────────────────────────────────────────────────────────────────────────

def calculate_max_per_category(df: pd.DataFrame) -> pd.Series:
    """Calculate maximum expense for each category across all months.

    Args:
        df: DataFrame with categories as index and months as columns

    Returns:
        Series with maximum value for each category

    Example:
        >>> df = pd.DataFrame({'Jan': [100, 200], 'Feb': [150, 180]}, 
        ...                   index=['Rent', 'Utilities'])
        >>> result = calculate_max_per_category(df)
        >>> result['Rent']
        150
    """
    # axis=1 means calculate max across columns (horizontal)
    return df.max(axis=1)


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 3: Minimum Expense per Category
# ──────────────────────────────────────────────────────────────────────────────

def calculate_min_per_category(df: pd.DataFrame) -> pd.Series:
    """Calculate minimum expense for each category across all months.

    Args:
        df: DataFrame with categories as index and months as columns

    Returns:
        Series with minimum value for each category

    Example:
        >>> df = pd.DataFrame({'Jan': [100, 200], 'Feb': [150, 180]},
        ...                   index=['Rent', 'Utilities'])
        >>> result = calculate_min_per_category(df)
        >>> result['Rent']
        100
    """
    return df.min(axis=1)


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3, TASK 4: Average Expense per Category
# ──────────────────────────────────────────────────────────────────────────────

def calculate_avg_per_category(df: pd.DataFrame) -> pd.Series:
    """Calculate average expense for each category across all months.

    Args:
        df: DataFrame with categories as index and months as columns

    Returns:
        Series with average value for each category

    Example:
        >>> df = pd.DataFrame({'Jan': [100, 200], 'Feb': [150, 180]},
        ...                   index=['Rent', 'Utilities'])
        >>> result = calculate_avg_per_category(df)
        >>> result['Rent']
        125.0
    """
    return df.mean(axis=1)


# ──────────────────────────────────────────────────────────────────────────────
# HOMEWORK 3: Complete Demo
# ──────────────────────────────────────────────────────────────────────────────

def demo_homework3() -> None:
    """Interactive demo for Homework 3: Category-wise Expense Analysis."""
    hr("HOMEWORK 3: Category-wise Expense Analysis")

    # Task 1: Create DataFrame
    print("\n📊 Creating expenses DataFrame...")
    df = create_expenses_dataframe()
    print_dataframe(df, "Original DataFrame")

    # Set Category as index (as instructed in homework)
    print("\n" + "─"*70)
    print("Setting 'Category' as index using .set_index('Category')...")
    df_indexed = set_category_as_index(df)
    print_dataframe(df_indexed, "With Category as Index")

    # Task 2: Maximum per category
    print("\n" + "─"*70)
    print("TASK 2: Maximum expense for each category")
    max_per_category = calculate_max_per_category(df_indexed)
    print("\nMaximum expenses:")
    for category, value in max_per_category.items():
        print(f"  {category:15s}: ${value:,.0f}")

    # Task 3: Minimum per category
    print("\n" + "─"*70)
    print("TASK 3: Minimum expense for each category")
    min_per_category = calculate_min_per_category(df_indexed)
    print("\nMinimum expenses:")
    for category, value in min_per_category.items():
        print(f"  {category:15s}: ${value:,.0f}")

    # Task 4: Average per category
    print("\n" + "─"*70)
    print("TASK 4: Average expense for each category")
    avg_per_category = calculate_avg_per_category(df_indexed)
    print("\nAverage expenses:")
    for category, value in avg_per_category.items():
        print(f"  {category:15s}: ${value:,.2f}")

    # Bonus: Summary DataFrame
    print("\n" + "─"*70)
    print("📊 Complete Summary Statistics by Category")
    summary = pd.DataFrame({
        'Minimum': min_per_category,
        'Maximum': max_per_category,
        'Average': avg_per_category
    })
    print(summary.to_string())

    # Educational note about axis parameter
    print("\n" + "─"*70)
    print("📚 Understanding axis parameter:")
    print("  • axis=0: operate down rows (column-wise aggregation)")
    print("  • axis=1: operate across columns (row-wise aggregation)")
    print("  • In this homework, we used axis=1 to find stats across months")

    print("\n✓ Homework 3 completed!")


# ══════════════════════════════════════════════════════════════════════════════
# Test Runner
# ══════════════════════════════════════════════════════════════════════════════

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
    print(" 🐼 Lesson 17: Pandas DataFrame Operations ".center(70, "="))
    print("="*70)
    print(f"Pandas version: {pd.__version__}")
    print(f"NumPy version: {np.__version__}")

    # Main menu loop
    try:
        while True:
            hr("Main Menu")
            print("Choose a homework to explore:\n")
            print("  1️⃣   Homework 1: Basic DataFrame Operations")
            print("         (rename, select, add columns, statistics)")
            print("\n  2️⃣   Homework 2: Sales and Expenses Analysis")
            print("         (max, min, average calculations)")
            print("\n  3️⃣   Homework 3: Category-wise Expense Analysis")
            print("         (set_index, row-wise aggregations)")
            print("\n  🎯 Run All Homeworks")
            print("  🧪 Run Tests")
            print("  0️⃣   Exit")

            choice = input("\nSelect option: ").strip()

            try:
                if choice == "1":
                    demo_homework1()

                elif choice == "2":
                    demo_homework2()

                elif choice == "3":
                    demo_homework3()

                elif choice.lower() in ("all", "🎯"):
                    # Run all homeworks in sequence
                    hr("Running All Homeworks")
                    print("Executing all 3 homeworks...\n")

                    homeworks = [demo_homework1,
                                 demo_homework2, demo_homework3]

                    for i, hw in enumerate(homeworks, 1):
                        try:
                            hw()
                            if i < len(homeworks):
                                input(
                                    f"\nPress Enter to continue to Homework {i+1}...")
                        except Exception as e:
                            print(f"❌ Error in Homework {i}: {e}")
                            import traceback
                            traceback.print_exc()
                            break

                    print("\n✓ All homeworks completed!")

                elif choice.lower() in ("tests", "test", "🧪", "t"):
                    run_tests()
                    input("\nPress Enter to continue...")

                elif choice == "0":
                    print("\n👋 Thank you for exploring Pandas!")
                    print("💡 Pandas is essential for data analysis in Python")
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


if __name__ == "__main__":
    sys.exit(main())
