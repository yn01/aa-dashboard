"""
Adobe Analytics Dashboard - Main Application
経営層向けKPIダッシュボード
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.data_loader import (
    load_data, get_date_range, filter_by_date,
    get_comparison_data, calculate_change
)
from utils.charts import (
    create_metric_card, create_line_chart, create_area_chart,
    format_number, COLOR_PALETTE
)

# Page configuration
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    .block-container {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Load data
    df_daily = load_data("daily_summary.csv")

    if df_daily.empty:
        st.error("データが見つかりません。sample_dataフォルダにCSVファイルを配置してください。")
        return

    # Sidebar - Date filter
    st.sidebar.title("📊 Analytics Dashboard")
    st.sidebar.markdown("---")

    min_date, max_date = get_date_range(df_daily)

    st.sidebar.subheader("期間選択")

    # Quick date range buttons
    date_option = st.sidebar.radio(
        "プリセット",
        ["過去7日", "過去30日", "過去90日", "カスタム"],
        horizontal=True
    )

    if date_option == "過去7日":
        start_date = max_date - timedelta(days=6)
        end_date = max_date
    elif date_option == "過去30日":
        start_date = max_date - timedelta(days=29)
        end_date = max_date
    elif date_option == "過去90日":
        start_date = min_date
        end_date = max_date
    else:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("開始日", min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("終了日", max_date, min_value=min_date, max_value=max_date)

    # Comparison period
    comparison_type = st.sidebar.selectbox("比較期間", ["前週", "前日", "前月"])

    st.sidebar.markdown("---")
    st.sidebar.caption(f"データ期間: {min_date.strftime('%Y/%m/%d')} - {max_date.strftime('%Y/%m/%d')}")

    # Filter data
    df_current = filter_by_date(df_daily, start_date, end_date)
    df_previous = get_comparison_data(df_daily, start_date, end_date, comparison_type)

    # Main content
    st.title("KPI サマリー")
    st.caption(f"期間: {pd.to_datetime(start_date).strftime('%Y/%m/%d')} - {pd.to_datetime(end_date).strftime('%Y/%m/%d')} | 比較: {comparison_type}")

    # Calculate KPIs
    current_metrics = {
        'visitors': df_current['visitors'].sum(),
        'sessions': df_current['sessions'].sum(),
        'pageviews': df_current['pageviews'].sum(),
        'conversions': df_current['conversions'].sum(),
        'revenue': df_current['revenue'].sum(),
        'bounce_rate': df_current['bounce_rate'].mean() * 100,
        'avg_session_duration': df_current['avg_session_duration'].mean(),
    }

    previous_metrics = {
        'visitors': df_previous['visitors'].sum(),
        'sessions': df_previous['sessions'].sum(),
        'pageviews': df_previous['pageviews'].sum(),
        'conversions': df_previous['conversions'].sum(),
        'revenue': df_previous['revenue'].sum(),
        'bounce_rate': df_previous['bounce_rate'].mean() * 100,
        'avg_session_duration': df_previous['avg_session_duration'].mean(),
    }

    # Calculate CVR
    current_metrics['cvr'] = (current_metrics['conversions'] / current_metrics['sessions'] * 100) if current_metrics['sessions'] > 0 else 0
    previous_metrics['cvr'] = (previous_metrics['conversions'] / previous_metrics['sessions'] * 100) if previous_metrics['sessions'] > 0 else 0

    # KPI Cards - Row 1 (Traffic)
    st.subheader("トラフィック指標")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        _, change_pct, _ = calculate_change(current_metrics['visitors'], previous_metrics['visitors'])
        create_metric_card("訪問者数", current_metrics['visitors'], change_pct)

    with col2:
        _, change_pct, _ = calculate_change(current_metrics['sessions'], previous_metrics['sessions'])
        create_metric_card("セッション数", current_metrics['sessions'], change_pct)

    with col3:
        _, change_pct, _ = calculate_change(current_metrics['pageviews'], previous_metrics['pageviews'])
        create_metric_card("ページビュー", current_metrics['pageviews'], change_pct)

    with col4:
        _, change_pct, _ = calculate_change(current_metrics['bounce_rate'], previous_metrics['bounce_rate'])
        # Bounce rate: negative is better
        change_pct = -change_pct if change_pct != 0 else 0
        create_metric_card("直帰率", f"{current_metrics['bounce_rate']:.1f}%", change_pct)

    # KPI Cards - Row 2 (Conversion)
    st.subheader("コンバージョン指標")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        _, change_pct, _ = calculate_change(current_metrics['conversions'], previous_metrics['conversions'])
        create_metric_card("コンバージョン数", current_metrics['conversions'], change_pct)

    with col2:
        _, change_pct, _ = calculate_change(current_metrics['cvr'], previous_metrics['cvr'])
        create_metric_card("CVR", f"{current_metrics['cvr']:.2f}%", change_pct)

    with col3:
        _, change_pct, _ = calculate_change(current_metrics['revenue'], previous_metrics['revenue'])
        create_metric_card("売上", current_metrics['revenue'], change_pct, prefix="¥")

    with col4:
        avg_order = current_metrics['revenue'] / current_metrics['conversions'] if current_metrics['conversions'] > 0 else 0
        prev_avg_order = previous_metrics['revenue'] / previous_metrics['conversions'] if previous_metrics['conversions'] > 0 else 0
        _, change_pct, _ = calculate_change(avg_order, prev_avg_order)
        create_metric_card("平均注文額", avg_order, change_pct, prefix="¥")

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("訪問者数・セッション数 推移")
        df_trend = df_current.copy()
        df_trend = df_trend.melt(
            id_vars=['date'],
            value_vars=['visitors', 'sessions'],
            var_name='指標',
            value_name='値'
        )
        df_trend['指標'] = df_trend['指標'].map({'visitors': '訪問者数', 'sessions': 'セッション数'})
        fig = create_line_chart(df_trend, x='date', y='値', color='指標')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("売上・コンバージョン 推移")
        fig = create_area_chart(df_current, x='date', y='revenue', title="")
        st.plotly_chart(fig, use_container_width=True)

    # Daily breakdown table
    st.subheader("日別詳細データ")

    df_display = df_current[['date', 'visitors', 'sessions', 'pageviews', 'conversions', 'revenue', 'bounce_rate']].copy()
    df_display.columns = ['日付', '訪問者数', 'セッション数', 'PV', 'CV', '売上', '直帰率']
    df_display['日付'] = df_display['日付'].dt.strftime('%Y/%m/%d')
    df_display['売上'] = df_display['売上'].apply(lambda x: f"¥{x:,.0f}")
    df_display['直帰率'] = df_display['直帰率'].apply(lambda x: f"{x*100:.1f}%")

    st.dataframe(df_display, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
