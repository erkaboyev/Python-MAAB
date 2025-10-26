# Task 1: Given the side of a square. Find its perimeter and area.
print("=== Task 1 ===")
    side = read_float("Enter the side of the square: ", nonneg=True)
    perimeter = 4 * side
    area = side ** 2
    print(f"Perimeter of a square: {perimeter:.2f}")
    print(f"Area of a square: {area:.2f}\n")


# Task 2: Given the diameter of a circle, find its circumference.
print("=== Task 2 ===")
    diameter = read_float("Enter the diameter of the circle: ", nonneg=True)
    length = math.pi * diameter  # C = π * d
    print(f"Circumference length: {length:.2f}\n")


# Task 3: Given two numbers a and b, find their arithmetic mean.
print("=== Task 3 ===")
a = float(input("Enter a number a: "))
b = float(input("Enter a number b: "))
mean = (a + b) / 2
print(f"Arithmetic mean: {mean:.2f}")


# Task 4: Given two numbers a and b. Find their sum, product, and square of each number.
print("=== Task 4 ===")
a = float(input("Enter a number a: "))
b = float(input("Enter a number b: "))
 sum_ab = a + b
    product_ab = a * b
    square_a = a ** 2
    square_b = b ** 2
    print(f"Amount: {sum_ab:.2f}")
    print(f"Product: {product_ab:.2f}")
    print(f"Square of number a: {square_a:.2f}")
    print(f"Square of number b: {square_b:.2f}")
