"""
Chart utilities for Adobe Analytics Dashboard
"""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

# Color palette
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ffbb00',
    'info': '#17becf',
    'purple': '#9467bd',
    'pink': '#e377c2',
}

COLOR_PALETTE = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']


def format_number(value, prefix="", suffix="", decimal=0):
    """Format number with Japanese-style grouping"""
    if pd.isna(value):
        return "-"

    # If value is already a string, return it with prefix/suffix
    if isinstance(value, str):
        return f"{prefix}{value}{suffix}"

    if abs(value) >= 100000000:  # 1億以上
        formatted = f"{value / 100000000:.1f}億"
    elif abs(value) >= 10000:  # 1万以上
        formatted = f"{value / 10000:.1f}万"
    else:
        formatted = f"{value:,.{decimal}f}"

    return f"{prefix}{formatted}{suffix}"


def create_metric_card(label: str, value, change_pct: float = None, prefix: str = "", suffix: str = ""):
    """Create a metric card with optional change indicator"""
    # If value is already formatted as string, use it directly
    if isinstance(value, str):
        formatted_value = value
    else:
        formatted_value = format_number(value, prefix, suffix)

    if change_pct is not None:
        delta = f"{change_pct:+.1f}%"
        delta_color = "normal" if change_pct >= 0 else "inverse"
        st.metric(label=label, value=formatted_value, delta=delta, delta_color=delta_color)
    else:
        st.metric(label=label, value=formatted_value)


def create_line_chart(df: pd.DataFrame, x: str, y: str, title: str = "",
                      color: str = None, height: int = 400):
    """Create a line chart"""
    if color and color in df.columns:
        fig = px.line(df, x=x, y=y, color=color, title=title,
                      color_discrete_sequence=COLOR_PALETTE)
    else:
        fig = px.line(df, x=x, y=y, title=title,
                      color_discrete_sequence=[COLORS['primary']])

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="")

    return fig


def create_area_chart(df: pd.DataFrame, x: str, y: str, title: str = "",
                      color: str = None, height: int = 400):
    """Create an area chart"""
    if color and color in df.columns:
        fig = px.area(df, x=x, y=y, color=color, title=title,
                      color_discrete_sequence=COLOR_PALETTE)
    else:
        fig = px.area(df, x=x, y=y, title=title,
                      color_discrete_sequence=[COLORS['primary']])

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )

    return fig


def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "",
                     orientation: str = "v", color: str = None, height: int = 400):
    """Create a bar chart"""
    if orientation == "h":
        fig = px.bar(df, x=y, y=x, orientation='h', title=title,
                     color=color, color_discrete_sequence=COLOR_PALETTE)
    else:
        fig = px.bar(df, x=x, y=y, title=title,
                     color=color, color_discrete_sequence=COLOR_PALETTE)

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=bool(color),
    )

    return fig


def create_pie_chart(df: pd.DataFrame, values: str, names: str, title: str = "",
                     height: int = 400, hole: float = 0.4):
    """Create a donut/pie chart"""
    fig = px.pie(df, values=values, names=names, title=title,
                 color_discrete_sequence=COLOR_PALETTE, hole=hole)

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig


def create_funnel_chart(df: pd.DataFrame, x: str, y: str, title: str = "", height: int = 400):
    """Create a funnel chart"""
    fig = go.Figure(go.Funnel(
        y=df[y],
        x=df[x],
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(color=COLOR_PALETTE[:len(df)]),
    ))

    fig.update_layout(
        title=title,
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


def create_heatmap(df: pd.DataFrame, x: str, y: str, z: str, title: str = "", height: int = 400):
    """Create a heatmap"""
    pivot_df = df.pivot_table(values=z, index=y, columns=x, aggfunc='sum')

    fig = px.imshow(pivot_df, title=title, color_continuous_scale='Blues',
                    aspect='auto')

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig
