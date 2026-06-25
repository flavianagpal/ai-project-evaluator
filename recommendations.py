def generate_recommendations(result):
    recommendations = []

    if not result["engineering_signals"]["has_tests"]:
        recommendations.append(
            "Add automated tests using pytest or unittest."
        )

    if not result["engineering_signals"]["has_ci"]:
        recommendations.append(
            "Set up GitHub Actions for CI/CD automation."
        )

    if not result["engineering_signals"]["has_docker"]:
        recommendations.append(
            "Add a Dockerfile for easier deployment."
        )

    if not result["engineering_signals"]["has_docs"]:
        recommendations.append(
            "Improve project documentation and usage guides."
        )

    if result["open_issues"] > 500:
        recommendations.append(
            "Review and triage the large backlog of open issues."
        )

    if result["releases"] == 0:
        recommendations.append(
            "Publish versioned releases for easier adoption."
        )

    return recommendations