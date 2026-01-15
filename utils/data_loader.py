"""
Data loading utilities for Adobe Analytics Dashboard
"""
import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "sample_data"

@st.cache_data
def load_data(filename: str) -> pd.DataFrame:
    """Load CSV data with caching"""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        st.error(f"File not found: {filepath}")
        return pd.DataFrame()

    df = pd.read_csv(filepath)

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])

    return df


def get_date_range(df: pd.DataFrame) -> tuple:
    """Get min and max dates from dataframe"""
    if 'date' not in df.columns or df.empty:
        return None, None
    return df['date'].min(), df['date'].max()


def filter_by_date(df: pd.DataFrame, start_date, end_date) -> pd.DataFrame:
    """Filter dataframe by date range"""
    if 'date' not in df.columns:
        return df

    mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
    return df[mask]


def get_comparison_data(df: pd.DataFrame, current_start, current_end, period_type: str = "前週") -> pd.DataFrame:
    """Get comparison period data"""
    current_start = pd.to_datetime(current_start)
    current_end = pd.to_datetime(current_end)
    period_days = (current_end - current_start).days + 1

    if period_type == "前日":
        prev_start = current_start - pd.Timedelta(days=1)
        prev_end = current_end - pd.Timedelta(days=1)
    elif period_type == "前週":
        prev_start = current_start - pd.Timedelta(days=7)
        prev_end = current_end - pd.Timedelta(days=7)
    else:  # 前月
        prev_start = current_start - pd.Timedelta(days=30)
        prev_end = current_end - pd.Timedelta(days=30)

    return filter_by_date(df, prev_start, prev_end)


def calculate_change(current_value, previous_value) -> tuple:
    """Calculate percentage change and return (change_value, change_pct, is_positive)"""
    if previous_value == 0:
        return 0, 0, True

    change = current_value - previous_value
    change_pct = (change / previous_value) * 100
    is_positive = change >= 0

    return change, change_pct, is_positive
