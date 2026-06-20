def detect_technologies(structure):

    tech = {
        "backend": [],
        "frontend": [],
        "infrastructure": []
    }

    structure_set = set(structure)

    if (
        "requirements.txt" in structure_set
        or "pyproject.toml" in structure_set
    ):
        tech["backend"].append("Python")

    if "package.json" in structure_set:
        tech["frontend"].append("Node.js")

    if "Dockerfile" in structure_set:
        tech["infrastructure"].append("Docker")

    if ".github" in structure_set:
        tech["infrastructure"].append("GitHub Actions")

    return tech


if __name__ == "__main__":

    structure = [
        "README.md",
        "Dockerfile",
        ".github",
        "pyproject.toml"
    ]

    print(
        detect_technologies(structure)
    )