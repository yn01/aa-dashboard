"""
Conversion Analysis Page - コンバージョン分析
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
    create_funnel_chart, create_area_chart, format_number
)

st.set_page_config(
    page_title="Conversion Analysis",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 コンバージョン分析")

# Load data
df_daily = load_data("daily_summary.csv")
df_funnel = load_data("conversion_funnel.csv")
df_products = load_data("product_sales.csv")
df_referrer = load_data("referrer_metrics.csv")

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
    key="conv_date"
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
df_funnel_filtered = filter_by_date(df_funnel, start_date, end_date)
df_products_filtered = filter_by_date(df_products, start_date, end_date)
df_referrer_filtered = filter_by_date(df_referrer, start_date, end_date)

st.caption(f"期間: {start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}")

# Summary metrics
total_cv = df_daily_filtered['conversions'].sum()
total_revenue = df_daily_filtered['revenue'].sum()
total_sessions = df_daily_filtered['sessions'].sum()
cvr = (total_cv / total_sessions * 100) if total_sessions > 0 else 0
avg_order = total_revenue / total_cv if total_cv > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("総コンバージョン", format_number(total_cv))
with col2:
    st.metric("CVR", f"{cvr:.2f}%")
with col3:
    st.metric("総売上", format_number(total_revenue, prefix="¥"))
with col4:
    st.metric("平均注文額", format_number(avg_order, prefix="¥"))

st.markdown("---")

# Conversion funnel
st.subheader("コンバージョンファネル")

col1, col2 = st.columns([1, 1])

with col1:
    # Aggregate funnel data
    df_funnel_agg = df_funnel_filtered.groupby(['step_number', 'step_name']).agg({
        'users': 'sum'
    }).reset_index().sort_values('step_number')

    fig = create_funnel_chart(df_funnel_agg, x='users', y='step_name', title="購入ファネル", height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Funnel metrics
    st.markdown("#### ファネル詳細")

    df_funnel_display = df_funnel_agg.copy()
    df_funnel_display['前ステップからの転換率'] = df_funnel_display['users'].pct_change().fillna(0)
    df_funnel_display['開始からの転換率'] = df_funnel_display['users'] / df_funnel_display['users'].iloc[0]

    for _, row in df_funnel_display.iterrows():
        col_a, col_b, col_c = st.columns([2, 1, 1])
        with col_a:
            st.write(f"**{row['step_name']}**")
        with col_b:
            st.write(format_number(row['users']))
        with col_c:
            st.write(f"{row['開始からの転換率']*100:.1f}%")

st.markdown("---")

# Revenue & Conversion trend
st.subheader("売上・コンバージョン推移")

col1, col2 = st.columns(2)

with col1:
    fig = create_area_chart(df_daily_filtered, x='date', y='revenue', title="日別売上推移")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_cv_trend = df_daily_filtered.copy()
    df_cv_trend['CVR'] = df_cv_trend['conversions'] / df_cv_trend['sessions'] * 100
    fig = create_line_chart(df_cv_trend, x='date', y='CVR', title="日別CVR推移(%)")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Product analysis
st.subheader("商品別売上分析")

col1, col2 = st.columns(2)

with col1:
    df_prod_cat = df_products_filtered.groupby('product_category').agg({
        'revenue': 'sum',
        'quantity': 'sum'
    }).reset_index().sort_values('revenue', ascending=False)

    fig = create_pie_chart(df_prod_cat, values='revenue', names='product_category',
                          title="カテゴリ別売上構成")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_prod_top = df_products_filtered.groupby('product_name').agg({
        'revenue': 'sum',
        'quantity': 'sum'
    }).reset_index().sort_values('revenue', ascending=True).tail(7)

    fig = create_bar_chart(df_prod_top, x='product_name', y='revenue',
                          title="商品別売上 TOP7", orientation='h')
    st.plotly_chart(fig, use_container_width=True)

# Product detail table
st.subheader("商品別詳細")
df_prod_detail = df_products_filtered.groupby(['product_name', 'product_category', 'unit_price']).agg({
    'quantity': 'sum',
    'revenue': 'sum'
}).reset_index().sort_values('revenue', ascending=False)

df_prod_detail.columns = ['商品名', 'カテゴリ', '単価', '販売数', '売上']
df_prod_detail['単価'] = df_prod_detail['単価'].apply(lambda x: f"¥{x:,.0f}")
df_prod_detail['売上'] = df_prod_detail['売上'].apply(lambda x: f"¥{x:,.0f}")

st.dataframe(df_prod_detail, use_container_width=True, hide_index=True)

st.markdown("---")

# Referrer conversion analysis
st.subheader("流入元別コンバージョン貢献")

col1, col2 = st.columns(2)

with col1:
    df_ref_cv = df_referrer_filtered.groupby('referrer_type').agg({
        'conversions': 'sum',
        'revenue': 'sum',
        'sessions': 'sum'
    }).reset_index()
    df_ref_cv['CVR'] = (df_ref_cv['conversions'] / df_ref_cv['sessions'] * 100).round(2)

    fig = create_bar_chart(df_ref_cv.sort_values('conversions', ascending=True),
                          x='referrer_type', y='conversions',
                          title="流入元タイプ別CV数", orientation='h')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = create_bar_chart(df_ref_cv.sort_values('CVR', ascending=True),
                          x='referrer_type', y='CVR',
                          title="流入元タイプ別CVR(%)", orientation='h')
    st.plotly_chart(fig, use_container_width=True)

# Referrer detail table
df_ref_detail = df_referrer_filtered.groupby('referrer').agg({
    'sessions': 'sum',
    'conversions': 'sum',
    'revenue': 'sum'
}).reset_index()
df_ref_detail['CVR'] = (df_ref_detail['conversions'] / df_ref_detail['sessions'] * 100).round(2)
df_ref_detail = df_ref_detail.sort_values('revenue', ascending=False)
df_ref_detail.columns = ['流入元', 'セッション', 'CV', '売上', 'CVR(%)']
df_ref_detail['売上'] = df_ref_detail['売上'].apply(lambda x: f"¥{x:,.0f}")

st.dataframe(df_ref_detail, use_container_width=True, hide_index=True)
