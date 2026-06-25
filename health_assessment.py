def generate_health_assessment(result):
    score = result["score"]

    positives = []
    concerns = []

    # Positives
    if result["engineering_score"] >= 80:
        positives.append("Strong engineering practices")

    if result["contributors"] >= 5:
        positives.append("Healthy contributor community")

    if result["has_ci"]:
        positives.append("CI/CD automation configured")

    if result["releases"] >= 5:
        positives.append("Regular releases")

    # Risks
    if result["open_issues"] > 1000:
        concerns.append("Very large backlog of open issues")
    elif result["open_issues"] > 300:
        concerns.append("Moderate issue backlog")

    if len(result["engineering_weaknesses"]) >= 2:
        concerns.append("Multiple engineering gaps detected")

    # Verdict
    if score >= 80 and len(concerns) == 0:
        verdict = "Excellent Repository"
    elif score >= 70 and len(concerns) <= 1:
        verdict = "Good Repository"
    elif score >= 50:
        verdict = "Average Repository"
    else:
        verdict = "High Risk Repository"

    return {
        "verdict": verdict,
        "positives": positives,
        "concerns": concerns
    }