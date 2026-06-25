def detect_engineering_signals(structure):
    """
    Detect engineering quality signals from a repository file tree.

    `structure` is expected to be a list of file and folder paths,
    for example:
        [
            "README.md",
            ".github/workflows/test.yml",
            "frontend/package.json",
            "backend/requirements.txt",
            "tests/test_app.py"
        ]
    """

    structure_set = {item.lower() for item in structure}

    signals = {
        "has_tests": False,
        "has_docs": False,
        "has_ci": False,
        "has_docker": False,
        "has_dependency_management": False
    }

    # --------------------------------------------------
    # Tests
    # --------------------------------------------------
    test_indicators = [
        "tests",
        "test",
        "__tests__",
        "specs",
        "spec",
        "e2e",
        "e2e_playwright",
        "integration_tests",
        "unit_tests",
        "pytest.ini",
        "tox.ini"
    ]

    if any(
        any(indicator in path for indicator in test_indicators)
        for path in structure_set
    ):
        signals["has_tests"] = True

    # --------------------------------------------------
    # Documentation
    # --------------------------------------------------
    doc_indicators = [
        "readme",
        "docs",
        "wiki",
        "documentation",
        "contributing.md",
        "contributing",
        "security.md",
        "code_of_conduct.md"
    ]

    if any(
        any(indicator in path for indicator in doc_indicators)
        for path in structure_set
    ):
        signals["has_docs"] = True

    # --------------------------------------------------
    # CI / CD
    # --------------------------------------------------
    ci_indicators = [
        ".github/workflows",
        ".gitlab-ci.yml",
        ".circleci",
        "azure-pipelines.yml",
        "jenkinsfile",
        ".travis.yml"
    ]

    if any(
        any(indicator in path for indicator in ci_indicators)
        for path in structure_set
    ):
        signals["has_ci"] = True

    # --------------------------------------------------
    # Docker / Containerization
    # --------------------------------------------------
    docker_indicators = [
        "dockerfile",
        "docker-compose",
        "compose.yml",
        "compose.yaml",
        ".dockerignore",
        ".devcontainer"
    ]

    if any(
        any(indicator in path for indicator in docker_indicators)
        for path in structure_set
    ):
        signals["has_docker"] = True

    # --------------------------------------------------
    # Dependency Management
    # --------------------------------------------------
    dependency_indicators = [
        "requirements.txt",
        "pyproject.toml",
        "poetry.lock",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "pom.xml",
        "cargo.toml",
        "cargo.lock",
        "go.mod",
        "composer.json"
    ]

    if any(
        any(indicator in path for indicator in dependency_indicators)
        for path in structure_set
    ):
        signals["has_dependency_management"] = True

    return signals


if __name__ == "__main__":
    sample = [
        "README.md",
        ".github/workflows/test.yml",
        "backend/requirements.txt",
        "tests/test_app.py",
        "docker/Dockerfile",
        "docs/index.md"
    ]

    print(detect_engineering_signals(sample))