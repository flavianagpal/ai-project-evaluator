import requests
import base64
import math
from datetime import datetime, timezone

from repository_structure import get_repo_structure
from engineering_signals import detect_engineering_signals
from engineering_review import build_engineering_review
from engineering_score import calculate_engineering_score
from technology_detector import detect_technologies
from dependency_parser import get_file_content, detect_frontend_stack
from health_assessment import generate_health_assessment
from recommendations import generate_recommendations
from dependency_detector import detect_dependencies_from_files


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get(url: str, params: dict | None = None, token: str | None = None) -> requests.Response:
    """Central HTTP helper — injects auth token when provided."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.get(url, headers=headers, params=params, timeout=10)


def find_file_in_structure(structure: list[str], filenames: list[str]) -> str | None:
    """
    Find the first matching file path in the repository structure.
    Matching is based on path ending, so it works for nested files too.

    Example:
        find_file_in_structure(structure, ["requirements.txt", "pyproject.toml"])
    """
    structure_lower = [item.lower() for item in structure]
    filename_set = [name.lower() for name in filenames]

    for path in structure_lower:
        for name in filename_set:
            if path.endswith(name):
                return path

    return None


# ── Data-fetch layer ──────────────────────────────────────────────────────────

def get_repo_data(owner: str, repo: str, token: str | None = None) -> dict | None:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    r = _get(url, token=token)
    return r.json() if r.status_code == 200 else None


def get_readme_content(owner: str, repo: str, token: str | None = None) -> str:
    r = _get(f"https://api.github.com/repos/{owner}/{repo}/readme", token=token)
    if r.status_code != 200:
        return ""

    data = r.json()
    try:
        return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def get_commit_count(owner: str, repo: str, token: str | None = None) -> int:
    """
    Uses the contributor-stats endpoint to sum all commits.
    Falls back to a paginated commits walk if stats aren't ready.
    """
    r = _get(
        f"https://api.github.com/repos/{owner}/{repo}/stats/contributors",
        token=token,
    )
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list):
            return sum(c.get("total", 0) for c in data)

    # Fallback: paginated commits (up to 500 for speed)
    total = 0
    for page in range(1, 6):
        r = _get(
            f"https://api.github.com/repos/{owner}/{repo}/commits",
            params={"per_page": 100, "page": page},
            token=token,
        )
        if r.status_code != 200:
            break

        batch = r.json()
        total += len(batch)

        if len(batch) < 100:
            break

    return total


def get_contributor_count(owner: str, repo: str, token: str | None = None) -> int:
    r = _get(
        f"https://api.github.com/repos/{owner}/{repo}/contributors",
        params={"per_page": 100, "anon": "true"},
        token=token,
    )
    if r.status_code != 200:
        return 0
    return len(r.json())


def get_has_license(owner: str, repo: str, token: str | None = None) -> bool:
    r = _get(f"https://api.github.com/repos/{owner}/{repo}/license", token=token)
    return r.status_code == 200


def get_has_ci(owner: str, repo: str, token: str | None = None) -> bool:
    """Check for GitHub Actions workflows or classic CI config files."""
    # GitHub Actions
    r = _get(
        f"https://api.github.com/repos/{owner}/{repo}/contents/.github/workflows",
        token=token,
    )
    if r.status_code == 200 and isinstance(r.json(), list) and len(r.json()) > 0:
        return True

    # Common CI files at root
    for ci_file in [".travis.yml", "Jenkinsfile", ".circleci/config.yml", "azure-pipelines.yml"]:
        r2 = _get(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{ci_file}",
            token=token,
        )
        if r2.status_code == 200:
            return True

    return False


def get_open_issues_count(owner: str, repo: str, token: str | None = None) -> int:
    """
    Returns open issues excluding pull requests using GitHub Search API.
    More accurate than /issues?per_page=100 for large repos.
    """
    query = f"repo:{owner}/{repo} type:issue state:open"
    r = _get(
        "https://api.github.com/search/issues",
        params={"q": query, "per_page": 1},
        token=token,
    )

    if r.status_code != 200:
        return 0

    data = r.json()
    return data.get("total_count", 0)


def get_release_count(owner: str, repo: str, token: str | None = None) -> int:
    r = _get(
        f"https://api.github.com/repos/{owner}/{repo}/releases",
        params={"per_page": 100},
        token=token,
    )
    if r.status_code != 200:
        return 0
    return len(r.json())


# ── Scoring engine ────────────────────────────────────────────────────────────

def _days_since(iso_str: str) -> int:
    """How many days ago was an ISO-8601 timestamp?"""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except Exception:
        return 9999


def _log_score(value: int, threshold_full: int, max_points: int) -> float:
    """
    Smooth logarithmic scoring: 0 → 0 pts, threshold_full → max_points,
    values above threshold_full plateau gradually.
    """
    if value <= 0:
        return 0.0

    ratio = value / threshold_full
    return min(max_points, max_points * math.log1p(ratio) / math.log1p(1))


def compute_score(
    data: dict,
    readme: str,
    commit_count: int,
    contributor_count: int,
    has_license: bool,
    has_ci: bool,
    open_issues: int,
    release_count: int,
) -> tuple[float, list[dict], list[dict], list[dict]]:
    """
    Returns:
        total_score, strengths, weaknesses, breakdown
    """
    breakdown: list[dict] = []

    # ── 1. Documentation (25 pts) ─────────────────────────────────────────
    doc_pts = 0
    if readme:
        doc_pts += 5
        rl = len(readme)

        if rl > 3000:
            doc_pts += 10
        elif rl > 1000:
            doc_pts += 6
        elif rl > 300:
            doc_pts += 2

        rl_lower = readme.lower()
        signals = [
            "install",
            "usage",
            "example",
            "quickstart",
            "getting started",
            "contributing",
            "license",
            "badge",
            "##",
        ]
        doc_pts += min(10, sum(2 for s in signals if s in rl_lower))

    breakdown.append({
        "category": "Documentation",
        "points": min(25, doc_pts),
        "max": 25
    })

    # ── 2. Maintenance & activity (25 pts) ────────────────────────────────
    act_pts = 0
    days_since_push = _days_since(data.get("pushed_at", ""))

    if days_since_push < 30:
        act_pts += 10
    elif days_since_push < 180:
        act_pts += 6
    elif days_since_push < 365:
        act_pts += 2

    act_pts += min(10, _log_score(commit_count, 200, 10))

    if release_count > 0:
        act_pts += min(5, 2 + release_count)

    breakdown.append({
        "category": "Activity",
        "points": min(25, act_pts),
        "max": 25
    })

    # ── 3. Community & popularity (20 pts) ────────────────────────────────
    comm_pts = 0
    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)

    comm_pts += min(8, _log_score(stars, 500, 8))
    comm_pts += min(4, _log_score(forks, 100, 4))
    comm_pts += min(8, _log_score(contributor_count, 10, 8))

    breakdown.append({
        "category": "Community",
        "points": min(20, comm_pts),
        "max": 20
    })

    # ── 4. Project hygiene (20 pts) ───────────────────────────────────────
    hyg_pts = 0
    if data.get("description"):
        hyg_pts += 4
    if data.get("topics"):
        hyg_pts += min(4, len(data["topics"]) * 1)
    if has_license:
        hyg_pts += 5
    if has_ci:
        hyg_pts += 5
    if data.get("has_wiki"):
        hyg_pts += 2

    breakdown.append({
        "category": "Hygiene",
        "points": min(20, hyg_pts),
        "max": 20
    })

    # ── 5. Issue health (10 pts) ──────────────────────────────────────────
    issue_pts = 0
    if data.get("has_issues"):
        issue_pts += 2

        if stars > 0:
            ratio = open_issues / max(stars, 1)
            if ratio < 0.05:
                issue_pts += 8
            elif ratio < 0.15:
                issue_pts += 5
            elif ratio < 0.3:
                issue_pts += 2
        else:
            issue_pts += 4

    breakdown.append({
        "category": "Issue Health",
        "points": min(10, issue_pts),
        "max": 10
    })

    total = sum(b["points"] for b in breakdown)
    total = round(min(100, total), 1)

    strengths = []
    weaknesses = []
    rl_lower = readme.lower() if readme else ""

    # Documentation
    if breakdown[0]["points"] >= 18:
        strengths.append({
            "label": "Excellent documentation",
            "detail": "README is thorough with guides and examples."
        })
    elif breakdown[0]["points"] >= 10:
        strengths.append({
            "label": "Decent documentation",
            "detail": "README covers the basics."
        })
    else:
        if not readme:
            weaknesses.append({
                "label": "No README",
                "detail": "Add a README — it's the first thing visitors see."
            })
        else:
            weaknesses.append({
                "label": "Thin documentation",
                "detail": "README is too short or missing key sections (install, usage, examples)."
            })

    for kw, label in [
        ("install", "Installation guide"),
        ("usage", "Usage instructions"),
        ("contributing", "Contribution guide"),
        ("example", "Code examples"),
    ]:
        if kw in rl_lower:
            strengths.append({
                "label": label,
                "detail": f"README includes a {label.lower()} section."
            })
        elif readme and label in ["Installation guide", "Usage instructions"]:
            weaknesses.append({
                "label": f"Missing {label.lower()}",
                "detail": f"Add a {label.lower()} section to help new users."
            })

    # Activity
    if days_since_push < 30:
        strengths.append({
            "label": "Actively maintained",
            "detail": f"Last push was {days_since_push} day(s) ago."
        })
    elif days_since_push > 365:
        weaknesses.append({
            "label": "Stale repository",
            "detail": f"No pushes in {days_since_push // 30} months — may be abandoned."
        })

    if commit_count >= 200:
        strengths.append({
            "label": "Rich commit history",
            "detail": f"{commit_count:,} commits show sustained development."
        })
    elif commit_count < 10:
        weaknesses.append({
            "label": "Very few commits",
            "detail": "Less than 10 commits — project looks early-stage or inactive."
        })

    if release_count > 0:
        strengths.append({
            "label": "Versioned releases",
            "detail": f"{release_count} GitHub release(s) published."
        })
    else:
        weaknesses.append({
            "label": "No releases",
            "detail": "Publish versioned releases so users can track changes."
        })

    # Community
    if stars > 1000:
        strengths.append({
            "label": "Highly popular",
            "detail": f"⭐ {stars:,} stars — a well-known project."
        })
    elif stars > 100:
        strengths.append({
            "label": "Popular repository",
            "detail": f"⭐ {stars:,} stars."
        })

    if contributor_count >= 10:
        strengths.append({
            "label": "Strong contributor base",
            "detail": f"{contributor_count} contributors."
        })
    elif contributor_count == 1:
        weaknesses.append({
            "label": "Solo project",
            "detail": "Only 1 contributor — consider inviting collaborators."
        })

    # Hygiene
    if not data.get("description"):
        weaknesses.append({
            "label": "No description",
            "detail": "Add a one-line description to the repository settings."
        })

    if not data.get("topics"):
        weaknesses.append({
            "label": "No topics",
            "detail": "Add topics (tags) so GitHub can surface your repo in searches."
        })

    if has_license:
        strengths.append({
            "label": "License present",
            "detail": "Repository has an open-source license."
        })
    else:
        weaknesses.append({
            "label": "No license",
            "detail": "Without a license, others can't legally reuse your code."
        })

    if has_ci:
        strengths.append({
            "label": "CI/CD configured",
            "detail": "Automated tests or workflows detected."
        })
    else:
        weaknesses.append({
            "label": "No CI/CD",
            "detail": "Add GitHub Actions (or similar) to automate testing."
        })

    return total, strengths, weaknesses, breakdown


# ── Public API ────────────────────────────────────────────────────────────────

def analyze_repo(owner: str, repo: str, token: str | None = None) -> dict | None:
    data = get_repo_data(owner, repo, token)
    if data is None:
        return None

    structure = get_repo_structure(owner, repo, token)

    # Engineering analysis
    signals = detect_engineering_signals(structure)
    eng_strengths, eng_weaknesses = build_engineering_review(signals)
    engineering_score = calculate_engineering_score(signals)

    # Technology / dependency detection
    technologies = detect_technologies(structure)

    # Locate dependency files from full repo structure
    pyproject_path = find_file_in_structure(structure, ["pyproject.toml"])
    requirements_path = find_file_in_structure(structure, ["requirements.txt"])
    package_json_path = find_file_in_structure(structure, ["package.json"])

    pyproject_content = get_file_content(owner, repo, pyproject_path, token) if pyproject_path else ""
    requirements_content = get_file_content(owner, repo, requirements_path, token) if requirements_path else ""
    package_json_content = get_file_content(owner, repo, package_json_path, token) if package_json_path else ""

    frontend_stack = detect_frontend_stack(package_json_content)

    dependencies = detect_dependencies_from_files(
        pyproject_content,
        requirements_content,
        package_json_content,
    )

    # Repository metadata
    readme = get_readme_content(owner, repo, token)
    commit_count = get_commit_count(owner, repo, token)
    contributor_count = get_contributor_count(owner, repo, token)
    has_license = get_has_license(owner, repo, token)
    has_ci = get_has_ci(owner, repo, token)
    open_issues = get_open_issues_count(owner, repo, token)
    release_count = get_release_count(owner, repo, token)

    # Main score
    score, strengths, weaknesses, breakdown = compute_score(
        data,
        readme,
        commit_count,
        contributor_count,
        has_license,
        has_ci,
        open_issues,
        release_count,
    )

    # Repo health assessment
    assessment = generate_health_assessment({
        "score": score,
        "engineering_score": engineering_score,
        "contributors": contributor_count,
        "has_ci": has_ci,
        "releases": release_count,
        "open_issues": open_issues,
        "engineering_weaknesses": eng_weaknesses,
    })

    # Recommendations
    recommendations = generate_recommendations({
        "engineering_signals": signals,
        "open_issues": open_issues,
        "releases": release_count,
    })

    return {
        "name": data["name"],
        "full_name": data.get("full_name", f"{owner}/{repo}"),
        "description": data.get("description") or "No description",
        "language": data.get("language") or "Unknown",
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "open_issues": open_issues,
        "commits": commit_count,
        "structure": structure,
        "contributors": contributor_count,
        "releases": release_count,
        "topics": data.get("topics", []),
        "license": data.get("license", {}).get("spdx_id", "None") if data.get("license") else "None",
        "has_ci": has_ci,
        "pushed_at": data.get("pushed_at", ""),
        "created_at": data.get("created_at", ""),
        "homepage": data.get("homepage") or "",
        "score": score,
        "breakdown": breakdown,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "readme_length": len(readme),
        "engineering_signals": signals,
        "engineering_strengths": eng_strengths,
        "engineering_weaknesses": eng_weaknesses,
        "engineering_score": engineering_score,
        "technologies": technologies,
        "dependencies": dependencies,
        "frontend_stack": frontend_stack,
        "assessment": assessment,
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    owner = input("Enter owner: ")
    repo = input("Enter repository: ")

    result = analyze_repo(owner, repo)

    if result:
        print(f"\n{'=' * 50}")
        print(f"  {result['full_name']}  —  Score: {result['score']}/100")
        print(f"{'=' * 50}")

        for b in result["breakdown"]:
            bar = "█" * int(b["points"] / b["max"] * 20)
            print(f"  {b['category']:<18} {bar:<20} {b['points']:.1f}/{b['max']}")

        print(f"\n✅ Strengths ({len(result['strengths'])}):")
        for s in result["strengths"]:
            print(f"  + {s['label']}: {s['detail']}")

        print(f"\n⚠ Weaknesses ({len(result['weaknesses'])}):")
        for w in result["weaknesses"]:
            print(f"  - {w['label']}: {w['detail']}")
    else:
        print("Repository not found.")