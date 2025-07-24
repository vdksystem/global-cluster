import random

SYMBOLS = ["cherry", "lemon", "bell", "seven", "bar"]
ROWS, COLUMNS = 3, 3

def generate_reels():
    return [[random.choice(SYMBOLS) for _ in range(COLUMNS)] for _ in range(ROWS)]

def calculate_win(reels):
    # Simple: reward if middle row has all the same symbol
    middle_row = reels[1]
    if all(symbol == middle_row[0] for symbol in middle_row):
        return 10.0  # fixed win
    return 0.0
