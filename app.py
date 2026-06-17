import requests
import base64


def get_readme(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"

    response = requests.get(url)

    return response.status_code == 200


def get_readme_content(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"

    response = requests.get(url)

    if response.status_code != 200:
        return ""

    data = response.json()

    content = base64.b64decode(
        data["content"]
    ).decode("utf-8")

    return content


owner = input("Enter owner: ")
repo = input("Enter repository: ")

url = f"https://api.github.com/repos/{owner}/{repo}"

response = requests.get(url)

if response.status_code != 200:
    print("Repository not found")

else:
    data = response.json()

    has_readme = get_readme(owner, repo)

    readme_content = get_readme_content(owner, repo)

    print("README Exists:", has_readme)
    print("README Length:", len(readme_content))

    print("\nDEBUG INFO")
    print("Created:", data["created_at"])
    print("Updated:", data["updated_at"])
    print("Open Issues:", data["open_issues_count"])
    print("Topics:", data["topics"])
    print("Repository Size:", data["size"])

    # ==========================
    # CATEGORY SCORES
    # ==========================

    documentation_score = 0
    popularity_score = 0
    activity_score = 0

    # Documentation Score (/30)

    if has_readme:
        documentation_score += 10

    if len(readme_content) > 1000:
        documentation_score += 10

    if data["description"]:
        documentation_score += 5

    if len(data["topics"]) > 0:
        documentation_score += 5

    # Popularity Score (/30)

    if data["stargazers_count"] > 10:
        popularity_score += 10

    if data["stargazers_count"] > 100:
        popularity_score += 10

    if data["forks_count"] > 10:
        popularity_score += 10

    # Activity Score (/40)

    if data["open_issues_count"] > 0:
        activity_score += 10

    if data["updated_at"]:
        activity_score += 30

    total_score = (
        documentation_score
        + popularity_score
        + activity_score
    )

    print("\nRepository Analysis")
    print("--------------------")

    print("Name:", data["name"])
    print("Description:", data["description"])
    print("Language:", data["language"])
    print("Stars:", data["stargazers_count"])
    print("Forks:", data["forks_count"])

    print("\nEvaluation Report")
    print("--------------------")

    print("Documentation Score:", documentation_score, "/30")
    print("Popularity Score:", popularity_score, "/30")
    print("Activity Score:", activity_score, "/40")

    print("\nOverall Score:", total_score, "/100")