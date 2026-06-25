import requests


def get_file_content(owner, repo, filepath, token=None):
    """
    Fetch a file from a GitHub repository using the contents API.
    Returns the raw text content, or None if the file doesn't exist.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filepath}"

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    if response.status_code != 200:
        return None

    data = response.json()

    if "download_url" not in data or not data["download_url"]:
        return None

    raw = requests.get(
        data["download_url"],
        timeout=10
    )

    if raw.status_code != 200:
        return None

    return raw.text


def detect_dependencies(text):
    """
    Lightweight dependency detector from a raw text file.
    Kept mainly for local testing / fallback use.
    RepoLens production flow uses dependency_detector.py for main library detection.
    """
    if not text:
        return []

    text = text.lower()
    found = []

    checks = {
        "streamlit": "Streamlit",
        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "plotly": "Plotly",
        "langchain": "LangChain",
        "openai": "OpenAI",
        "transformers": "Transformers",
        "torch": "PyTorch",
        "tensorflow": "TensorFlow",
        "scikit-learn": "Scikit-Learn",
    }

    for key, label in checks.items():
        if key in text:
            found.append(label)

    return sorted(set(found))


def detect_frontend_stack(text):
    """
    Detect common frontend technologies from package.json content.
    """
    if not text:
        return []

    text = text.lower()
    found = []

    checks = {
        "react": "React",
        "next": "Next.js",
        "vue": "Vue",
        "angular": "Angular",
        "typescript": "TypeScript",
        "tailwind": "Tailwind CSS",
        "vite": "Vite",
    }

    for key, label in checks.items():
        if key in text:
            found.append(label)

    return sorted(set(found))


if __name__ == "__main__":
    content = get_file_content(
        "streamlit",
        "streamlit",
        "pyproject.toml"
    )

    if content:
        print(content[:500])
        print(detect_dependencies(content))
    else:
        print("File not found.")