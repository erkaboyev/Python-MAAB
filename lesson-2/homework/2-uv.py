# Task 1: Age Calculator
from datetime import date

name = input("Your name: ")
year = int(input("Year of birth (e.g. 2005): "))
today_year = date.today().year  # current year
age = today_year - year
print(f"Hello, {name}! You are {age} years old.")


# Task 2: Extract Car Names — txt = 'LMaasleitbtui'
# Idea: take every other character.
txt = 'LMaasleitbtui'
car2 = txt[1::2]   # 'Malibu'
car1 = txt[::2]    # 'Lasetti' 
print(car1, car2)


# Task 3: Extract Car Names — txt = 'MsaatmiazD'
# We use slices with a step and line wrap [::-1]
txt = 'MsaatmiazD'
car1 = txt[::2]            # 'Matiz'
car2 = txt[1::2][::-1]     # 'Damas' (take odd numbers + reverse)
print(car1, car2)


# Task 4: Extract Residence Area — txt = "I'am John. I am from London"
# We simply take everything after the word “from” (case-insensitive) and remove spaces/periods:
import re

txt = "I'am John. I am from London"
m = re.search(r'\bfrom\s+([A-Za-z\-\' ]+)\.?', txt, flags=re.IGNORECASE) # Regular expressions via the re module
area = m.group(1).strip() if m else None
print(area)  # London

# Task 5: Reverse String
s = input("Enter text: ")
print(s[::-1]) # Cut with a step of -1 — line reversal.


# Task 6: Count Vowels
s = input("Enter text: ")
vowels = set("aeiou")
count = sum(1 for ch in s.lower() if ch in vowels)
print(count)


# Task 7: Find Maximum Value
nums = list(map(float, input("Numbers (space-separated): ").split()))
print(max(nums))


# Task 8: Check Palindrome
# Ignore case and non-alphanumeric characters.
s = input("Word: ")

normalized = "".join(ch for ch in s if ch.isalnum()).casefold()
is_pal = normalized == normalized[::-1] # We use casefold() and the slice [::-1]
print("Palindrome" if is_pal else "Not a palindrome")


# Task 9: Extract Email Domain
email = input("Email: ").strip()
domain = email.rsplit("@", 1)[-1] if "@" in email else None #Take the part after @ (reliably — from right to left)
print(domain)


# Task 10: Generate Random Password
import secrets
import string

def gen_password(length=12):
    if length < 4:
        raise ValueError("Length must be ≥ 4")

    # We guarantee at least one from each class.
    groups = [
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits,
        string.punctuation
    ]

    pwd_chars = [secrets.choice(g) for g in groups]
    all_chars = "".join(groups)
    pwd_chars += [secrets.choice(all_chars) for _ in range(length - len(pwd_chars))]

    # simple shuffle without a predictable selection order
    for i in range(len(pwd_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        pwd_chars[i], pwd_chars[j] = pwd_chars[j], pwd_chars[i]

    return "".join(pwd_chars)

print(gen_password(12))

# For passwords, we use the secrets module (cryptographically strong random values) and the constants string.ascii_*, string.digits, string.punctuation.




