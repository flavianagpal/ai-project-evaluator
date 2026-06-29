import streamlit as st
from datetime import datetime, timezone

from app import analyze_repo
from charts import radar_chart, bar_chart

from ui_components import (
    section_header,
    metric_card,
    render_score_badge,
    render_tags,
    render_signal_checklist,
    render_note_cards,
    render_verdict_card,
    render_findings,
    render_ai_cards,
)


st.set_page_config(
    page_title="RepoLens · GitHub Repository Intelligence",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# CSS
# --------------------------------------------------

def load_css():
    try:
        with open("style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("style.css not found. UI loaded without custom styling.")


load_css()


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def score_class(score):
    if score >= 80:
        return "score-excellent"
    if score >= 60:
        return "score-good"
    if score >= 40:
        return "score-fair"
    return "score-poor"


def fmt_number(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def days_ago(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        d = (datetime.now(timezone.utc) - dt).days
        if d == 0:
            return "today"
        if d == 1:
            return "yesterday"
        if d < 30:
            return f"{d}d ago"
        if d < 365:
            return f"{d // 30}mo ago"
        return f"{d // 365}y ago"
    except Exception:
        return "unknown"


def render_score_explanation(result):
    score = result["score"]

    if score >= 80:
        verdict_color = "#34d399"
        verdict = "Excellent Repository"
    elif score >= 65:
        verdict_color = "#6C8EFF"
        verdict = "Good Repository"
    elif score >= 50:
        verdict_color = "#fbbf24"
        verdict = "Average Repository"
    else:
        verdict_color = "#f87171"
        verdict = "Needs Improvement"

    st.markdown(f"""
    <div class="dashboard-card">
        <div class="repo-title">Overall Repository Score</div>
        <div class="repo-desc">
            RepoLens computes the overall score using weighted repository health
            metrics including documentation, activity, community, hygiene, and issue health.
        </div>
        <div style="margin-top:1rem;padding:1rem 1.1rem;border-left:3px solid {verdict_color};
                    background:rgba(255,255,255,.03);border-radius:8px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;
                         font-weight:700;color:{verdict_color};">{score}/100</span>
            <span style="color:#7b93b8;font-size:.9rem;margin-left:.6rem;">— {verdict}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Category Breakdown")

    bars_html = ""
    for item in result["breakdown"]:
        pct = round((item["points"] / item["max"]) * 100)
        if pct >= 80:
            color = "#34d399"
        elif pct >= 60:
            color = "#6C8EFF"
        elif pct >= 40:
            color = "#fbbf24"
        else:
            color = "#f87171"

        bars_html += (
            f'<div style="margin-bottom:.85rem;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem;">'
            f'<span style="font-size:.82rem;font-weight:500;color:#c7d4f0;">{item["category"]}</span>'
            f'<span style="font-size:.78rem;font-family:JetBrains Mono,monospace;color:{color};font-weight:600;">'
            f'{item["points"]:.0f}<span style="color:#435975;">/{item["max"]}</span></span>'
            f'</div>'
            f'<div style="background:#213044;border-radius:999px;height:6px;overflow:hidden;">'
            f'<div style="width:{pct}%;height:100%;background:{color};border-radius:999px;"></div>'
            f'</div>'
            f'</div>'
        )

    legend_html = (
        '<div style="display:flex;flex-wrap:wrap;gap:.5rem 1.2rem;margin-top:1.1rem;'
        'padding-top:.9rem;border-top:1px solid rgba(99,155,255,.1);">'
        '<span style="font-size:.78rem;color:#7b93b8;display:flex;align-items:center;gap:5px;">'
        '<span style="width:8px;height:8px;border-radius:50%;background:#34d399;display:inline-block;"></span>80–100 Excellent</span>'
        '<span style="font-size:.78rem;color:#7b93b8;display:flex;align-items:center;gap:5px;">'
        '<span style="width:8px;height:8px;border-radius:50%;background:#6C8EFF;display:inline-block;"></span>60–79 Good</span>'
        '<span style="font-size:.78rem;color:#7b93b8;display:flex;align-items:center;gap:5px;">'
        '<span style="width:8px;height:8px;border-radius:50%;background:#fbbf24;display:inline-block;"></span>40–59 Average</span>'
        '<span style="font-size:.78rem;color:#7b93b8;display:flex;align-items:center;gap:5px;">'
        '<span style="width:8px;height:8px;border-radius:50%;background:#f87171;display:inline-block;"></span>Below 40 Needs work</span>'
        '</div>'
    )

    st.markdown(
        f'<div class="dashboard-card" style="margin-top:.5rem;">{bars_html}{legend_html}</div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# Hero
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-badge">GitHub Repository Intelligence</div>
    <h1>RepoLens</h1>
    <p>
        Evaluate any public GitHub repository across activity, maintainability,
        engineering practices, ecosystem signals, and project health — all in one dashboard.
    </p>
</div>
""", unsafe_allow_html=True)

input_col, button_col = st.columns([5, 1.3])

with input_col:
    repo_input = st.text_input(
        "GitHub Repository",
        placeholder="e.g. streamlit/streamlit",
        label_visibility="collapsed",
    )

with button_col:
    st.write("")
    analyze_clicked = st.button("Analyze →", use_container_width=True)

with st.expander("GitHub token (optional — raises API rate limits)"):
    token = st.text_input(
        "Personal access token",
        type="password",
        placeholder="ghp_...",
        label_visibility="collapsed",
    )
    st.caption("A read-only token is enough. Used only for GitHub API requests and never stored.")

token = token.strip() if token else None


# --------------------------------------------------
# Analysis
# --------------------------------------------------

if analyze_clicked:
    repo_value = repo_input.strip()

    if not repo_value or repo_value.count("/") != 1:
        st.warning("Enter a repository in the format owner/repo — for example streamlit/streamlit.")
    else:
        owner, repo = repo_value.split("/", 1)

        with st.spinner("Analyzing repository..."):
            result = analyze_repo(owner.strip(), repo.strip(), token or None)

        if result is None:
            st.error("Repository not found, API limit reached, or data could not be fetched.")
        else:
            score      = result["score"]
            cls        = score_class(score)
            assessment = result["assessment"]

            # --------------------------------------------------
            # Overview
            # --------------------------------------------------
            section_header("Overview")

            c0, c1, c2, c3, c4, c5 = st.columns([1.25, 1, 1, 1, 1, 1])

            with c0:
                render_score_badge(score, cls)

            metric_items = [
                (result["engineering_score"], "Engineering"),
                (fmt_number(result["stars"]),  "Stars"),
                (fmt_number(result["forks"]),  "Forks"),
                (str(result["contributors"]),  "Contributors"),
                (str(result["open_issues"]),   "Open Issues"),
            ]

            for col, (val, lbl) in zip([c1, c2, c3, c4, c5], metric_items):
                with col:
                    metric_card(val, lbl)

            # --------------------------------------------------
            # Executive Summary
            # --------------------------------------------------
            section_header("Executive Summary")

            ex1, ex2 = st.columns([3, 2])

            with ex1:
                topic_html = "".join(
                    f"<span class='topic-chip'>{t}</span>"
                    for t in result["topics"][:8]
                ) if result["topics"] else ""

                st.markdown(f"""
                <div class="dashboard-card">
                    <div class="repo-title">{result['full_name']}</div>
                    <div class="repo-desc">{result['description']}</div>
                    <div class="repo-meta">
                        <span>🗣 {result['language']}</span>
                        <span>📜 {result['license']}</span>
                        <span>🕑 Pushed {days_ago(result['pushed_at'])}</span>
                        <span>🏷 {result['releases']} releases</span>
                    </div>
                    <div style="margin-top:.9rem;">{topic_html}</div>
                </div>
                """, unsafe_allow_html=True)

            with ex2:
                render_verdict_card(assessment)

            # --------------------------------------------------
            # Health Review
            # --------------------------------------------------
            section_header("Health Review")

            h1, h2, h3 = st.columns([1.15, 1.15, 1.3])

            with h1:
                st.markdown("### Positives")
                render_note_cards(
                    assessment["positives"],
                    variant="positive",
                    empty_text="No strong positive signals highlighted.",
                )

            with h2:
                st.markdown("### Risks")
                render_note_cards(
                    assessment["concerns"],
                    variant="warning",
                    empty_text="No major risks detected.",
                )

            with h3:
                st.markdown("### Recommendations")
                render_note_cards(
                    result["recommendations"],
                    variant="info",
                    empty_text="No major improvements recommended.",
                )

            # --------------------------------------------------
            # Technology & Engineering Snapshot
            # --------------------------------------------------
            section_header("Technology & Engineering Snapshot")

            snap1, snap2 = st.columns([1.2, 1])

            with snap1:
                st.markdown("### Technology Stack")
                t1, t2, t3 = st.columns(3)
                tech = result["technologies"]

                with t1:
                    st.markdown("**Backend**")
                    render_tags(tech["backend"], class_name="tech-tag")

                with t2:
                    st.markdown("**Frontend**")
                    frontend_items = result["frontend_stack"] or tech["frontend"]
                    render_tags(frontend_items, class_name="tech-tag")

                with t3:
                    st.markdown("**Infrastructure**")
                    render_tags(tech["infrastructure"], class_name="tech-tag")

                st.markdown("### Detected Libraries")
                render_tags(
                    result["dependencies"],
                    class_name="dep-tag",
                    empty_text="No major libraries detected.",
                )

            with snap2:
                st.markdown("### Engineering Signals")
                render_signal_checklist(result["engineering_signals"])

            # --------------------------------------------------
            # Engineering Review
            # --------------------------------------------------
            section_header("Engineering Review")

            er1, er2 = st.columns(2)

            with er1:
                st.markdown("### Strengths")
                render_note_cards(
                    result["engineering_strengths"],
                    variant="positive",
                    empty_text="No explicit engineering strengths detected.",
                )

            with er2:
                st.markdown("### Gaps")
                render_note_cards(
                    result["engineering_weaknesses"],
                    variant="warning",
                    empty_text="No major engineering gaps detected.",
                )

            # --------------------------------------------------
            # Score Breakdown
            # --------------------------------------------------
            section_header("Score Breakdown")

            ch1, ch2 = st.columns(2)

            with ch1:
                with st.container(border=True):
                    st.plotly_chart(radar_chart(result["breakdown"]), use_container_width=True)

            with ch2:
                with st.container(border=True):
                    st.plotly_chart(bar_chart(result["breakdown"]), use_container_width=True)

            # --------------------------------------------------
            # Score Explanation
            # --------------------------------------------------
            section_header("Score Explanation")
            render_score_explanation(result)

            # --------------------------------------------------
            # Methodology
            # --------------------------------------------------
            section_header("Methodology")

            with st.expander("How does RepoLens calculate repository quality?"):
                st.markdown("""
### Overall Score

| Category | Weight |
|---|---|
| Documentation | 25 |
| Activity | 25 |
| Community | 20 |
| Project Hygiene | 20 |
| Issue Health | 10 |

### Engineering Score

Engineering quality considers automated tests, documentation, CI/CD, Docker support, and dependency management.

RepoLens scans repository metadata, file structure, and dependency files to produce heuristic repository health scores.
""")

            # --------------------------------------------------
            # Findings
            # --------------------------------------------------
            section_header("Findings")

            sw1, sw2 = st.columns(2)

            with sw1:
                render_findings("Strengths", result["strengths"], "pill-strength")

            with sw2:
                render_findings("Weaknesses", result["weaknesses"], "pill-weakness")

            # --------------------------------------------------
            # AI Repository Assessment
            # --------------------------------------------------
            section_header("AI Repository Assessment")
            render_ai_cards(result["ai_summary"])