import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timezone

from app import analyze_repo


# --------------------------------------------------
# Page Config
# --------------------------------------------------

st.set_page_config(
    page_title="RepoLens · GitHub Repository Intelligence",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# Load CSS
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


def radar_chart(breakdown):
    cats = [b["category"] for b in breakdown]
    pcts = [round(b["points"] / b["max"] * 100) for b in breakdown]

    fig = go.Figure(go.Scatterpolar(
        r=pcts + [pcts[0]],
        theta=cats + [cats[0]],
        fill="toself",
        fillcolor="rgba(55,138,221,0.12)",
        line=dict(color="#378ADD", width=1.5),
        marker=dict(size=5, color="#378ADD"),
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="#111827",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color="#94a3b8", size=10),
                gridcolor="rgba(255,255,255,.06)",
                linecolor="rgba(255,255,255,.06)",
            ),
            angularaxis=dict(
                tickfont=dict(color="#f1f5f9", size=11),
                gridcolor="rgba(255,255,255,.06)",
                linecolor="rgba(255,255,255,.06)",
            ),
        ),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        margin=dict(t=20, b=20, l=30, r=30),
        height=320,
        showlegend=False,
    )
    return fig


def bar_chart(breakdown):
    cats = [b["category"] for b in breakdown]
    pcts = [round(b["points"] / b["max"] * 100) for b in breakdown]

    colors = [
        "#1D9E75" if p >= 75 else "#378ADD" if p >= 50 else "#BA7517" if p >= 25 else "#E24B4A"
        for p in pcts
    ]

    fig = go.Figure(go.Bar(
        y=cats,
        x=pcts,
        orientation="h",
        marker_color=colors,
        text=[f"{p}%" for p in pcts],
        textposition="outside",
        textfont=dict(color="#94a3b8", size=11),
    ))

    fig.update_layout(
        xaxis=dict(
            range=[0, 115],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            color="#94a3b8",
        ),
        yaxis=dict(
            tickfont=dict(color="#f1f5f9", size=11),
            gridcolor="rgba(255,255,255,.06)",
        ),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        margin=dict(t=10, b=10, l=0, r=60),
        height=260,
        showlegend=False,
    )
    return fig


def render_tags(items, class_name="tech-tag", empty_text="Not detected"):
    if not items:
        st.caption(empty_text)
        return

    html = "".join(
        f'<span class="{class_name}">{item}</span>'
        for item in items
    )
    st.markdown(html, unsafe_allow_html=True)


def render_signal_checklist(signals):
    signal_items = [
        ("Tests", signals.get("has_tests", False)),
        ("Documentation", signals.get("has_docs", False)),
        ("CI/CD", signals.get("has_ci", False)),
        ("Docker", signals.get("has_docker", False)),
        ("Dependency Management", signals.get("has_dependency_management", False)),
    ]

    rows = ""
    for label, value in signal_items:
        badge_class = "signal-yes" if value else "signal-no"
        badge_text = "Yes" if value else "No"
        rows += f"""
        <div class="signal-item">
            <div class="signal-name">{label}</div>
            <div class="signal-badge {badge_class}">{badge_text}</div>
        </div>
        """

    st.markdown(f'<div class="signal-grid">{rows}</div>', unsafe_allow_html=True)


def render_note_cards(items, variant="info", empty_text=None):
    if not items:
        if empty_text:
            st.caption(empty_text)
        return

    variant_class = {
        "positive": "note-positive",
        "warning": "note-warning",
        "info": "note-info",
    }.get(variant, "note-info")

    title_map = {
        "positive": "Positive",
        "warning": "Risk",
        "info": "Recommendation",
    }
    title_label = title_map.get(variant, "")

    for item in items:
        st.markdown(
            f"""
            <div class="note-card {variant_class}">
                <div class="note-title">{title_label}</div>
                {item}
            </div>
            """,
            unsafe_allow_html=True,
        )


# --------------------------------------------------
# Hero / Input
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
        label_visibility="collapsed"
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
    st.caption("A read-only token is enough. It is only used for GitHub API requests and is not stored.")

token = token.strip() if token else None


# --------------------------------------------------
# Analysis
# --------------------------------------------------

if analyze_clicked:
    repo_value = repo_input.strip()

    if not repo_value or repo_value.count("/") != 1:
        st.warning("Enter a repository in the format owner/repo, for example streamlit/streamlit.")
    else:
        owner, repo = repo_value.split("/", 1)

        with st.spinner("Analyzing repository..."):
            result = analyze_repo(owner.strip(), repo.strip(), token or None)

        if result is None:
            st.error("Repository not found, API limit reached, or repository data could not be fetched.")
        else:
            score = result["score"]
            cls = score_class(score)
            assessment = result["assessment"]

            # --------------------------------------------------
            # Overview
            # --------------------------------------------------
            st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)

            c0, c1, c2, c3, c4, c5 = st.columns([1.25, 1, 1, 1, 1, 1])

            with c0:
                st.markdown(f"""
                <div style="text-align:center; padding:.4rem 0;">
                    <div class="score-badge {cls}">{score}</div>
                    <div style="font-size:.72rem; color:#94a3b8; margin-top:.4rem; text-transform:uppercase; letter-spacing:.07em;">Overall Score</div>
                </div>
                """, unsafe_allow_html=True)

            metric_items = [
                (result["engineering_score"], "Engineering"),
                (fmt_number(result["stars"]), "Stars"),
                (fmt_number(result["forks"]), "Forks"),
                (str(result["contributors"]), "Contributors"),
                (str(result["open_issues"]), "Open Issues"),
            ]

            for col, (val, lbl) in zip([c1, c2, c3, c4, c5], metric_items):
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="lbl">{lbl}</div>
                        <div class="val">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # --------------------------------------------------
            # Executive Summary
            # --------------------------------------------------
            st.markdown('<div class="section-header">Executive Summary</div>', unsafe_allow_html=True)

            ex1, ex2 = st.columns([3, 2])

            with ex1:
                topic_html = ""
                if result["topics"]:
                    topic_html = "".join(
                        f"<span class='topic-chip'>{topic}</span>"
                        for topic in result["topics"][:8]
                    )

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
                    <div style="margin-top:.9rem;">
                        {topic_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with ex2:
                concern_count = len(assessment["concerns"])
                positive_count = len(assessment["positives"])

                st.markdown(f"""
                <div class="verdict-card">
                    <div class="verdict-label">Repository Health Verdict</div>
                    <div class="verdict-value">{assessment['verdict']}</div>
                    <div class="verdict-sub">
                        {positive_count} positive signals detected · {concern_count} active concern(s)
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # --------------------------------------------------
            # Health Review + Recommendations
            # --------------------------------------------------
            st.markdown('<div class="section-header">Health Review</div>', unsafe_allow_html=True)

            h1, h2, h3 = st.columns([1.15, 1.15, 1.3])

            with h1:
                st.markdown("### Positives")
                render_note_cards(
                    assessment["positives"],
                    variant="positive",
                    empty_text="No strong positive signals highlighted."
                )

            with h2:
                st.markdown("### Risks")
                render_note_cards(
                    assessment["concerns"],
                    variant="warning",
                    empty_text="No major risks detected."
                )

            with h3:
                st.markdown("### Recommendations")
                render_note_cards(
                    result["recommendations"],
                    variant="info",
                    empty_text="No major improvements recommended."
                )

            # --------------------------------------------------
            # Technology + Engineering Snapshot
            # --------------------------------------------------
            st.markdown('<div class="section-header">Technology & Engineering Snapshot</div>', unsafe_allow_html=True)

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
                    frontend_items = result["frontend_stack"] if result["frontend_stack"] else tech["frontend"]
                    render_tags(frontend_items, class_name="tech-tag")

                with t3:
                    st.markdown("**Infrastructure**")
                    render_tags(tech["infrastructure"], class_name="tech-tag")

                st.markdown("### Detected Libraries")
                render_tags(
                    result["dependencies"],
                    class_name="dep-tag",
                    empty_text="No major libraries detected."
                )

            with snap2:
                st.markdown("### Engineering Signals")
                render_signal_checklist(result["engineering_signals"])

            # --------------------------------------------------
            # Engineering Review
            # --------------------------------------------------
            st.markdown('<div class="section-header">Engineering Review</div>', unsafe_allow_html=True)

            er1, er2 = st.columns(2)

            with er1:
                st.markdown("### Strengths")
                render_note_cards(
                    result["engineering_strengths"],
                    variant="positive",
                    empty_text="No explicit engineering strengths detected."
                )

            with er2:
                st.markdown("### Gaps")
                render_note_cards(
                    result["engineering_weaknesses"],
                    variant="warning",
                    empty_text="No major engineering gaps detected."
                )

            # --------------------------------------------------
            # Score Breakdown
            # --------------------------------------------------
            st.markdown('<div class="section-header">Score Breakdown</div>', unsafe_allow_html=True)

            ch1, ch2 = st.columns(2)
            with ch1:
                st.plotly_chart(radar_chart(result["breakdown"]), width="stretch")
            with ch2:
                st.plotly_chart(bar_chart(result["breakdown"]), width="stretch")

            # --------------------------------------------------
            # Findings
            # --------------------------------------------------
            st.markdown('<div class="section-header">Findings</div>', unsafe_allow_html=True)

            sw1, sw2 = st.columns(2)

            with sw1:
                st.markdown("### Strengths")
                if result["strengths"]:
                    for s in result["strengths"]:
                        st.markdown(f"""
                        <div class="pill pill-strength">
                            <div>
                                <div class="pill-label">{s['label']}</div>
                                <div class="pill-detail">{s['detail']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No notable strengths detected.")

            with sw2:
                st.markdown("### Weaknesses")
                if result["weaknesses"]:
                    for w in result["weaknesses"]:
                        st.markdown(f"""
                        <div class="pill pill-weakness">
                            <div>
                                <div class="pill-label">{w['label']}</div>
                                <div class="pill-detail">{w['detail']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No major weaknesses detected.")

            # --------------------------------------------------
            # AI Analysis Placeholder
            # --------------------------------------------------
            st.markdown('<div class="section-header">AI Analysis</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="dashboard-card">
                <div class="repo-title">AI Summary</div>
                <div class="repo-desc" style="margin-bottom:0;">
                    AI-generated repository analysis is temporarily disabled in this deployment build.
                    RepoLens analysis, scoring, health checks, and engineering review remain fully available.
                </div>
            </div>
            """, unsafe_allow_html=True)

            # --------------------------------------------------
            # Raw JSON
            # --------------------------------------------------
            with st.expander("Raw JSON data"):
                safe = {k: v for k, v in result.items() if k not in ("strengths", "weaknesses", "breakdown")}
                safe["strengths"] = [s["label"] for s in result["strengths"]]
                safe["weaknesses"] = [w["label"] for w in result["weaknesses"]]
                st.json(safe)