import requests


def get_file_content(owner, repo, filepath, token=None):

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

    if "download_url" not in data:
        return None

    raw = requests.get(
        data["download_url"],
        timeout=10
    )

    return raw.text

def detect_dependencies(text):

    found = []

    if not text:
        return found

    text = text.lower()

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
        "scikit-learn": "Scikit-Learn"
    }

    for key, label in checks.items():

        if key in text:
            found.append(label)

    return sorted(found)

def detect_frontend_stack(text):

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
        "vite": "Vite"
    }

    for key, label in checks.items():
        if key in text:
            found.append(label)

    return sorted(found)

if __name__ == "__main__":

    content = get_file_content(
        "streamlit",
        "streamlit",
        "pyproject.toml"
    )

    print(content[:500])

    print(
        detect_dependencies(content)
    )