import subprocess
import json
import sys
import tempfile
from pathlib import Path


def run_ruff(code: str):

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8"
    ) as temp_file:

        temp_file.write(code)
        temp_file_path = temp_file.name

    try:
        result = subprocess.run(
           [
            sys.executable,
            "-m",
            "ruff",
            "check",
            temp_file_path,
            "--output-format",
            "json"
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0 and not result.stdout:
            return [{
                "error": "Ruff execution failed",
                "details": result.stderr.strip()
            }]

        if result.stdout:
            findings = json.loads(result.stdout)
        else:
            findings = []

        return findings
    finally:
        Path(temp_file_path).unlink(missing_ok=True)


def run_bandit(code: str):

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8"
    ) as temp_file:

        temp_file.write(code)
        temp_file_path = temp_file.name

    try:
        result = subprocess.run(
           [
            sys.executable,
            "-m",
            "bandit",
            "-f",
            "json",
            "-q",
            temp_file_path
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0 and not result.stdout:
            return [{
                "error": "Bandit execution failed",
                "details": result.stderr.strip()
            }]

        if result.stdout:

            try:
                report = json.loads(result.stdout)
                return report.get("results", [])

            except json.JSONDecodeError:
                return [{
                    "error": "Bandit returned invalid JSON",
                    "details": result.stdout
                }]

        return []

    finally:
        Path(temp_file_path).unlink(missing_ok=True)


def run_static_analysis(code: str):

    ruff_results = run_ruff(code)

    bandit_results = run_bandit(code)

    return {
        "ruff": ruff_results,
        "bandit": bandit_results
    }