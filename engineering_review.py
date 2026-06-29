def build_engineering_review(signals):
    """
    Convert engineering signal booleans into human-readable strengths and gaps.
    """

    strengths = []
    weaknesses = []

    
    if signals.get("has_tests", False):
        strengths.append("Automated testing infrastructure detected")
    else:
        weaknesses.append("No automated test suite detected in the repository tree")

   
    if signals.get("has_docs", False):
        strengths.append("Documentation resources and contributor guidance are present")
    else:
        weaknesses.append("Documentation resources were not clearly detected")

    
    if signals.get("has_ci", False):
        strengths.append("CI/CD workflow configuration detected")
    else:
        weaknesses.append("No CI/CD workflow configuration detected")

    
    if signals.get("has_docker", False):
        strengths.append("Containerization or development environment support detected")
    else:
        weaknesses.append("No Docker or dev-container configuration detected")

    
    if signals.get("has_dependency_management", False):
        strengths.append("Dependency management files are configured")
    else:
        weaknesses.append("Dependency management files were not detected")

    return strengths, weaknesses


if __name__ == "__main__":
    signals = {
        "has_tests": True,
        "has_docs": True,
        "has_ci": True,
        "has_docker": False,
        "has_dependency_management": True,
    }

    strengths, weaknesses = build_engineering_review(signals)

    print("Strengths:")
    for item in strengths:
        print("-", item)

    print("\nWeaknesses:")
    for item in weaknesses:
        print("-", item)