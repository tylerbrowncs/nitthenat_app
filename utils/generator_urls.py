import string

ALPHABET = string.ascii_letters + string.digits
BASE = len(ALPHABET)
MAX = BASE ** 6

# Must be coprime with MAX (odd number works here)
MULTIPLIER = 5_000_001
OFFSET = 12345

def generate_string(n):
    if n >= MAX:
        raise ValueError("Exceeded maximum possible unique strings")

    # Permute the counter (bijective mapping)
    n = (n * MULTIPLIER + OFFSET) % MAX

    result = ""
    for _ in range(6):
        result = ALPHABET[n % BASE] + result
        n //= BASE

    return result

