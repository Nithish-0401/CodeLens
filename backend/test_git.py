
from github_integration import (
    parse_github_url,
    fetch_github_file,
)

# Test 1: Invalid repository URL
print("\nTEST 1: Invalid repository URL")

try:
    parse_github_url("https://example.com/not-a-repository")
except ValueError as exc:
    print("Handled correctly:", exc)


# Test 2: Python file that does not exist
print("\nTEST 2: Missing Python file")

try:
    fetch_github_file(
        "pallets",
        "flask",
        "this_file_does_not_exist.py"
    )
except ValueError as exc:
    print("Handled correctly:", exc)


# Test 3: Unsupported file extension
print("\nTEST 3: Non-Python file")

try:
    fetch_github_file(
        "pallets",
        "flask",
        "README.md"
    )
except ValueError as exc:
    print("Handled correctly:", exc)
