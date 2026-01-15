"""
User Behavior Analysis Page - ユーザー行動分析
"""
import streamlit as st
import pandas as pd
from datetime import timedelta

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import load_data, get_date_range, filter_by_date
from utils.charts import (
    create_line_chart, create_bar_chart, create_pie_chart,
    create_area_chart, format_number
)

st.set_page_config(
    page_title="Behavior Analysis",
    page_icon="👤",
    layout="wide"
)

st.title("👤 ユーザー行動分析")

# Load data
df_daily = load_data("daily_summary.csv")
df_pages = load_data("page_metrics.csv")

if df_daily.empty:
    st.error("データが見つかりません。")
    st.stop()

# Date filter
min_date, max_date = get_date_range(df_daily)

st.sidebar.subheader("期間選択")
date_option = st.sidebar.radio(
    "プリセット",
    ["過去7日", "過去30日", "過去90日"],
    horizontal=True,
    key="behavior_date"
)

if date_option == "過去7日":
    start_date = max_date - timedelta(days=6)
elif date_option == "過去30日":
    start_date = max_date - timedelta(days=29)
else:
    start_date = min_date
end_date = max_date

# Filter dataframes
df_daily_filtered = filter_by_date(df_daily, start_date, end_date)
df_pages_filtered = filter_by_date(df_pages, start_date, end_date)

st.caption(f"期間: {start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}")

# Summary metrics
avg_session_duration = df_daily_filtered['avg_session_duration'].mean()
avg_pages_per_session = df_daily_filtered['pages_per_session'].mean()
avg_bounce_rate = df_daily_filtered['bounce_rate'].mean() * 100
total_new_visitors = df_daily_filtered['new_visitors'].sum()
total_returning = df_daily_filtered['returning_visitors'].sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    minutes = int(avg_session_duration // 60)
    seconds = int(avg_session_duration % 60)
    st.metric("平均セッション時間", f"{minutes}分{seconds}秒")
with col2:
    st.metric("平均閲覧ページ数", f"{avg_pages_per_session:.1f}ページ")
with col3:
    st.metric("平均直帰率", f"{avg_bounce_rate:.1f}%")
with col4:
    new_ratio = total_new_visitors / (total_new_visitors + total_returning) * 100
    st.metric("新規訪問者率", f"{new_ratio:.1f}%")

st.markdown("---")

# Visitor type breakdown
st.subheader("訪問者タイプ分析")

col1, col2 = st.columns(2)

with col1:
    df_visitor_type = pd.DataFrame({
        'タイプ': ['新規訪問者', 'リピーター'],
        '訪問者数': [total_new_visitors, total_returning]
    })
    fig = create_pie_chart(df_visitor_type, values='訪問者数', names='タイプ',
                          title="訪問者タイプ構成")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Trend of new vs returning
    df_visitor_trend = df_daily_filtered[['date', 'new_visitors', 'returning_visitors']].copy()
    df_visitor_trend = df_visitor_trend.melt(
        id_vars=['date'],
        value_vars=['new_visitors', 'returning_visitors'],
        var_name='タイプ',
        value_name='訪問者数'
    )
    df_visitor_trend['タイプ'] = df_visitor_trend['タイプ'].map({
        'new_visitors': '新規訪問者',
        'returning_visitors': 'リピーター'
    })
    fig = create_area_chart(df_visitor_trend, x='date', y='訪問者数', color='タイプ',
                           title="訪問者タイプ推移")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Engagement metrics trend
st.subheader("エンゲージメント指標推移")

col1, col2 = st.columns(2)

with col1:
    fig = create_line_chart(df_daily_filtered, x='date', y='avg_session_duration',
                           title="平均セッション時間(秒)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_bounce = df_daily_filtered.copy()
    df_bounce['bounce_rate_pct'] = df_bounce['bounce_rate'] * 100
    fig = create_line_chart(df_bounce, x='date', y='bounce_rate_pct',
                           title="直帰率(%)")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Page analysis
st.subheader("ページ分析")

# Top pages by pageviews
col1, col2 = st.columns(2)

with col1:
    df_page_pv = df_pages_filtered.groupby('page_name').agg({
        'pageviews': 'sum',
        'unique_pageviews': 'sum'
    }).reset_index().sort_values('pageviews', ascending=True).tail(10)

    fig = create_bar_chart(df_page_pv, x='page_name', y='pageviews',
                          title="ページ別PV数 TOP10", orientation='h')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Pages by category
    df_page_cat = df_pages_filtered.groupby('page_category').agg({
        'pageviews': 'sum'
    }).reset_index().sort_values('pageviews', ascending=False)

    fig = create_pie_chart(df_page_cat, values='pageviews', names='page_category',
                          title="カテゴリ別PV構成")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Exit analysis
st.subheader("離脱分析")

col1, col2 = st.columns(2)

with col1:
    # Top exit pages
    df_exit = df_pages_filtered.groupby('page_name').agg({
        'exit_rate': 'mean',
        'pageviews': 'sum'
    }).reset_index()
    df_exit = df_exit[df_exit['pageviews'] > df_exit['pageviews'].quantile(0.25)]  # Filter low traffic pages
    df_exit = df_exit.sort_values('exit_rate', ascending=True).tail(10)
    df_exit['exit_rate_pct'] = df_exit['exit_rate'] * 100

    fig = create_bar_chart(df_exit, x='page_name', y='exit_rate_pct',
                          title="離脱率の高いページ TOP10", orientation='h')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Average time on page
    df_time = df_pages_filtered.groupby('page_name').agg({
        'avg_time_on_page': 'mean',
        'pageviews': 'sum'
    }).reset_index()
    df_time = df_time[df_time['pageviews'] > df_time['pageviews'].quantile(0.25)]
    df_time = df_time.sort_values('avg_time_on_page', ascending=True).tail(10)

    fig = create_bar_chart(df_time, x='page_name', y='avg_time_on_page',
                          title="滞在時間の長いページ TOP10 (秒)", orientation='h')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Page detail table
st.subheader("ページ別詳細データ")

df_page_detail = df_pages_filtered.groupby(['page_name', 'page_category', 'page_url']).agg({
    'pageviews': 'sum',
    'unique_pageviews': 'sum',
    'avg_time_on_page': 'mean',
    'exit_rate': 'mean',
    'entrances': 'sum'
}).reset_index().sort_values('pageviews', ascending=False)

df_page_detail['avg_time_on_page'] = df_page_detail['avg_time_on_page'].round(1)
df_page_detail['exit_rate'] = (df_page_detail['exit_rate'] * 100).round(1)

df_page_detail.columns = ['ページ名', 'カテゴリ', 'URL', 'PV', 'UU', '平均滞在時間(秒)', '離脱率(%)', '入口数']

st.dataframe(df_page_detail, use_container_width=True, hide_index=True)

# Entry pages analysis
st.subheader("入口ページ分析")

df_entry = df_pages_filtered.groupby('page_name').agg({
    'entrances': 'sum'
}).reset_index().sort_values('entrances', ascending=True).tail(10)

fig = create_bar_chart(df_entry, x='page_name', y='entrances',
                      title="入口ページ TOP10", orientation='h', height=350)
st.plotly_chart(fig, use_container_width=True)
