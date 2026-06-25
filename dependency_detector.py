import json
import re
import tomllib


def _normalize_package_name(dep: str) -> str:
    """
    Convert a dependency string like:
    - fastapi>=0.100
    - torch==2.0
    - pandas[performance]>=2.0
    - scikit-learn ~= 1.5
    into a clean package name.
    """
    dep = dep.strip().lower()

    # Remove version specifiers
    dep = re.split(r"[<>=!~]", dep)[0].strip()

    # Remove extras like pandas[performance]
    dep = dep.split("[")[0].strip()

    return dep


def detect_dependencies_from_files(
    pyproject_content="",
    requirements_content="",
    package_json_content=""
):
    deps = []
    packages = set()

    known_python_packages = {
        "numpy": "NumPy",
        "pandas": "Pandas",
        "plotly": "Plotly",
        "streamlit": "Streamlit",
        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",
        "uvicorn": "Uvicorn",
        "pydantic": "Pydantic",
        "starlette": "Starlette",
        "langchain": "LangChain",
        "openai": "OpenAI",
        "transformers": "Transformers",
        "torch": "PyTorch",
        "tensorflow": "TensorFlow",
        "scikit-learn": "Scikit-Learn",
        "celery": "Celery",
        "sqlalchemy": "SQLAlchemy",
        "pytest": "Pytest",
        "alembic": "Alembic",
    }

    frontend_packages = {
        "react": "React",
        "next": "Next.js",
        "vue": "Vue",
        "@angular/core": "Angular",
        "typescript": "TypeScript",
        "tailwindcss": "Tailwind CSS",
        "vite": "Vite",
        "redux": "Redux",
        "svelte": "Svelte",
    }

    # --------------------------------------------------
    # Parse pyproject.toml
    # --------------------------------------------------
    if pyproject_content:
        try:
            data = tomllib.loads(pyproject_content)

            # PEP 621 style: [project.dependencies]
            project_dependencies = (
                data.get("project", {})
                .get("dependencies", [])
            )

            for dep in project_dependencies:
                package_name = _normalize_package_name(dep)
                if package_name:
                    packages.add(package_name)

            # Poetry style: [tool.poetry.dependencies]
            poetry_dependencies = (
                data.get("tool", {})
                .get("poetry", {})
                .get("dependencies", {})
            )

            for dep_name in poetry_dependencies.keys():
                package_name = _normalize_package_name(dep_name)
                if package_name and package_name != "python":
                    packages.add(package_name)

        except Exception:
            pass

        # Fallback: keyword scan if structured parse didn't find anything
        if not packages:
            text = pyproject_content.lower()

            for package in known_python_packages:
                if package in text:
                    packages.add(package)

    # --------------------------------------------------
    # Parse requirements.txt
    # --------------------------------------------------
    if requirements_content:
        for line in requirements_content.splitlines():
            line = line.strip().lower()

            if not line or line.startswith("#"):
                continue

            package_name = _normalize_package_name(line)
            if package_name:
                packages.add(package_name)

    # --------------------------------------------------
    # Convert Python package names to display labels
    # --------------------------------------------------
    for package, display_name in known_python_packages.items():
        if package in packages:
            deps.append(display_name)

    # --------------------------------------------------
    # Parse package.json properly
    # --------------------------------------------------
    if package_json_content:
        try:
            data = json.loads(package_json_content)

            all_js_deps = {}

            dependencies = data.get("dependencies", {})
            dev_dependencies = data.get("devDependencies", {})

            if isinstance(dependencies, dict):
                all_js_deps.update(dependencies)

            if isinstance(dev_dependencies, dict):
                all_js_deps.update(dev_dependencies)

            for package_name in all_js_deps.keys():
                key = package_name.lower()
                if key in frontend_packages:
                    deps.append(frontend_packages[key])

        except Exception:
            # fallback to plain text scan
            text = package_json_content.lower()

            for key, label in frontend_packages.items():
                if f'"{key}"' in text:
                    deps.append(label)

    return sorted(set(deps))


if __name__ == "__main__":
    sample_requirements = """
    fastapi==0.110.0
    uvicorn>=0.29.0
    pydantic==2.6.0
    sqlalchemy==2.0.0
    """

    print(
        detect_dependencies_from_files(
            requirements_content=sample_requirements
        )
    )