def build_engineering_review(signals):

    strengths = []
    weaknesses = []

    if signals["has_tests"]:
        strengths.append("Automated testing detected")
    else:
        weaknesses.append("No automated tests detected")

    if signals["has_docs"]:
        strengths.append("Documentation resources present")
    else:
        weaknesses.append("Documentation not detected")

    if signals["has_ci"]:
        strengths.append("CI/CD workflows configured")
    else:
        weaknesses.append("No CI/CD workflows detected")

    if signals["has_docker"]:
        strengths.append("Containerization support available")
    else:
        weaknesses.append("Docker configuration not detected")

    if signals["has_dependency_management"]:
        strengths.append("Dependency management configured")
    else:
        weaknesses.append("Dependency management not detected")

    return strengths, weaknesses

if __name__ == "__main__":

    signals = {
        "has_tests": True,
        "has_docs": True,
        "has_ci": True,
        "has_docker": False,
        "has_dependency_management": True,
    }

    print(build_engineering_review(signals))