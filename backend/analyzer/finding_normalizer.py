def normalize_ruff_findings(ruff_results: list):
    """Convert Ruff findings into a common format."""

    normalized = []

    for finding in ruff_results:
        rule = finding.get("code", "UNKNOWN")

        if rule.startswith("S"):
            category = "security"
        elif rule.startswith(("F", "E", "W", "B")):
            category = "code_quality"
        else:
            category = "maintainability"

        normalized.append({
            "source": "ruff",
            "category": category,
            "rule": rule,
            "severity": None,
            "line": finding.get("location", {}).get("row"),
            "title": finding.get(
                "message",
                "Code quality issue"
            ),
            "message": finding.get("message", ""),
            "confidence": None
        })

    return normalized


def normalize_bandit_findings(bandit_results: list):
    """Convert Bandit findings into a common format."""

    normalized = []

    for finding in bandit_results:

        severity = finding.get(
            "issue_severity",
            "LOW"
        ).upper()

        normalized.append({
            "source": "bandit",
            "category": "security",
            "rule": finding.get(
                "test_id",
                "UNKNOWN"
            ),
            "severity": severity,
            "line": finding.get("line_number"),
            "title": finding.get(
                "test_name",
                "Security issue"
            ),
            "message": finding.get(
                "issue_text",
                ""
            ),
            "confidence": finding.get(
                "issue_confidence"
            )
        })

    return normalized


def normalize_findings(
    ruff_results: list,
    bandit_results: list
):
    """Combine Ruff and Bandit findings."""

    ruff_findings = normalize_ruff_findings(
        ruff_results
    )

    bandit_findings = normalize_bandit_findings(
        bandit_results
    )

    return ruff_findings + bandit_findings