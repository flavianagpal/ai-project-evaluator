import requests


def get_repo_structure(owner, repo, token=None):
    """
    Fetches the top-level repository structure using
    GitHub's Contents API.

    Returns:
        List of file/folder names
        Example:
        [
            "README.md",
            "Dockerfile",
            "tests",
            ".github"
        ]
    """

    url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            return []

        data = response.json()

        structure = []

        for item in data:
            structure.append(item["name"])

        return sorted(structure)

    except Exception:
        return []
    
if __name__ == "__main__":
    files = get_repo_structure(
        "streamlit",
        "streamlit"
    )

    print(files)