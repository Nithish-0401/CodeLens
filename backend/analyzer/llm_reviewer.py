import os
from dotenv import load_dotenv
from google import genai
from groq import Groq
import json 

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

client = Groq(api_key=api_key)

def review_code(code : str , findings: list):

    """ Send Python code and static-analysis findings to Gemini
    for contextual code review.  """

    prompt=f""" You are an expert Python code reviewer.
    Analyze the Python code and the findings produced by
    Ruff and Bandit.

    Your responsibilities:

    1. Identify real bugs and logical problems.
    2. Identify security vulnerabilities.
    3. Identify code quality problems.
    4. Identify maintainability problems.
    5. Evaluate severity based on the actual context.
    6. Explain why each issue matters.
    7. Suggest a practical fix.
    8. Do not report imaginary problems.
    9. Do not blindly trust static-analysis findings.
    10. Identify false positives when appropriate.
    11. Use the exact source-code line number whenever possible.
    12. Avoid duplicate findings.

    Severity definitions:

    LOW:
    Minor issue with limited impact.

    MEDIUM:
    Issue that could cause incorrect behavior or
    maintenance problems.

    HIGH:
    Serious bug or security problem that could
    significantly affect the application.

    CRITICAL:
    Severe security vulnerability or issue that could
    cause major damage, data loss, unauthorized access,
    or system compromise.

    PYTHON CODE:
    {code}

    STATIC ANALYSIS FINDINGS:
    {json.dumps(findings, indent=2)}

    Return ONLY valid JSON using this structure:

    {{
        "summary": "Short overall summary",

        "overall_risk": "LOW | MEDIUM | HIGH | CRITICAL",

        "findings": [
            {{
                "source": "ruff | bandit | groq",
                "category": "bug | security | code_quality | maintainability",
                "rule": "Rule ID or null",
                "severity": "LOW | MEDIUM | HIGH | CRITICAL",
                "line": 1,
                "title": "Short issue title",
                "explanation": "Explain the issue clearly",
                "suggestion": "Explain how to fix it",
                "confidence": "LOW | MEDIUM | HIGH"
            }}
        ],

        "strengths": [
            "Positive aspect of the code"
        ],

        "improvements": [
            "Improvement suggestion"
        ]
    }}
    """
    
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert Python code reviewer. "
                    "Return only a complete, valid JSON object. "
                    "Do not include markdown or extra commentary. "
                    "Keep explanations concise."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_completion_tokens=4000,
        response_format={"type": "json_object"},
    )


    response_text = response.choices[0].message.content.strip()

    # Remove markdown JSON fences if the model adds them
    if response_text.startswith("```json"):
        response_text = response_text[7:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    try:
        return json.loads(response_text)

    except json.JSONDecodeError:
        return {
            "summary": "Groq returned invalid JSON.",
            "overall_risk": "UNKNOWN",
            "raw_response": response_text
        }