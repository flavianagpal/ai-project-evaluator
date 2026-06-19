def calculate_engineering_score(signals):

    score = 0

    if signals["has_tests"]:
        score += 20

    if signals["has_docs"]:
        score += 20

    if signals["has_ci"]:
        score += 20

    if signals["has_docker"]:
        score += 20

    if signals["has_dependency_management"]:
        score += 20

    return score

if __name__ == "__main__":

    signals = {
        "has_tests": True,
        "has_docs": True,
        "has_ci": True,
        "has_docker": False,
        "has_dependency_management": True
    }

    print(calculate_engineering_score(signals))