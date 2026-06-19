def detect_engineering_signals(structure):

    structure_set = {item.lower() for item in structure}

    signals = {
        "has_tests": False,
        "has_docs": False,
        "has_ci": False,
        "has_docker": False,
        "has_dependency_management": False,
    }

    # Tests
    test_indicators = {
    "tests",
    "test",
    "__tests__",
    "specs",
    "spec",
    "e2e",
    "e2e_playwright",
    "integration_tests",
    "unit_tests"}

    if any(item in structure_set for item in test_indicators):
        signals["has_tests"] = True 

    # Documentation
    doc_indicators = {
    "docs",
    "wiki",
    "documentation"}

    if any(item in structure_set for item in doc_indicators):
        signals["has_docs"] = True 

    # CI/CD
    ci_indicators = {
    ".github",
    ".gitlab-ci.yml",
    ".circleci"}

    if any(item in structure_set for item in ci_indicators):
        signals["has_ci"] = True
    # Docker
    if (
        "dockerfile" in structure_set
        or "docker-compose.yml" in structure_set
    ):
        signals["has_docker"] = True

    # Dependency management
    dependency_files = {
        "requirements.txt",
        "pyproject.toml",
        "poetry.lock",
        "package.json",
        "pom.xml",
        "cargo.toml"
    }

    if any(f in structure_set for f in dependency_files):
        signals["has_dependency_management"] = True

    return signals

if __name__ == "__main__":

    sample = [
        ".github",
        "README.md",
        "tests",
        "Dockerfile",
        "pyproject.toml",
        "wiki"
    ]

    print(detect_engineering_signals(sample))