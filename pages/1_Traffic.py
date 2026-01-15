"""
Traffic Analysis Page - トラフィック分析
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
    page_title="Traffic Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 トラフィック分析")

# Load data
df_daily = load_data("daily_summary.csv")
df_referrer = load_data("referrer_metrics.csv")
df_device = load_data("device_metrics.csv")
df_region = load_data("region_metrics.csv")

if df_daily.empty:
    st.error("データが見つかりません。")
    st.stop()

# Date filter in sidebar
min_date, max_date = get_date_range(df_daily)

st.sidebar.subheader("期間選択")
date_option = st.sidebar.radio(
    "プリセット",
    ["過去7日", "過去30日", "過去90日"],
    horizontal=True,
    key="traffic_date"
)

if date_option == "過去7日":
    start_date = max_date - timedelta(days=6)
elif date_option == "過去30日":
    start_date = max_date - timedelta(days=29)
else:
    start_date = min_date
end_date = max_date

# Filter all dataframes
df_daily_filtered = filter_by_date(df_daily, start_date, end_date)
df_referrer_filtered = filter_by_date(df_referrer, start_date, end_date)
df_device_filtered = filter_by_date(df_device, start_date, end_date)
df_region_filtered = filter_by_date(df_region, start_date, end_date)

st.caption(f"期間: {start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}")

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("総訪問者数", format_number(df_daily_filtered['visitors'].sum()))
with col2:
    st.metric("総セッション数", format_number(df_daily_filtered['sessions'].sum()))
with col3:
    st.metric("総ページビュー", format_number(df_daily_filtered['pageviews'].sum()))
with col4:
    st.metric("平均直帰率", f"{df_daily_filtered['bounce_rate'].mean() * 100:.1f}%")

st.markdown("---")

# Traffic trend
st.subheader("トラフィック推移")

# Aggregation selector
agg_type = st.radio("集計単位", ["日別", "週別"], horizontal=True)

if agg_type == "週別":
    df_trend = df_daily_filtered.copy()
    df_trend['week'] = df_trend['date'].dt.to_period('W').apply(lambda x: x.start_time)
    df_trend = df_trend.groupby('week').agg({
        'visitors': 'sum',
        'sessions': 'sum',
        'pageviews': 'sum'
    }).reset_index()
    df_trend.columns = ['date', 'visitors', 'sessions', 'pageviews']
else:
    df_trend = df_daily_filtered

col1, col2 = st.columns(2)

with col1:
    df_melt = df_trend.melt(
        id_vars=['date'],
        value_vars=['visitors', 'sessions'],
        var_name='指標',
        value_name='値'
    )
    df_melt['指標'] = df_melt['指標'].map({'visitors': '訪問者数', 'sessions': 'セッション数'})
    fig = create_line_chart(df_melt, x='date', y='値', color='指標', title="訪問者数・セッション数")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = create_area_chart(df_trend, x='date', y='pageviews', title="ページビュー数")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Referrer analysis
st.subheader("流入元分析")

col1, col2 = st.columns(2)

with col1:
    # By referrer type
    df_ref_type = df_referrer_filtered.groupby('referrer_type').agg({
        'sessions': 'sum',
        'visitors': 'sum'
    }).reset_index().sort_values('sessions', ascending=False)

    fig = create_pie_chart(df_ref_type, values='sessions', names='referrer_type', title="流入元タイプ別セッション")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Top referrers
    df_ref_top = df_referrer_filtered.groupby('referrer').agg({
        'sessions': 'sum',
        'conversions': 'sum',
        'revenue': 'sum'
    }).reset_index().sort_values('sessions', ascending=False).head(10)

    fig = create_bar_chart(df_ref_top, x='referrer', y='sessions', title="流入元別セッション数 TOP10")
    st.plotly_chart(fig, use_container_width=True)

# Referrer detail table
st.subheader("流入元詳細")
df_ref_detail = df_referrer_filtered.groupby(['referrer', 'referrer_type']).agg({
    'sessions': 'sum',
    'visitors': 'sum',
    'conversions': 'sum',
    'revenue': 'sum'
}).reset_index().sort_values('sessions', ascending=False)

df_ref_detail['CVR'] = (df_ref_detail['conversions'] / df_ref_detail['sessions'] * 100).round(2)
df_ref_detail.columns = ['流入元', 'タイプ', 'セッション', '訪問者', 'CV', '売上', 'CVR(%)']
df_ref_detail['売上'] = df_ref_detail['売上'].apply(lambda x: f"¥{x:,.0f}")

st.dataframe(df_ref_detail, use_container_width=True, hide_index=True)

st.markdown("---")

# Device analysis
st.subheader("デバイス分析")

col1, col2 = st.columns(2)

with col1:
    df_device_sum = df_device_filtered.groupby('device').agg({
        'sessions': 'sum'
    }).reset_index()
    df_device_sum['device'] = df_device_sum['device'].map({
        'desktop': 'デスクトップ',
        'mobile': 'モバイル',
        'tablet': 'タブレット'
    })

    fig = create_pie_chart(df_device_sum, values='sessions', names='device', title="デバイス別セッション割合")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_device_detail = df_device_filtered.groupby('device').agg({
        'sessions': 'sum',
        'visitors': 'sum',
        'conversions': 'sum',
        'revenue': 'sum'
    }).reset_index()
    df_device_detail['CVR'] = (df_device_detail['conversions'] / df_device_detail['sessions'] * 100).round(2)
    df_device_detail['device'] = df_device_detail['device'].map({
        'desktop': 'デスクトップ',
        'mobile': 'モバイル',
        'tablet': 'タブレット'
    })

    fig = create_bar_chart(df_device_detail, x='device', y='CVR', title="デバイス別CVR(%)")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Region analysis
st.subheader("地域分析")

col1, col2 = st.columns(2)

with col1:
    df_region_sum = df_region_filtered.groupby('region').agg({
        'sessions': 'sum'
    }).reset_index().sort_values('sessions', ascending=True).tail(10)

    fig = create_bar_chart(df_region_sum, x='region', y='sessions',
                          title="地域別セッション数 TOP10", orientation='h')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_region_detail = df_region_filtered.groupby('region').agg({
        'sessions': 'sum',
        'conversions': 'sum',
        'revenue': 'sum'
    }).reset_index().sort_values('revenue', ascending=True).tail(10)

    fig = create_bar_chart(df_region_detail, x='region', y='revenue',
                          title="地域別売上 TOP10", orientation='h')
    st.plotly_chart(fig, use_container_width=True)
