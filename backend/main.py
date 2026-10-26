import code

from fastapi import FastAPI, UploadFile, File, HTTPException, requests
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from github_integration import (
    parse_github_url,
    fetch_github_file,
)



app = FastAPI(title="AI Code Reviewer")

class GitHubReviewRequest(BaseModel):
    repo_url: str
    file_path: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from analyzer.ast_analyzer import analyze_code
from analyzer.static_analyzer import run_static_analysis
from analyzer.finding_normalizer import normalize_findings
from analyzer.llm_reviewer import review_code
from analyzer.report_generator import generate_report



@app.get("/")
def home():
    return {
        "message": "AI Code Reviewer API is running"
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    if not file.filename or not file.filename.lower().endswith(".py"):
        raise HTTPException(
            status_code=400,
            detail="Only Python (.py) files are allowed."
        )

    contents = await file.read()

    try:
        code = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Only UTF-8 encoded Python files are supported."
    )

    


    analysis = analyze_code(code)

    static_analysis = run_static_analysis(code)

    normalized_findings = normalize_findings(static_analysis["ruff"], static_analysis["bandit"])

    review = review_code(code, normalized_findings)

    report = generate_report(file.filename, normalized_findings, review)

    return {
        "filename": file.filename,
        "code": code,
        "analysis": analysis,
        "static_analysis": static_analysis,
        "normalized_findings": normalized_findings,
        "ai_review": review,
        "report": report
    }

    
@app.post("/review-github")
def review_github_file(request: GitHubReviewRequest):

    try:
        owner, repo = parse_github_url(request.repo_url)

        code = fetch_github_file(
            owner,
            repo,
            request.file_path
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to GitHub."
        ) from exc

    analysis = analyze_code(code)

    static_analysis = run_static_analysis(code)

    normalized_findings = normalize_findings(static_analysis["ruff"],static_analysis["bandit"])

    ai_review = review_code(code,normalized_findings)

    report = generate_report(request.file_path,normalized_findings,ai_review)

    return {
        "source": "github",
        "repository": f"{owner}/{repo}",
        "file_path": request.file_path,
        "code": code,
        "analysis": analysis,
        "static_analysis": static_analysis,
        "findings": normalized_findings,
        "ai_review": ai_review,
        "report": report
    }