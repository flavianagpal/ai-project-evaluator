import plotly.graph_objects as go


def radar_chart(breakdown):
    categories  = [b["category"] for b in breakdown]
    percentages = [round((b["points"] / b["max"]) * 100) for b in breakdown]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=percentages + [percentages[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(108,142,255,0.12)",
        line=dict(color="#6C8EFF", width=2),
        marker=dict(size=5, color="#6C8EFF"),
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="#1c2a3d",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color="#7b93b8", size=10),
                gridcolor="rgba(99,155,255,.08)",
                linecolor="rgba(99,155,255,.08)",
            ),
            angularaxis=dict(
                tickfont=dict(color="#c7d4f0", size=11),
                gridcolor="rgba(99,155,255,.08)",
                linecolor="rgba(99,155,255,.08)",
            ),
        ),
        paper_bgcolor="#1c2a3d",
        plot_bgcolor="#1c2a3d",
        showlegend=False,
        height=340,
        margin=dict(t=20, b=20, l=30, r=30),
    )
    return fig


def bar_chart(breakdown):
    categories  = [b["category"] for b in breakdown]
    percentages = [round((b["points"] / b["max"]) * 100) for b in breakdown]

    colors = [
        "#34d399" if p >= 80 else
        "#6C8EFF" if p >= 60 else
        "#fbbf24" if p >= 40 else
        "#f87171"
        for p in percentages
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=percentages,
        y=categories,
        orientation="h",
        marker_color=colors,
        marker=dict(
            color=colors,
            line=dict(width=0),
        ),
        text=[f"{p}%" for p in percentages],
        textposition="outside",
        textfont=dict(color="#7b93b8", size=11),
    ))

    fig.update_layout(
        paper_bgcolor="#1c2a3d",
        plot_bgcolor="#1c2a3d",
        xaxis=dict(
            range=[0, 115],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(color="#c7d4f0", size=11),
            gridcolor="rgba(99,155,255,.06)",
        ),
        showlegend=False,
        height=320,
        margin=dict(t=10, b=10, l=0, r=50),
    )
    return fig