def detect_technologies(structure):
    """
    Detect high-level technologies from a repository file tree.

    Returns:
        {
            "backend": [...],
            "frontend": [...],
            "infrastructure": [...]
        }
    """
    tech = {
        "backend": [],
        "frontend": [],
        "infrastructure": []
    }

    structure_lower = [item.lower() for item in structure]


    if any(
        item.endswith("requirements.txt")
        or item.endswith("pyproject.toml")
        or item.endswith("setup.py")
        or item.endswith("manage.py")
        or item.endswith("poetry.lock")
        for item in structure_lower
    ):
        tech["backend"].append("Python")

    if any(
        item.endswith("pom.xml")
        or item.endswith("build.gradle")
        or item.endswith("build.gradle.kts")
        or item.endswith("mvnw")
        for item in structure_lower
    ):
        tech["backend"].append("Java")

    if any(
        item.endswith("cargo.toml")
        or item.endswith("cargo.lock")
        for item in structure_lower
    ):
        tech["backend"].append("Rust")

    if any(
        item.endswith("go.mod")
        or item.endswith("go.sum")
        for item in structure_lower
    ):
        tech["backend"].append("Go")

    if any(
        item.endswith("gemfile")
        or item.endswith("gemfile.lock")
        for item in structure_lower
    ):
        tech["backend"].append("Ruby")

    if any(
        item.endswith("composer.json")
        for item in structure_lower
    ):
        tech["backend"].append("PHP")

   
    has_node = any(
        item.endswith("package.json")
        or item.endswith("package-lock.json")
        or item.endswith("yarn.lock")
        or item.endswith("pnpm-lock.yaml")
        for item in structure_lower
    )

    if has_node:
        tech["frontend"].append("Node.js")

    # Frontend framework hints from repo structure
    if any("next.config" in item for item in structure_lower):
        tech["frontend"].append("Next.js")

    if any("vite.config" in item for item in structure_lower):
        tech["frontend"].append("Vite")

    if any("tailwind.config" in item for item in structure_lower):
        tech["frontend"].append("Tailwind CSS")

   
    if any(
        "src/app.tsx" in item
        or "src/index.tsx" in item
        or "src/app.jsx" in item
        or "src/index.jsx" in item
        for item in structure_lower
    ):
        tech["frontend"].append("React")

    if any("angular.json" in item for item in structure_lower):
        tech["frontend"].append("Angular")

    if any("nuxt.config" in item or "vue.config" in item for item in structure_lower):
        tech["frontend"].append("Vue")

    
    if any(
        "dockerfile" in item
        or "docker-compose" in item
        or "compose.yml" in item
        or "compose.yaml" in item
        or ".dockerignore" in item
        or ".devcontainer" in item
        for item in structure_lower
    ):
        tech["infrastructure"].append("Docker")

    if any(
        ".github/workflows" in item
        or item == ".github"
        for item in structure_lower
    ):
        tech["infrastructure"].append("GitHub Actions")

    if any("vercel.json" in item for item in structure_lower):
        tech["infrastructure"].append("Vercel")

    if any(
        "k8s/" in item
        or "kubernetes" in item
        or "helm/" in item
        or "chart.yaml" in item
        for item in structure_lower
    ):
        tech["infrastructure"].append("Kubernetes")

   
    tech["backend"] = sorted(set(tech["backend"]))
    tech["frontend"] = sorted(set(tech["frontend"]))
    tech["infrastructure"] = sorted(set(tech["infrastructure"]))

    return tech


if __name__ == "__main__":
    sample = [
        "README.md",
        "backend/requirements.txt",
        "frontend/package.json",
        "frontend/next.config.js",
        ".github/workflows/test.yml",
        "docker/Dockerfile"
    ]

    print(detect_technologies(sample))