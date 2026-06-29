from groq import Groq
import json

from config import GROQ_API_KEY, GROQ_MODEL


client = Groq(api_key=GROQ_API_KEY)


def build_prompt(result):
    strengths_fmt = "\n".join(
        f"  - {s}" for s in result["engineering_strengths"]
    ) or "  None detected"

    weaknesses_fmt = "\n".join(
        f"  - {w}" for w in result["engineering_weaknesses"]
    ) or "  None detected"

    recommendations_fmt = "\n".join(
        f"  - {r}" for r in result["recommendations"]
    ) or "  None"

    deps_fmt = ", ".join(result["dependencies"]) or "None detected"

    tech = result["technologies"]
    tech_fmt = (
        f"  Backend: {', '.join(tech.get('backend', [])) or 'N/A'}\n"
        f"  Frontend: {', '.join(tech.get('frontend', [])) or 'N/A'}\n"
        f"  Infrastructure: {', '.join(tech.get('infrastructure', [])) or 'N/A'}"
    )

    return f"""You are a senior software architect with 15+ years of experience evaluating open-source and production-grade repositories.

Analyze the GitHub repository data below and return a detailed, opinionated, and actionable assessment.

Rules:
- Use ONLY the data provided. Never invent facts or metrics.
- Be specific — reference the actual scores, languages, dependencies, and signals.
- Write in a clear, professional tone. Avoid generic filler phrases like "overall this is a good repo."
- Each field should be substantive: 3–5 sentences minimum.
- Return ONLY valid JSON matching the exact schema below.

JSON schema:
{{
    "executive_summary": "3–5 sentence overview covering what the repo does, its maturity level, community traction, and whether it is production-ready. Reference the score and key signals.",
    "engineering_assessment": "3–5 sentences on code quality signals, tech stack choices, dependency health, CI/CD, test coverage, and what the engineering score reflects. Be specific about what is strong and what is lacking.",
    "risks": ["Specific risk 1 with context", "Specific risk 2 with context", "..."],
    "recommendation": "2–4 sentences on whether to adopt, contribute to, fork, or avoid this repository — and under what conditions. Be direct and actionable."
}}

--- REPOSITORY DATA ---

Name: {result["name"]}
Description: {result["description"]}
Primary Language: {result["language"]}
License: {result.get("license", "Unknown")}

Scores:
  Overall: {result["score"]}/100
  Engineering: {result["engineering_score"]}/100

Community Metrics:
  Stars: {result["stars"]}
  Forks: {result["forks"]}
  Contributors: {result["contributors"]}
  Open Issues: {result["open_issues"]}
  Releases: {result["releases"]}

Technology Stack:
{tech_fmt}

Key Dependencies: {deps_fmt}

Engineering Strengths:
{strengths_fmt}

Engineering Weaknesses:
{weaknesses_fmt}

Health Verdict: {result["assessment"]["verdict"]}

Positives Detected:
{chr(10).join(f"  - {p}" for p in result["assessment"]["positives"]) or "  None"}

Concerns Detected:
{chr(10).join(f"  - {c}" for c in result["assessment"]["concerns"]) or "  None"}

Recommendations:
{recommendations_fmt}
"""


def call_groq(prompt):
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert software architect. "
                    "You write detailed, specific, and actionable repository assessments. "
                    "You always return valid JSON and never include markdown formatting or code fences."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return response.choices[0].message.content


def generate_ai_summary(result):
    try:
        prompt = build_prompt(result)
        response = call_groq(prompt)
        parsed = json.loads(response)

        # Ensure all expected keys exist with fallbacks
        return {
            "executive_summary": parsed.get("executive_summary", "Not available."),
            "engineering_assessment": parsed.get("engineering_assessment", "Not available."),
            "risks": parsed.get("risks", []),
            "recommendation": parsed.get("recommendation", "Not available."),
        }

    except Exception as e:
        return {
            "executive_summary": f"AI analysis could not be completed ({e}).",
            "engineering_assessment": "Engineering assessment unavailable.",
            "risks": ["AI analysis failed — review the repository manually."],
            "recommendation": "Run the analysis again or inspect the repository directly on GitHub.",
        }