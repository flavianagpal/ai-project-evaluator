import requests


def get_repo_structure(owner, repo, token=None):
    """
    Fetch the full repository file tree using GitHub's Git Trees API.

    Returns:
        List of file and folder paths, for example:
        [
            "README.md",
            ".github/workflows/test.yml",
            "frontend/package.json",
            "backend/requirements.txt",
            "tests/test_app.py"
        ]
    """
    headers = {
        "Accept": "application/vnd.github+json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        # Step 1: get default branch info
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        repo_response = requests.get(
            repo_url,
            headers=headers,
            timeout=10
        )

        if repo_response.status_code != 200:
            return []

        repo_data = repo_response.json()
        default_branch = repo_data.get("default_branch", "main")

        # Step 2: fetch recursive tree for that branch
        tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
        tree_response = requests.get(
            tree_url,
            headers=headers,
            timeout=10
        )

        if tree_response.status_code != 200:
            return []

        tree_data = tree_response.json()
        tree = tree_data.get("tree", [])

        structure = []
        seen_dirs = set()

        for item in tree:
            path = item.get("path")
            if not path:
                continue

            structure.append(path)

            # Also add parent directory names so detectors can still match
            # things like ".github", "docs", "tests", etc.
            parts = path.split("/")
            for i in range(1, len(parts)):
                seen_dirs.add("/".join(parts[:i]))

        structure.extend(seen_dirs)

        return sorted(set(structure))

    except Exception:
        return []


if __name__ == "__main__":
    files = get_repo_structure(
        "streamlit",
        "streamlit"
    )

    print(files[:100])