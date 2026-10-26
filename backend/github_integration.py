
import base64
import re

import requests


GITHUB_API = "https://api.github.com"


def parse_github_url(repo_url: str):
    """Extract the owner and repository name from a GitHub URL."""

    pattern = (
        r"^https?://github\.com/"
        r"([^/\s]+)/([^/\s]+)/?$"
    )

    match = re.match(pattern, repo_url.strip())

    if not match:
        raise ValueError(
            "Please provide a valid GitHub repository URL."
        )

    owner = match.group(1)
    repo = match.group(2)

    if repo.endswith(".git"):
        repo = repo[:-4]

    if not owner or not repo:
        raise ValueError(
            "GitHub owner and repository are required."
        )

    return owner, repo


def fetch_github_file(
    owner: str,
    repo: str,
    file_path: str
) -> str:
    """Fetch a Python file from a public GitHub repository."""

    if not file_path or not file_path.lower().endswith(".py"):
        raise ValueError(
            "Only Python (.py) files are supported."
        )

    url = (
        f"{GITHUB_API}/repos/{owner}/{repo}"
        f"/contents/{file_path}"
    )

    response = requests.get(
        url,
        headers={
            "Accept": "application/vnd.github+json"
        },
        timeout=15
    )

    if response.status_code == 404:
        raise ValueError(
            "Repository or file not found, or it is not public."
        )

    if response.status_code == 403:
        raise ValueError(
            "GitHub rate limit reached or access was denied."
        )

    response.raise_for_status()

    data = response.json()

    if data.get("type") != "file":
        raise ValueError(
            "The requested path is not a file."
        )

    if data.get("encoding") != "base64":
        raise ValueError(
            "GitHub returned an unsupported file encoding."
        )

    try:
        encoded_content = "".join(
            data["content"].split()
        )

        content = base64.b64decode(
            encoded_content,
            validate=True
        ).decode("utf-8")

    except (KeyError, ValueError, UnicodeDecodeError) as exc:
        raise ValueError(
            "Could not decode the Python file as UTF-8."
        ) from exc

    return content
