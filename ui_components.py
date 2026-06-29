import streamlit as st


def section_header(title):
    st.markdown(
        f'<div class="section-header">{title}</div>',
        unsafe_allow_html=True,
    )


def metric_card(value, label):
    st.markdown(
        f'<div class="metric-card"><div class="lbl">{label}</div><div class="val">{value}</div></div>',
        unsafe_allow_html=True,
    )


def render_score_badge(score, css_class):
    st.markdown(
        f'<div class="score-wrap"><div class="score-badge {css_class}">{score}</div><div class="score-label">Overall Score</div></div>',
        unsafe_allow_html=True,
    )


def render_tags(items, class_name="tech-tag", empty_text="Not detected"):
    if not items:
        st.caption(empty_text)
        return
    html = "".join(f'<span class="{class_name}">{item}</span>' for item in items)
    st.markdown(html, unsafe_allow_html=True)


def render_signal_checklist(signals):
    rows = [
        ("Tests", signals["has_tests"]),
        ("Documentation", signals["has_docs"]),
        ("CI/CD", signals["has_ci"]),
        ("Docker", signals["has_docker"]),
        ("Dependency Management", signals["has_dependency_management"]),
    ]

    items_html = "".join(
        f'<div class="signal-item"><span class="signal-name">{label}</span>'
        f'<span class="signal-badge {"signal-yes" if value else "signal-no"}">{"Yes" if value else "No"}</span></div>'
        for label, value in rows
    )
    st.markdown(f'<div class="signal-grid">{items_html}</div>', unsafe_allow_html=True)


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
        "warning":  "Risk",
        "info":     "Recommendation",
    }
    title = title_map.get(variant, "")

    for item in items:
        st.markdown(
            f'<div class="note-card {variant_class}"><div class="note-title">{title}</div>{item}</div>',
            unsafe_allow_html=True,
        )


def render_verdict_card(assessment):
    positives = len(assessment["positives"])
    concerns  = len(assessment["concerns"])
    st.markdown(
        f'<div class="verdict-card">'
        f'<div class="verdict-label">Repository Health Verdict</div>'
        f'<div class="verdict-value">{assessment["verdict"]}</div>'
        f'<div class="verdict-sub">{positives} positive signals · {concerns} concern(s) flagged</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_findings(title, items, pill_class):
    st.markdown(f"### {title}")
    if not items:
        st.caption(f"No {title.lower()} detected.")
        return
    for item in items:
        st.markdown(
            f'<div class="pill {pill_class}">'
            f'<div><div class="pill-label">{item["label"]}</div>'
            f'<div class="pill-detail">{item["detail"]}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_ai_cards(ai):
    c1, c2 = st.columns(2)

    risks_html = "".join(
        f"<li>{r}</li>" for r in ai["risks"]
    ) if ai["risks"] else "<li>No major risks detected.</li>"

    with c1:
        st.markdown(
            f'<div class="dashboard-card ai-card">'
            f'<div class="ai-title">Executive Summary</div>'
            f'<div class="ai-body">{ai["executive_summary"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="dashboard-card ai-card">'
            f'<div class="ai-title">Risks</div>'
            f'<ul class="ai-list">{risks_html}</ul>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f'<div class="dashboard-card ai-card">'
            f'<div class="ai-title">Engineering Assessment</div>'
            f'<div class="ai-body">{ai["engineering_assessment"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="dashboard-card ai-card">'
            f'<div class="ai-title">Recommendation</div>'
            f'<div class="ai-body">{ai["recommendation"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )