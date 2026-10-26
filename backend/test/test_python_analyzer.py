"""
test_python_analyzer.py

Purpose:
- Exercise a Python source-code analyzer.
- Contains examples of imports, functions, methods, classes, loops,
  conditions, comprehensions, exception handling, and file operations.
- Intentionally contains Ruff lint findings and Bandit security findings.
- DO NOT use this file as production code.

Suggested commands:
    ruff check test_python_analyzer.py --select ALL
    bandit -r test_python_analyzer.py
"""

# -------------------------
# Ruff / lint test cases
# -------------------------

import os
import sys
import math
import json
import re
import random
import subprocess
import hashlib
import tempfile
import pickle
import sqlite3
import logging
import pathlib
from pathlib import Path
from collections import defaultdict


UNUSED_GLOBAL = 123


def unused_function():
    """A function that is intentionally never called."""
    unused_local = "unused"
    another_unused = 42
    return None


def calculate(value, unused_parameter, another_parameter=None):
    # F841: assigned but never used
    unused_variable = 999

    # E712: comparison to True
    if value == True:
        print("value is true")

    # E711: comparison to None
    if another_parameter == None:
        print("parameter is none")

    # E713: membership test can be simplified
    if value not in [1, 2, 3]:
        print("not in list")

    # E741: ambiguous variable name
    l = 10
    O = 20
    I = l + O

    # E702: multiple statements on one line
    x = 1; y = 2

    # E401: multiple imports on one line
    import datetime, time

    # E722: bare except
    try:
        result = 10 / value
    except:
        result = 0

    # B007: loop control variable not used
    for i in range(5):
        print("loop")

    # B020: loop variable overwritten
    for item in [1, 2, 3]:
        item = item + 1
        print(item)

    # F841: local variable assigned but unused
    temporary = calculate_square(5)

    return result


def calculate_square(number):
    return number * number


def too_long_line():
    # E501: intentionally overlong line
    message = "This is an intentionally very long line that is included to test whether the analyzer detects lines that exceed the configured maximum line length."
    return message


def shadowing_examples():
    # A001/A002-style naming issues when those rule families are enabled.
    list = [1, 2, 3]
    id = 100
    input = "hello"
    print(list, id, input)

    # E741 again
    l = 1
    return l


def control_flow(value):
    # SIM102/SIM103-style findings when simplification rules are enabled.
    if value > 0:
        if value < 100:
            return True

    if value == 10:
        return True
    else:
        return False


def useless_operations():
    # B018: useless expression
    "This string expression does nothing."

    # B018: another useless expression
    12345

    # F841
    unused_result = math.sqrt(16)

    return 0


class ExampleCalculator:
    """Class containing methods for analyzer extraction."""

    def __init__(self, initial_value):
        self.value = initial_value

    def add(self, amount):
        self.value += amount
        return self.value

    def multiply(self, amount):
        return self.value * amount

    def process(self, values):
        results = []

        # for loop
        for value in values:
            # if / elif / else
            if value > 10:
                results.append(value * 2)
            elif value == 10:
                results.append(value)
            else:
                results.append(value + 1)

        # while loop
        counter = 0
        while counter < len(results):
            results[counter] = results[counter]
            counter += 1

        return results


def comprehensions_and_conditions(values):
    squares = [x * x for x in values]
    even_numbers = {x for x in values if x % 2 == 0}
    mapping = {x: x * 2 for x in values}

    if squares and even_numbers and mapping:
        return squares, even_numbers, mapping

    return [], set(), {}


# -------------------------
# Bandit security test cases
# -------------------------

# B105: hardcoded password-like string
PASSWORD = "SuperSecretPassword123"

# B106: hardcoded password in function argument
def connect(username, password="admin123"):
    return username, password


# B107: hardcoded password in default argument
def authenticate(password="root_password"):
    return password


def dangerous_assert(user_value):
    # B101: assert used
    assert user_value == "admin"
    return True


def dangerous_exec(user_code):
    # B102: exec
    exec(user_code)
    return True


def dangerous_eval(user_expression):
    # B307: eval
    return eval(user_expression)


def dangerous_os_command(command):
    # B605: start process with shell
    os.system(command)


def dangerous_subprocess(command):
    # B602: subprocess with shell=True
    subprocess.run(command, shell=True)


def dangerous_popen(command):
    # B602/B603-related subprocess analysis
    subprocess.Popen(command, shell=True)


def dangerous_chmod(filename):
    # B103: insecure file permissions
    os.chmod(filename, 0o777)


def dangerous_bind():
    # B104: binding to all interfaces
    server_host = "0.0.0.0"
    return server_host


def dangerous_temp_file():
    # B108: insecure temporary file usage
    temp = tempfile.mktemp()
    return temp


def unsafe_pickle(filename):
    # B301: unsafe pickle deserialization
    with open(filename, "rb") as file:
        return pickle.load(file)


def weak_hash(data):
    # B303: weak MD5 hash
    return hashlib.md5(data.encode()).hexdigest()


def weak_sha1(data):
    # B324: weak SHA1 hash
    return hashlib.sha1(data.encode()).hexdigest()


def weak_random():
    # B311: random module is not suitable for security-sensitive use
    return random.random()


def insecure_sql(user_id):
    # B608: SQL injection pattern
    query = "SELECT * FROM users WHERE id = '%s'" % user_id

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def insecure_sql_fstring(user_id):
    # Another B608-style SQL injection pattern
    query = f"SELECT * FROM users WHERE id = '{user_id}'"

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def unsafe_yaml(data):
    # B506: unsafe yaml.load
    import yaml
    return yaml.load(data)


def unsafe_tarfile(archive):
    # B202: tarfile extraction without safety checks
    import tarfile
    with tarfile.open(archive) as tar:
        tar.extractall("/tmp/extracted")


def weak_crypto_cipher():
    # B304: insecure cipher construction
    from Crypto.Cipher import DES
    return DES.new(b"12345678")


def wildcard_import():
    # F403/F405 when this module is imported/analyzed
    from os import *
    return path


def insecure_logging(password):
    # Potential sensitive information handling for analyzer testing
    logging.info("User password: %s", password)


def exception_cases():
    try:
        risky_operation()
    except Exception:
        # B110: try/except/pass
        pass

    try:
        risky_operation()
    except Exception:
        # B112: try/except/continue
        continue_target = True
        if continue_target:
            return None

    return None


def risky_operation():
    raise RuntimeError("test")


def main():
    values = [1, 5, 10, 20, 50]

    calculator = ExampleCalculator(10)

    # Method calls
    calculator.add(5)
    calculator.multiply(2)
    processed = calculator.process(values)

    # Function calls
    calculate(5, "unused")
    calculate_square(10)
    comprehensions_and_conditions(values)

    # Conditional
    if processed:
        print("Processed:", processed)
    else:
        print("No results")

    return processed


if __name__ == "__main__":
    main()
