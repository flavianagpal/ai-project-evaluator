import streamlit as st
import plotly.graph_objects as go
import requests

from datetime import datetime, timezone
from app import analyze_repo


# --------------------------------------------------
# Page Config
# --------------------------------------------------

st.set_page_config(
    page_title="Repo Lens · GitHub Evaluator",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# Load External CSS
# --------------------------------------------------

def load_css():
    with open("styles.css", "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True,
        )


load_css()



# ── Helpers ───────────────────────────────────────────────────────────────────

def score_class(s):
    if s >= 80: return "score-excellent"
    if s >= 60: return "score-good"
    if s >= 40: return "score-fair"
    return "score-poor"




def fmt_number(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}k"
    return str(n)


def days_ago(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        d = (datetime.now(timezone.utc) - dt).days
        if d == 0: return "today"
        if d == 1: return "yesterday"
        if d < 30: return f"{d}d ago"
        if d < 365: return f"{d//30}mo ago"
        return f"{d//365}y ago"
    except Exception:
        return "unknown"


def radar_chart(breakdown):
    cats = [b["category"] for b in breakdown]
    pcts = [round(b["points"] / b["max"] * 100) for b in breakdown]

    fig = go.Figure(go.Scatterpolar(
        r=pcts + [pcts[0]],
        theta=cats + [cats[0]],
        fill="toself",
        fillcolor="rgba(88,166,255,0.15)",
        line=dict(color="#58a6ff", width=2),
        marker=dict(size=6, color="#58a6ff"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#0d1117",
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(color="#8b949e", size=10),
                gridcolor="#30363d", linecolor="#30363d",
            ),
            angularaxis=dict(
                tickfont=dict(color="#c9d1d9", size=12),
                gridcolor="#21262d", linecolor="#30363d",
            ),
        ),
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        margin=dict(t=20, b=20, l=30, r=30),
        height=300,
        showlegend=False,
    )
    return fig


def bar_chart(breakdown):
    cats = [b["category"] for b in breakdown]
    pcts = [round(b["points"] / b["max"] * 100) for b in breakdown]
    colors = ["#3fb950" if p >= 75 else "#58a6ff" if p >= 50 else "#d29922" if p >= 25 else "#f85149"
              for p in pcts]

    fig = go.Figure(go.Bar(
        y=cats, x=pcts,
        orientation="h",
        marker_color=colors,
        text=[f"{p}%" for p in pcts],
        textposition="outside",
        textfont=dict(color="#8b949e", size=11),
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 115], showgrid=False, showticklabels=False,
                   zeroline=False, color="#8b949e"),
        yaxis=dict(tickfont=dict(color="#c9d1d9", size=12), gridcolor="#21262d"),
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        margin=dict(t=10, b=10, l=0, r=60),
        height=220,
        showlegend=False,
    )
    return fig


def get_ai_summary(result: dict) -> str:
    """Ask Claude to write a crisp 3-sentence evaluation of the repo."""
    prompt = f"""You are a senior software engineer reviewing a GitHub repository.
Here is the evaluation data:

Repository: {result['full_name']}
Description: {result['description']}
Language: {result['language']}
Stars: {result['stars']:,}  Forks: {result['forks']:,}  Contributors: {result['contributors']}
Commits: {result['commits']:,}  Releases: {result['releases']}  Open issues: {result['open_issues']}
Overall score: {result['score']}/100
Strengths: {', '.join(s['label'] for s in result['strengths'][:5])}
Weaknesses: {', '.join(w['label'] for w in result['weaknesses'][:5])}
Last pushed: {days_ago(result['pushed_at'])}
License: {result['license']}  CI/CD: {'Yes' if result['has_ci'] else 'No'}

Write a crisp 3-sentence analysis:
1. What kind of project this appears to be and its overall health.
2. Its two most important strengths.
3. The single most impactful improvement the maintainer should make.

Be direct, specific, and useful. No filler phrases. No bullet points."""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )
        data = response.json()
        return data["content"][0]["text"].strip()
    except Exception as e:
        return f"AI summary unavailable: {e}"


# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="hero-badge">GitHub Analysis</div>
    <h1>🔭 Repo Lens</h1>
    <p>Deep-dive quality analysis for any public GitHub repository — documentation, activity, community health, and more.</p>
</div>
""", unsafe_allow_html=True)

col_l, col_r, col_btn = st.columns([3, 3, 2])

with col_l:
    owner = st.text_input(
    "Repository Owner",
    placeholder="owner  (e.g. facebook)",
    label_visibility="collapsed"
)

with col_r:
    repo = st.text_input(
    "Repository Name",
    placeholder="repository  (e.g. react)",
    label_visibility="collapsed"
)
with col_btn:
    st.write("")  # vertical alignment nudge
    analyze_clicked = st.button("Analyze →", use_container_width=True)

# Optional GitHub token for higher rate limits
with st.expander("⚙ GitHub token (optional — raises API rate limits)"):
    token = st.text_input("Personal access token", type="password",
                          placeholder="ghp_...", label_visibility="collapsed")
    st.caption("Read-only token is sufficient. Never stored or logged.")
token = token.strip() if token else None

# ── Analysis ──────────────────────────────────────────────────────────────────

if analyze_clicked:
    if not owner.strip() or not repo.strip():
        st.warning("Enter both an owner and repository name.")
    else:
        with st.spinner("Fetching repository data…"):
            result = analyze_repo(owner.strip(), repo.strip(), token or None)

        if result is None:
            st.error("Repository not found or GitHub API rate limit reached. Try adding a token above.")
        else:
            sc = result["score"]
            cls = score_class(sc)

            # ── Top row: score + key metrics ──────────────────────────────
            st.markdown(f'<div class="section-header">Overview</div>', unsafe_allow_html=True)

            c0, c1, c2, c3, c4, c5 = st.columns([1.2, 1, 1, 1, 1, 1])
            with c0:
                st.markdown(f"""
                <div style="text-align:center; padding: .5rem 0;">
                    <div class="score-badge {cls}">{sc}</div>
                    <div style="font-size:.75rem; color:#8b949e; margin-top:.4rem;">out of 100</div>
                </div>""", unsafe_allow_html=True)

            for col, val, lbl in [
                (c1, fmt_number(result["stars"]),        "⭐ Stars"),
                (c2, fmt_number(result["forks"]),        "🍴 Forks"),
                (c3, fmt_number(result["commits"]),      "📝 Commits"),
                (c4, str(result["contributors"]),        "👥 Contributors"),
                (c5, str(result["releases"]),            "🏷 Releases"),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="val">{val}</div>
                        <div class="lbl">{lbl}</div>
                    </div>""", unsafe_allow_html=True)
            st.markdown(
                '<div class="section-header">Repository Health</div>',unsafe_allow_html=True)

            assessment = result["assessment"]

            st.success(f"Overall Verdict: {assessment['verdict']}")
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("### Strengths")

                for item in assessment["positives"]:
                    st.success(item)

            with c2:
                st.markdown("### Risks")

                if assessment["concerns"]:
                    for item in assessment["concerns"]:
                        st.warning(item)
                else:
                    st.success("No major risks detected")
                    

               
            # ── Repo meta ──────────────────────────────────────────────────
            st.markdown(f'<div class="section-header">Repository</div>', unsafe_allow_html=True)
            mc1, mc2 = st.columns([3, 2])
            with mc1:
                st.markdown(f"""
                <div style="background:#161b22; border:1px solid #30363d; border-radius:12px; padding:1rem 1.4rem;">
                    <div style="font-size:1.1rem; font-weight:700; color:#f0f6fc;">{result['full_name']}</div>
                    <div style="color:#8b949e; font-size:.88rem; margin:.35rem 0 .7rem;">{result['description']}</div>
                    <div style="display:flex; gap:1.2rem; flex-wrap:wrap; font-size:.8rem; color:#8b949e;">
                        <span>🗣 {result['language']}</span>
                        <span>📜 {result['license']}</span>
                        <span>⚙ CI: {'✅' if result['has_ci'] else '❌'}</span>
                        <span>🕑 Pushed {days_ago(result['pushed_at'])}</span>
                        <span>🐛 {result['open_issues']} open issues</span>
                    </div>
                    {"<div style='margin-top:.7rem; display:flex; gap:.4rem; flex-wrap:wrap;'>" + ''.join(f"<span style='background:#21262d; color:#58a6ff; border:1px solid #30363d; border-radius:12px; padding:2px 9px; font-size:.73rem;'>{t}</span>" for t in result['topics'][:8]) + "</div>" if result['topics'] else ""}
                </div>""", unsafe_allow_html=True)

            with mc2:
                if result.get("homepage"):
                    st.markdown(f"""
                    <div style="background:#161b22; border:1px solid #30363d; border-radius:12px; padding:1rem 1.4rem; height:100%;">
                        <div style="font-size:.8rem; color:#8b949e; margin-bottom:.4rem;">🌐 Homepage</div>
                        <a href="{result['homepage']}" target="_blank" style="color:#58a6ff; font-size:.88rem; word-break:break-all;">{result['homepage']}</a>
                    </div>""", unsafe_allow_html=True)

            st.markdown('<div class="section-header">Technology Stack</div>',unsafe_allow_html=True)
            tech = result["technologies"]

            t1, t2, t3 = st.columns(3)

            with t1:
                st.markdown("### Backend")

                for item in tech["backend"]:
                    st.info(item)

            with t2:
                st.markdown("### Frontend")

                if result["frontend_stack"]:

                    for item in result["frontend_stack"]:
                        st.info(item)

                elif tech["frontend"]:

                    for item in tech["frontend"]:
                        st.info(item)

                else:
                    st.caption("Not detected")
            with t3:
                st.markdown("### Infrastructure")

                for item in tech["infrastructure"]:
                    st.info(item)
            st.markdown('<div class="section-header">Engineering Quality</div>',unsafe_allow_html=True)
      
            st.metric("Engineering Score",f'{result["engineering_score"]}/100')


            st.markdown('<div class="section-header">Detected Libraries</div>',unsafe_allow_html=True)

            dep_cols = st.columns(4)

            for i, dep in enumerate(result["dependencies"]):
                with dep_cols[i % 4]:
                    st.info(dep)
            
            # ── Engineering Analysis ───────────────────────────

            st.markdown('<div class="section-header">Engineering Analysis</div>',unsafe_allow_html=True)

            eng1, eng2 = st.columns(2)

            with eng1:
                st.markdown("### ✅ Engineering Strengths")

                for item in result["engineering_strengths"]:
                    st.success(item)

            with eng2:
                st.markdown("### ⚠ Engineering Gaps")

                for item in result["engineering_weaknesses"]:
                    st.warning(item)

            # ── Score breakdown charts ─────────────────────────────────────
            st.markdown(f'<div class="section-header">Score Breakdown</div>', unsafe_allow_html=True)
            ch1, ch2 = st.columns(2)
            with ch1:
                st.plotly_chart(radar_chart(result["breakdown"]),width="stretch")
            with ch2:
                st.plotly_chart(bar_chart(result["breakdown"]),width="stretch")

            # ── Strengths & Weaknesses ─────────────────────────────────────
            st.markdown(f'<div class="section-header">Findings</div>', unsafe_allow_html=True)
            sw1, sw2 = st.columns(2)

            with sw1:
                st.markdown("**✅ Strengths**")
                if result["strengths"]:
                    for s in result["strengths"]:
                        st.markdown(f"""
                        <div class="pill pill-strength">
                            <div class="pill-icon">✅</div>
                            <div>
                                <div class="pill-label">{s['label']}</div>
                                <div class="pill-detail">{s['detail']}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#8b949e; font-size:.85rem;">No notable strengths detected.</div>', unsafe_allow_html=True)

            with sw2:
                st.markdown("**⚠️ Weaknesses**")
                if result["weaknesses"]:
                    for w in result["weaknesses"]:
                        st.markdown(f"""
                        <div class="pill pill-weakness">
                            <div class="pill-icon">⚠️</div>
                            <div>
                                <div class="pill-label">{w['label']}</div>
                                <div class="pill-detail">{w['detail']}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#3fb950; font-size:.85rem;">No major weaknesses detected 🎉</div>', unsafe_allow_html=True)

            # ── AI Summary ─────────────────────────────────────────────────
            st.markdown(f'<div class="section-header">AI Analysis</div>', unsafe_allow_html=True)
            with st.spinner("Generating AI summary…"):
                ai_text = get_ai_summary(result)

            st.markdown(f"""
            <div class="ai-card">
                <h4>🤖 Claude's take on {result['name']}</h4>
                <p>{ai_text}</p>
            </div>""", unsafe_allow_html=True)

            # ── Compare / share ────────────────────────────────────────────
            with st.expander("📋 Raw JSON data"):
                safe = {k: v for k, v in result.items() if k not in ("strengths", "weaknesses", "breakdown")}
                safe["strengths"] = [s["label"] for s in result["strengths"]]
                safe["weaknesses"] = [w["label"] for w in result["weaknesses"]]
                st.json(safe)