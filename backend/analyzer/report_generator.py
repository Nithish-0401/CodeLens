def calculate_score(findings: list):
    score = 100

    penalties = {
        "LOW": 5,
        "MEDIUM": 10,
        "HIGH": 20,
        "CRITICAL": 30
    }

    for finding in findings:
        severity = finding.get("severity")
        if not severity:
            continue
        severity = severity.upper()

        score -= penalties.get(severity, 0)
    return max(0, min(100, score))


def get_risk_level(score: int):
    if score >= 80:
        return "LOW"
    elif score >= 60:
        return "MEDIUM"
    elif score >= 40:
        return "HIGH"
    else:
        return "CRITICAL"


def count_severities(findings: list):
    counts = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0
    }

    for finding in findings:
        severity = finding.get("severity")

        if not severity:
            continue

        severity = severity.upper()

        if severity in counts:
            counts[severity] += 1

    return counts

def generate_report(
    filename: str,
    static_findings: list,
    ai_review: dict
):
    """
    Generate the final structured code review report.
    """

    ai_findings = ai_review.get("findings", [])

    score = calculate_score(ai_findings)

    severity_counts = count_severities(ai_findings)

    risk_level = get_risk_level(score)

    return {
        "filename": filename,

        "score": score,

        "risk_level": risk_level,

        "statistics": {
            "total_findings": len(ai_findings),
            "low": severity_counts["LOW"],
            "medium": severity_counts["MEDIUM"],
            "high": severity_counts["HIGH"],
            "critical": severity_counts["CRITICAL"]
        },

        "summary": ai_review.get(
            "summary",
            ""
        ),

        "static_findings": static_findings,

        "findings": ai_findings,

        "strengths": ai_review.get(
            "strengths",
            []
        ),

        "improvements": ai_review.get(
            "improvements",
            []
        )
    }