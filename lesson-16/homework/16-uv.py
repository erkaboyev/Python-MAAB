#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lesson16.py — NumPy Array Operations (Lesson 16)

Tasks:
    1. Convert list to 1D array
    2. Create 3x3 matrix with values 2-10
    3. Null vector (size 10) & update sixth value
    4. Array from 12 to 38
    5. Convert array to float type
    6. Celsius ↔ Fahrenheit conversion
    7. Append values to array
    8. Statistical functions (mean, median, std)
    9. Find min/max in 10x10 array
    10. Create 3x3x3 array with random values

Design Principles (from L1-L15 feedback):
    - Educational error messages with emoji and context (L8-L15)
    - Type hints throughout (L3-L15)
    - Comprehensive doctests (L4-L15)
    - Inline comments for complex operations (L13)
    - Production-ready validation (L9-L15)
    - User-friendly CLI with progress indicators (L9-L15)

Dependencies:
    pip install numpy

Run tests:
    python lesson16.py --test

Interactive CLI:
    python lesson16.py
"""
from __future__ import annotations

from typing import Any, List, Tuple, Union
from pathlib import Path
import doctest
import sys

# Third-party imports with graceful fallback
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("❌ NumPy not installed")
    print("💡 Install with: pip install numpy")
    sys.exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# Utility Functions: Pretty printing, input validation
# ──────────────────────────────────────────────────────────────────────────────

def hr(title: str = "", width: int = 70) -> None:
    """Print horizontal rule with optional title.

    Following L1-L15 feedback: consistent utility functions.

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


def confirm(prompt: str = "Continue?") -> bool:
    """Ask for yes/no confirmation."""
    response = input(f"{prompt} (y/n): ").strip().lower()
    return response in ('y', 'yes')


def read_float_list(prompt: str) -> List[float]:
    """Read a list of floats from user input.

    Following L8-L15 feedback: educational error handling.
    """
    while True:
        try:
            values_str = input(prompt).strip()
            if not values_str:
                print("❌ Input cannot be empty")
                print("💡 Example: 1.5, 2.3, 4.0")
                continue

            # Parse comma-separated values
            values = [float(x.strip()) for x in values_str.split(',')]

            if not values:
                print("❌ No valid numbers found")
                continue

            return values

        except ValueError as e:
            print(f"❌ Invalid number format: {e}")
            print("💡 Enter numbers separated by commas (e.g., 1.5, 2.3, 4.0)")
        except KeyboardInterrupt:
            print("\n⚠ Input cancelled by user")
            raise


def print_array(
    arr: np.ndarray,
    title: str = "Array",
    *,
    max_display: int = 1000
) -> None:
    """Print NumPy array with nice formatting.

    Following L13-L15 feedback: user-friendly display with context.

    Args:
        arr: NumPy array to display
        title: Title for the output
        max_display: Maximum elements to display (prevents console spam)
    """
    print(f"\n{title}:")
    print(f"  Shape: {arr.shape}")
    print(f"  Dtype: {arr.dtype}")
    print(f"  Size: {arr.size} elements")

    if arr.size <= max_display:
        # Set print options for better readability
        with np.printoptions(precision=2, suppress=True, linewidth=70):
            print(f"  Values:\n{arr}")
    else:
        print(f"  (Too large to display: {arr.size} elements)")
        print(f"  First 10: {arr.flat[:10]}")
        print(f"  Last 10: {arr.flat[-10:]}")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 1: Convert List to 1D Array
# ──────────────────────────────────────────────────────────────────────────────

def list_to_array(values: List[float]) -> np.ndarray:
    """Convert Python list to 1D NumPy array.

    Args:
        values: List of numeric values

    Returns:
        1D NumPy array

    Raises:
        ValueError: If list is empty or contains non-numeric values

    Example:
        >>> arr = list_to_array([12.23, 13.32, 100, 36.32])
        >>> arr.shape
        (4,)
        >>> arr.dtype
        dtype('float64')
        >>> round(arr[0], 2)
        12.23
    """
    if not values:
        raise ValueError(
            "❌ Cannot create array from empty list\n"
            "💡 Tip: Provide at least one numeric value"
        )

    try:
        # Convert to NumPy array (automatically infers dtype)
        arr = np.array(values)

        # Validate it's numeric
        if not np.issubdtype(arr.dtype, np.number):
            raise ValueError(
                f"❌ Array contains non-numeric values\n"
                f"   Dtype: {arr.dtype}\n"
                f"💡 Tip: Ensure all values are numbers"
            )

        return arr

    except Exception as e:
        raise ValueError(
            f"❌ Failed to convert list to array: {e}\n"
            f"💡 Tip: Check that all values are valid numbers"
        ) from e


def demo_task1() -> None:
    """Interactive demo for Task 1: List to 1D Array.

    Assignment: "Write a NumPy program to convert a list of numeric values
    into a one-dimensional NumPy array."
    """
    hr("Task 1: Convert List to 1D NumPy Array")

    # Default example from assignment
    default_list = [12.23, 13.32, 100, 36.32]

    print("Expected Output:")
    print(f"Original List: {default_list}")

    # Convert to array
    arr = list_to_array(default_list)

    print(f"One-dimensional NumPy array: {arr}")

    # Interactive option
    if confirm("\nTry with your own values?"):
        try:
            custom_values = read_float_list(
                "Enter numbers (comma-separated): ")
            custom_arr = list_to_array(custom_values)

            print(f"\n✓ Conversion successful!")
            print(f"Original List: {custom_values}")
            print_array(custom_arr, "One-dimensional NumPy array")

        except Exception as e:
            print(f"❌ Error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 2: Create 3x3 Matrix with values 2-10
# ──────────────────────────────────────────────────────────────────────────────

def create_3x3_matrix() -> np.ndarray:
    """Create 3x3 matrix with values from 2 to 10.

    Assignment: "Write a NumPy program to create a 3x3 matrix with values
    ranging from 2 to 10."

    Returns:
        3x3 NumPy array with values 2-10

    Example:
        >>> matrix = create_3x3_matrix()
        >>> matrix.shape
        (3, 3)
        >>> matrix[0, 0]
        2
        >>> matrix[2, 2]
        10
    """
    # Method 1: Using arange + reshape
    # arange(2, 11) creates [2, 3, 4, ..., 10]
    # reshape(3, 3) converts to 3x3 matrix
    values = np.arange(2, 11)  # 2 to 10 inclusive (11 is exclusive)
    matrix = values.reshape(3, 3)

    return matrix


def demo_task2() -> None:
    """Interactive demo for Task 2: Create 3x3 Matrix."""
    hr("Task 2: Create 3x3 Matrix (Values 2-10)")

    print("Creating 3x3 matrix with values ranging from 2 to 10...\n")

    # Create matrix
    matrix = create_3x3_matrix()

    print("Expected Output:")
    print("[[ 2  3  4]")
    print(" [ 5  6  7]")
    print(" [ 8  9 10]]")

    print("\nActual Output:")
    print(matrix)

    # Educational explanation
    print("\n📚 How it works:")
    print("  1. np.arange(2, 11) creates array [2, 3, ..., 10]")
    print("  2. reshape(3, 3) converts 9 elements into 3x3 matrix")
    print("  3. Values fill row-by-row (row-major order)")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 3: Null Vector & Update Sixth Value
# ──────────────────────────────────────────────────────────────────────────────

def create_null_vector(size: int = 10) -> np.ndarray:
    """Create null vector (all zeros) of specified size.

    Args:
        size: Length of vector (default: 10)

    Returns:
        1D array of zeros

    Example:
        >>> vec = create_null_vector(5)
        >>> vec.shape
        (5,)
        >>> np.all(vec == 0)
        True
    """
    if size <= 0:
        raise ValueError(
            f"❌ Invalid size: {size}\n"
            f"💡 Tip: Size must be positive integer"
        )

    return np.zeros(size)


def update_vector_element(
    vec: np.ndarray,
    index: int,
    value: float
) -> np.ndarray:
    """Update element at specified index.

    Note: NumPy arrays are mutable, so this modifies the array in-place.
    However, we return the array for convenience.

    Args:
        vec: NumPy array to update
        index: Index to update (0-based)
        value: New value

    Returns:
        Updated array (same object as input)

    Example:
        >>> vec = np.zeros(5)
        >>> updated = update_vector_element(vec, 2, 42.0)
        >>> updated[2]
        42.0
    """
    if index < 0 or index >= len(vec):
        raise IndexError(
            f"❌ Index out of range: {index}\n"
            f"   Valid range: 0 to {len(vec) - 1}\n"
            f"💡 Tip: Remember Python uses 0-based indexing"
        )

    vec[index] = value
    return vec


def demo_task3() -> None:
    """Interactive demo for Task 3: Null Vector & Update.

    Assignment: "Write a NumPy program to create a null vector of size 10
    and update the sixth value to 11."
    """
    hr("Task 3: Null Vector (Size 10) & Update Sixth Value")

    # Create null vector
    vec = create_null_vector(10)

    print("Original null vector:")
    print(vec)

    print("\nUpdate sixth value to 11")
    print("💡 Note: In Python, 'sixth value' means index 5 (0-based indexing)")

    # Update sixth value (index 5 in 0-based indexing)
    # Assignment says "sixth value" which could mean:
    # - index 5 (sixth element in 0-based)
    # - index 6 (position 6 in 1-based thinking)
    # Based on expected output showing 0s at positions 0-5 and 11 at position 6,
    # it appears they mean index 6 (position 7 in 1-based counting)
    update_vector_element(vec, 6, 11)

    print("\nUpdated vector:")
    print(vec)

    # Educational explanation
    print("\n📚 Indexing clarification:")
    print("  - Python uses 0-based indexing")
    print("  - 'Sixth value' could mean:")
    print("    • Index 5 (sixth element)")
    print("    • Index 6 (position 6 in output)")
    print("  - Based on expected output, we use index 6")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 4: Array from 12 to 38
# ──────────────────────────────────────────────────────────────────────────────

def create_range_array(start: int, end: int) -> np.ndarray:
    """Create array with values from start to end (exclusive).

    Args:
        start: Start value (inclusive)
        end: End value (exclusive)

    Returns:
        1D array with sequential values

    Example:
        >>> arr = create_range_array(12, 15)
        >>> list(arr)
        [12, 13, 14]
    """
    if start >= end:
        raise ValueError(
            f"❌ Invalid range: start ({start}) >= end ({end})\n"
            f"💡 Tip: Start must be less than end"
        )

    return np.arange(start, end)


def demo_task4() -> None:
    """Interactive demo for Task 4: Array from 12 to 38.

    Assignment: "Write a NumPy program to create an array with values
    ranging from 12 to 38."
    """
    hr("Task 4: Create Array from 12 to 38")

    # Note: Expected output shows [12...37], so end should be 38 (exclusive)
    arr = create_range_array(12, 38)

    print("Expected Output:")
    print("[12 13 14 15 16 17 18 19 20 21 22 23 24")
    print(" 25 26 27 28 29 30 31 32 33 34 35 36 37]")

    print("\nActual Output:")
    print(arr)

    print(f"\n✓ Array created with {len(arr)} elements")
    print(f"  First value: {arr[0]}")
    print(f"  Last value: {arr[-1]}")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 5: Convert Array to Float Type
# ──────────────────────────────────────────────────────────────────────────────

def convert_to_float(arr: np.ndarray) -> np.ndarray:
    """Convert array to floating-point type.

    Args:
        arr: Input array (any numeric type)

    Returns:
        Array with float64 dtype

    Example:
        >>> int_arr = np.array([1, 2, 3])
        >>> float_arr = convert_to_float(int_arr)
        >>> float_arr.dtype
        dtype('float64')
        >>> float_arr[0]
        1.0
    """
    try:
        # astype() creates a copy with new dtype
        return arr.astype(np.float64)
    except Exception as e:
        raise ValueError(
            f"❌ Failed to convert to float: {e}\n"
            f"   Input dtype: {arr.dtype}\n"
            f"💡 Tip: Ensure array contains convertible values"
        ) from e


def demo_task5() -> None:
    """Interactive demo for Task 5: Convert to Float Type.

    Assignment: "Write a NumPy program to convert an array to a floating type."
    """
    hr("Task 5: Convert Array to Float Type")

    # Sample array (integers)
    original = np.array([1, 2, 3, 4])

    print("Original array:")
    print(f"  Values: {original}")
    print(f"  Dtype: {original.dtype}")

    # Convert to float
    float_array = convert_to_float(original)

    print("\nConverted to float:")
    print(f"  Values: {float_array}")
    print(f"  Dtype: {float_array.dtype}")

    # Show the difference
    print("\n📚 Key differences:")
    print(f"  Integer: 1 (type: {type(original[0]).__name__})")
    print(f"  Float:   1.0 (type: {type(float_array[0]).__name__})")
    print("\n💡 Floating-point allows decimal values and scientific notation")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 6: Celsius ↔ Fahrenheit Conversion
# ──────────────────────────────────────────────────────────────────────────────

def celsius_to_fahrenheit(celsius: np.ndarray) -> np.ndarray:
    """Convert Celsius to Fahrenheit.

    Formula: F = (C × 9/5) + 32

    Args:
        celsius: Array of temperatures in Celsius

    Returns:
        Array of temperatures in Fahrenheit

    Example:
        >>> c = np.array([0, 100])
        >>> f = celsius_to_fahrenheit(c)
        >>> f[0], f[1]
        (32.0, 212.0)
    """
    # Vectorized operation (applies to all elements at once)
    return (celsius * 9/5) + 32


def fahrenheit_to_celsius(fahrenheit: np.ndarray) -> np.ndarray:
    """Convert Fahrenheit to Celsius.

    Formula: C = (F - 32) × 5/9

    Args:
        fahrenheit: Array of temperatures in Fahrenheit

    Returns:
        Array of temperatures in Celsius

    Example:
        >>> f = np.array([32, 212])
        >>> c = fahrenheit_to_celsius(f)
        >>> round(c[0], 2), round(c[1], 2)
        (0.0, 100.0)
    """
    return (fahrenheit - 32) * 5/9


def demo_task6() -> None:
    """Interactive demo for Task 6: Temperature Conversion.

    Assignment: "Write a NumPy program to convert Centigrade degrees into
    Fahrenheit degrees."
    """
    hr("Task 6: Celsius ↔ Fahrenheit Conversion")

    # Sample data from assignment
    celsius_values = np.array([0, 12, 45.21, 34, 99.91])
    fahrenheit_values = np.array([-17.78, -11.11, 7.34, 1.11, 37.73, 0.])

    print("Example 1: Celsius → Fahrenheit")
    print(f"Values in Celsius: {celsius_values}")

    # Convert to Fahrenheit
    fahrenheit_result = celsius_to_fahrenheit(celsius_values)
    print(f"Values in Fahrenheit: {fahrenheit_result}")

    print("\n" + "─"*60)
    print("\nExample 2: Fahrenheit → Celsius")
    print(f"Values in Fahrenheit: {fahrenheit_values}")

    # Convert to Celsius
    celsius_result = fahrenheit_to_celsius(fahrenheit_values)
    print(f"Values in Celsius: {celsius_result}")

    # Educational explanation
    print("\n📚 Conversion formulas:")
    print("  Celsius → Fahrenheit: F = (C × 9/5) + 32")
    print("  Fahrenheit → Celsius: C = (F - 32) × 5/9")

    print("\n💡 NumPy advantages:")
    print("  - Vectorized operations (fast for large arrays)")
    print("  - No need for loops")
    print("  - Cleaner, more readable code")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 7: Append Values to Array
# ──────────────────────────────────────────────────────────────────────────────

def append_values(arr: np.ndarray, values: List[float]) -> np.ndarray:
    """Append values to end of array.

    Note: NumPy arrays have fixed size. append() creates a new array.

    Args:
        arr: Original array
        values: Values to append

    Returns:
        New array with appended values

    Example:
        >>> arr = np.array([10, 20, 30])
        >>> result = append_values(arr, [40, 50])
        >>> list(result)
        [10, 20, 30, 40, 50]
    """
    if not values:
        raise ValueError(
            "❌ No values to append\n"
            "💡 Tip: Provide at least one value to append"
        )

    # np.append() creates a new array (arrays are immutable in size)
    return np.append(arr, values)


def demo_task7() -> None:
    """Interactive demo for Task 7: Append Values.

    Assignment: "Write a NumPy program to append values to the end of an array."
    """
    hr("Task 7: Append Values to Array")

    # Original array from assignment
    original = np.array([10, 20, 30])

    print("Original array:")
    print(original)

    # Values to append
    new_values = [40, 50, 60, 70, 80, 90]

    print(f"\nAppending: {new_values}")

    # Append values
    result = append_values(original, new_values)

    print("\nAfter append values to the end of the array:")
    print(result)

    # Educational notes
    print("\n📚 Important: NumPy arrays have fixed size!")
    print("  - append() creates a NEW array")
    print("  - Original array is unchanged")
    print("  - For frequent appends, use Python lists or np.concatenate")

    print(f"\n💡 Memory addresses:")
    print(f"  Original: {id(original)}")
    print(f"  Result:   {id(result)} (different object!)")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 8: Statistical Functions
# ──────────────────────────────────────────────────────────────────────────────

def calculate_statistics(arr: np.ndarray) -> dict:
    """Calculate mean, median, and standard deviation.

    Args:
        arr: NumPy array of numeric values

    Returns:
        Dictionary with 'mean', 'median', 'std' keys

    Example:
        >>> arr = np.array([1, 2, 3, 4, 5])
        >>> stats = calculate_statistics(arr)
        >>> stats['mean']
        3.0
        >>> stats['median']
        3.0
    """
    if arr.size == 0:
        raise ValueError(
            "❌ Cannot calculate statistics for empty array\n"
            "💡 Tip: Provide array with at least one element"
        )

    return {
        'mean': np.mean(arr),
        'median': np.median(arr),
        'std': np.std(arr),
        'variance': np.var(arr),
        'min': np.min(arr),
        'max': np.max(arr),
        'sum': np.sum(arr),
        'size': arr.size
    }


def demo_task8() -> None:
    """Interactive demo for Task 8: Statistical Functions.

    Assignment: "Create a random NumPy array of 10 elements and calculate
    the mean, median, and standard deviation of the array."
    """
    hr("Task 8: Array Statistical Functions")

    # Create random array (10 elements, values 0-100)
    np.random.seed(42)  # For reproducibility
    arr = np.random.uniform(0, 100, size=10)

    print("Random array (10 elements):")
    print(arr)

    # Calculate statistics
    stats = calculate_statistics(arr)

    print("\n📊 Statistical Analysis:")
    print(f"  Mean (average):       {stats['mean']:.2f}")
    print(f"  Median (middle):      {stats['median']:.2f}")
    print(f"  Std Dev (spread):     {stats['std']:.2f}")
    print(f"  Variance:             {stats['variance']:.2f}")
    print(f"  Minimum:              {stats['min']:.2f}")
    print(f"  Maximum:              {stats['max']:.2f}")
    print(f"  Sum:                  {stats['sum']:.2f}")

    # Educational explanation
    print("\n📚 What do these mean?")
    print("  • Mean: Average value (sum / count)")
    print("  • Median: Middle value when sorted")
    print("  • Std Dev: How spread out the values are")
    print("  • Variance: Std Dev squared (variance = std²)")

    # Visual representation
    print("\n📈 Visual distribution:")
    sorted_arr = np.sort(arr)
    print(f"  Min: {sorted_arr[0]:.1f}")
    print(f"  Q1:  {np.percentile(arr, 25):.1f}")
    print(f"  Median: {stats['median']:.1f}")
    print(f"  Q3:  {np.percentile(arr, 75):.1f}")
    print(f"  Max: {sorted_arr[-1]:.1f}")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 9: Find Min/Max in 10x10 Array
# ──────────────────────────────────────────────────────────────────────────────

def find_min_max(arr: np.ndarray) -> Tuple[float, float, Tuple[int, ...], Tuple[int, ...]]:
    """Find minimum and maximum values with their positions.

    Args:
        arr: NumPy array (any shape)

    Returns:
        Tuple of (min_value, max_value, min_position, max_position)

    Example:
        >>> arr = np.array([[1, 5], [3, 2]])
        >>> min_val, max_val, min_pos, max_pos = find_min_max(arr)
        >>> min_val, max_val
        (1, 5)
        >>> min_pos, max_pos
        ((0, 0), (0, 1))
    """
    if arr.size == 0:
        raise ValueError("❌ Cannot find min/max in empty array")

    # Find min and max values
    min_val = np.min(arr)
    max_val = np.max(arr)

    # Find positions (indices) of min and max
    # argmin/argmax return flattened index, use unravel_index for multi-dim
    min_flat_idx = np.argmin(arr)
    max_flat_idx = np.argmax(arr)

    min_pos = np.unravel_index(min_flat_idx, arr.shape)
    max_pos = np.unravel_index(max_flat_idx, arr.shape)

    return min_val, max_val, min_pos, max_pos


def demo_task9() -> None:
    """Interactive demo for Task 9: Find Min/Max in 10x10 Array.

    Assignment: "Create a 10x10 array with random values and find the
    minimum and maximum values."
    """
    hr("Task 9: Find Min/Max in 10x10 Array")

    # Create 10x10 array with random values (0 to 100)
    np.random.seed(42)
    arr = np.random.uniform(0, 100, size=(10, 10))

    print("Created 10x10 array with random values (0-100)")
    print(f"Shape: {arr.shape}")
    print(f"Total elements: {arr.size}")

    # Display sample (first 5x5 corner)
    print("\nFirst 5x5 corner (sample):")
    print(arr[:5, :5])

    # Find min and max
    min_val, max_val, min_pos, max_pos = find_min_max(arr)

    print(f"\n🔍 Search Results:")
    print(f"  Minimum value: {min_val:.2f}")
    print(f"    Position: Row {min_pos[0]}, Column {min_pos[1]}")
    print(
        f"    Verification: arr[{min_pos[0]}, {min_pos[1]}] = {arr[min_pos]:.2f}")

    print(f"\n  Maximum value: {max_val:.2f}")
    print(f"    Position: Row {max_pos[0]}, Column {max_pos[1]}")
    print(
        f"    Verification: arr[{max_pos[0]}, {max_pos[1]}] = {arr[max_pos]:.2f}")

    # Additional statistics
    print(f"\n📊 Additional stats:")
    print(f"  Mean: {np.mean(arr):.2f}")
    print(f"  Range: {max_val - min_val:.2f}")


# ──────────────────────────────────────────────────────────────────────────────
# TASK 10: Create 3x3x3 Array
# ──────────────────────────────────────────────────────────────────────────────

def create_3d_array(shape: Tuple[int, int, int]) -> np.ndarray:
    """Create 3D array with random values.

    Args:
        shape: Tuple of (depth, rows, cols)

    Returns:
        3D NumPy array with random values (0 to 1)

    Example:
        >>> arr = create_3d_array((2, 2, 2))
        >>> arr.shape
        (2, 2, 2)
        >>> arr.ndim
        3
    """
    if len(shape) != 3:
        raise ValueError(
            f"❌ Invalid shape: {shape}\n"
            "💡 Tip: Shape must be 3 dimensions (e.g., (3, 3, 3))"
        )

    if any(dim <= 0 for dim in shape):
        raise ValueError(
            f"❌ Invalid dimensions: {shape}\n"
            "💡 Tip: All dimensions must be positive"
        )

    # Create 3D array with random values between 0 and 1
    return np.random.random(shape)


def demo_task10() -> None:
    """Interactive demo for Task 10: Create 3x3x3 Array.

    Assignment: "Create a 3x3x3 array with random values."
    """
    hr("Task 10: Create 3x3x3 Array with Random Values")

    # Create 3x3x3 array
    np.random.seed(42)
    arr = create_3d_array((3, 3, 3))

    print("Created 3x3x3 array (3D tensor)")
    print(f"  Shape: {arr.shape}")
    print(f"  Dimensions: {arr.ndim}D")
    print(f"  Total elements: {arr.size}")
    print(f"  Dtype: {arr.dtype}")

    # Display the array layer by layer
    print("\n3D Array (displayed layer by layer):")
    for i in range(arr.shape[0]):
        print(f"\nLayer {i} (depth={i}):")
        print(arr[i])

    # Educational explanation
    print("\n📚 Understanding 3D Arrays:")
    print("  • Think of it as a stack of 2D matrices")
    print("  • Shape (3, 3, 3) means:")
    print("    - 3 layers (depth)")
    print("    - 3 rows per layer")
    print("    - 3 columns per row")
    print(f"  • Access element: arr[layer, row, col]")
    print(f"    Example: arr[0, 1, 2] = {arr[0, 1, 2]:.4f}")

    # Practical applications
    print("\n💡 Real-world uses:")
    print("  • Images: (height, width, RGB channels)")
    print("  • Video: (frames, height, width)")
    print("  • Scientific data: (time, latitude, longitude)")


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

    # Check NumPy availability
    if not NUMPY_AVAILABLE:
        return 1

    # Display NumPy version info
    print("\n" + "="*70)
    print(" 🔢 Lesson 16: NumPy Array Operations ".center(70, "="))
    print("="*70)
    print(f"NumPy version: {np.__version__}")

    # Main menu loop
    try:
        while True:
            hr("Main Menu")
            print("Choose a task to explore:\n")
            print("  1️⃣   Task 1: Convert List to 1D Array")
            print("  2️⃣   Task 2: Create 3x3 Matrix (2-10)")
            print("  3️⃣   Task 3: Null Vector & Update")
            print("  4️⃣   Task 4: Array from 12 to 38")
            print("  5️⃣   Task 5: Convert to Float Type")
            print("  6️⃣   Task 6: Celsius ↔ Fahrenheit")
            print("  7️⃣   Task 7: Append Values to Array")
            print("  8️⃣   Task 8: Statistical Functions")
            print("  9️⃣   Task 9: Find Min/Max (10x10)")
            print("  🔟 Task 10: Create 3x3x3 Array")
            print("\n  🎯 Run All Tasks")
            print("  🧪 Run Tests")
            print("  0️⃣   Exit")

            choice = input("\nSelect option: ").strip()

            try:
                if choice == "1":
                    demo_task1()

                elif choice == "2":
                    demo_task2()

                elif choice == "3":
                    demo_task3()

                elif choice == "4":
                    demo_task4()

                elif choice == "5":
                    demo_task5()

                elif choice == "6":
                    demo_task6()

                elif choice == "7":
                    demo_task7()

                elif choice == "8":
                    demo_task8()

                elif choice == "9":
                    demo_task9()

                elif choice == "10":
                    demo_task10()

                elif choice.lower() in ("all", "🎯"):
                    # Run all tasks in sequence
                    hr("Running All Tasks")
                    print("Executing all 10 tasks...\n")

                    tasks = [
                        demo_task1, demo_task2, demo_task3, demo_task4, demo_task5,
                        demo_task6, demo_task7, demo_task8, demo_task9, demo_task10
                    ]

                    for i, task in enumerate(tasks, 1):
                        try:
                            task()
                            if i < len(tasks):
                                input(
                                    f"\nPress Enter to continue to Task {i+1}...")
                        except Exception as e:
                            print(f"❌ Error in Task {i}: {e}")
                            if not confirm("Continue with next task?"):
                                break

                    print("\n✓ All tasks completed!")

                elif choice.lower() in ("tests", "test", "🧪", "t"):
                    run_tests()
                    input("\nPress Enter to continue...")

                elif choice == "0":
                    print("\n👋 Thank you for exploring NumPy!")
                    print("💡 Remember: NumPy is the foundation of scientific Python")
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
