from analyzer.llm_reviewer import review_code

code = """ 
    password = "admin123"
    def login():
        if password == "admin123":
            print("Login successful")
    """
findings = [
    {
        "source": "bandit",
        "category": "security",
        "rule": "B105",
        "severity": "LOW",
        "line": 2,
        "title": "Possible hardcoded password",
        "message": "Possible hardcoded password: 'admin123'",
        "confidence": "MEDIUM"
    }
]

result=review_code(code,findings)

print("Review Result:")
print(result)