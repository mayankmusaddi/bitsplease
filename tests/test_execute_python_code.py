from unittest import TestCase
from tools.execute_python_code import execute_python_code
import ast


class TestExecutePythonCode(TestCase):
    def test_execute_python_code(self):
        _results = execute_python_code("""# Import the random module
import random

# Function to generate a list of random numbers
def generate_random_numbers(n, start, end):
    random_numbers = []
    for _ in range(n):
        random_numbers.append(random.randint(start, end))
    return random_numbers

# Generate a list of 10 random numbers between 1 and 50
random_numbers = generate_random_numbers(10, 1, 50)
# Print the list of random numbers
print(random_numbers)""")
        _results = _results.encode("utf-8", "ignore").decode("utf-8")
        _results = ast.literal_eval(_results)
        assert len(_results) == 10

        # assert "title" in _results[0]
