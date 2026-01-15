"""
Adobe Analytics風サンプルデータ生成スクリプト
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 乱数シード固定（再現性のため）
np.random.seed(42)
random.seed(42)

# 期間設定（過去90日分）
end_date = datetime(2025, 1, 15)
start_date = end_date - timedelta(days=89)
dates = pd.date_range(start=start_date, end=end_date, freq='D')

# マスターデータ
pages = [
    {'page_name': 'トップページ', 'page_url': '/', 'category': 'TOP'},
    {'page_name': '商品一覧', 'page_url': '/products', 'category': '商品'},
    {'page_name': '商品詳細 - スマートフォン', 'page_url': '/products/smartphone', 'category': '商品'},
    {'page_name': '商品詳細 - ノートPC', 'page_url': '/products/laptop', 'category': '商品'},
    {'page_name': '商品詳細 - タブレット', 'page_url': '/products/tablet', 'category': '商品'},
    {'page_name': '商品詳細 - イヤホン', 'page_url': '/products/earphone', 'category': '商品'},
    {'page_name': 'カート', 'page_url': '/cart', 'category': 'CV'},
    {'page_name': '購入手続き', 'page_url': '/checkout', 'category': 'CV'},
    {'page_name': '購入完了', 'page_url': '/thanks', 'category': 'CV'},
    {'page_name': '会社概要', 'page_url': '/about', 'category': 'その他'},
    {'page_name': 'お問い合わせ', 'page_url': '/contact', 'category': 'その他'},
    {'page_name': '検索結果', 'page_url': '/search', 'category': '検索'},
]

referrers = [
    {'referrer': 'google', 'referrer_type': 'Organic Search'},
    {'referrer': 'yahoo', 'referrer_type': 'Organic Search'},
    {'referrer': 'bing', 'referrer_type': 'Organic Search'},
    {'referrer': 'facebook', 'referrer_type': 'Social'},
    {'referrer': 'twitter', 'referrer_type': 'Social'},
    {'referrer': 'instagram', 'referrer_type': 'Social'},
    {'referrer': 'line', 'referrer_type': 'Social'},
    {'referrer': 'google_ads', 'referrer_type': 'Paid Search'},
    {'referrer': 'yahoo_ads', 'referrer_type': 'Paid Search'},
    {'referrer': 'direct', 'referrer_type': 'Direct'},
    {'referrer': 'email', 'referrer_type': 'Email'},
    {'referrer': 'affiliate', 'referrer_type': 'Affiliate'},
]

devices = ['desktop', 'mobile', 'tablet']
device_weights = [0.35, 0.55, 0.10]

browsers = ['Chrome', 'Safari', 'Edge', 'Firefox', 'Other']
browser_weights = [0.45, 0.30, 0.12, 0.08, 0.05]

regions = ['東京', '大阪', '神奈川', '愛知', '福岡', '北海道', '埼玉', '千葉', '兵庫', 'その他']
region_weights = [0.25, 0.12, 0.10, 0.08, 0.06, 0.05, 0.07, 0.06, 0.05, 0.16]

products = [
    {'product_id': 'SP001', 'product_name': 'スマートフォン Pro', 'product_category': 'スマートフォン', 'price': 89800},
    {'product_id': 'SP002', 'product_name': 'スマートフォン Lite', 'product_category': 'スマートフォン', 'price': 49800},
    {'product_id': 'LP001', 'product_name': 'ノートPC 15インチ', 'product_category': 'ノートPC', 'price': 129800},
    {'product_id': 'LP002', 'product_name': 'ノートPC 13インチ', 'product_category': 'ノートPC', 'price': 98000},
    {'product_id': 'TB001', 'product_name': 'タブレット 10インチ', 'product_category': 'タブレット', 'price': 59800},
    {'product_id': 'EP001', 'product_name': 'ワイヤレスイヤホン', 'product_category': 'イヤホン', 'price': 19800},
    {'product_id': 'EP002', 'product_name': 'ノイズキャンセリングイヤホン', 'product_category': 'イヤホン', 'price': 34800},
]

# ============================================================
# 1. 日別サマリーデータ
# ============================================================
daily_data = []

for date in dates:
    # 曜日による変動（週末は増加）
    weekday = date.weekday()
    weekday_factor = 1.3 if weekday >= 5 else 1.0

    # 月による季節変動
    month = date.month
    if month in [11, 12]:  # 年末商戦
        season_factor = 1.4
    elif month in [1]:  # 初売り
        season_factor = 1.2
    else:
        season_factor = 1.0

    base_visitors = int(np.random.normal(5000, 800) * weekday_factor * season_factor)
    base_sessions = int(base_visitors * np.random.uniform(1.2, 1.5))
    base_pageviews = int(base_sessions * np.random.uniform(3.5, 5.0))

    # コンバージョン（CVR 2-4%）
    cvr = np.random.uniform(0.02, 0.04) * season_factor
    conversions = int(base_sessions * cvr)

    # 売上
    avg_order_value = np.random.normal(45000, 15000)
    revenue = int(conversions * avg_order_value)

    # その他指標
    bounce_rate = np.random.uniform(0.35, 0.50)
    avg_session_duration = np.random.uniform(120, 300)  # 秒
    pages_per_session = base_pageviews / base_sessions if base_sessions > 0 else 0

    daily_data.append({
        'date': date.strftime('%Y-%m-%d'),
        'visitors': base_visitors,
        'new_visitors': int(base_visitors * np.random.uniform(0.6, 0.75)),
        'returning_visitors': int(base_visitors * np.random.uniform(0.25, 0.4)),
        'sessions': base_sessions,
        'pageviews': base_pageviews,
        'conversions': conversions,
        'revenue': revenue,
        'bounce_rate': round(bounce_rate, 4),
        'avg_session_duration': round(avg_session_duration, 2),
        'pages_per_session': round(pages_per_session, 2),
    })

df_daily = pd.DataFrame(daily_data)
df_daily.to_csv('/Users/yoheinakanishi/Dev/test/sample_data/daily_summary.csv', index=False, encoding='utf-8-sig')
print(f"daily_summary.csv: {len(df_daily)} rows")

# ============================================================
# 2. ページ別データ（日別×ページ）
# ============================================================
page_data = []

# ページの人気度重み
page_weights = {
    '/': 0.25,
    '/products': 0.18,
    '/products/smartphone': 0.12,
    '/products/laptop': 0.10,
    '/products/tablet': 0.06,
    '/products/earphone': 0.05,
    '/cart': 0.08,
    '/checkout': 0.04,
    '/thanks': 0.03,
    '/about': 0.03,
    '/contact': 0.02,
    '/search': 0.04,
}

for date in dates:
    total_pv = df_daily[df_daily['date'] == date.strftime('%Y-%m-%d')]['pageviews'].values[0]

    for page in pages:
        weight = page_weights.get(page['page_url'], 0.05)
        pv = int(total_pv * weight * np.random.uniform(0.8, 1.2))
        unique_pv = int(pv * np.random.uniform(0.6, 0.85))

        # 離脱率（ページにより異なる）
        if page['category'] == 'CV':
            exit_rate = np.random.uniform(0.1, 0.3) if page['page_url'] == '/thanks' else np.random.uniform(0.2, 0.4)
        else:
            exit_rate = np.random.uniform(0.25, 0.55)

        avg_time = np.random.uniform(30, 180)

        page_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'page_name': page['page_name'],
            'page_url': page['page_url'],
            'page_category': page['category'],
            'pageviews': pv,
            'unique_pageviews': unique_pv,
            'avg_time_on_page': round(avg_time, 2),
            'exit_rate': round(exit_rate, 4),
            'entrances': int(unique_pv * np.random.uniform(0.2, 0.5)),
        })

df_pages = pd.DataFrame(page_data)
df_pages.to_csv('/Users/yoheinakanishi/Dev/test/sample_data/page_metrics.csv', index=False, encoding='utf-8-sig')
print(f"page_metrics.csv: {len(df_pages)} rows")

# ============================================================
# 3. 流入元別データ（日別×流入元）
# ============================================================
referrer_data = []

# 流入元の重み
ref_weights = {
    'google': 0.30,
    'yahoo': 0.10,
    'bing': 0.03,
    'facebook': 0.05,
    'twitter': 0.04,
    'instagram': 0.06,
    'line': 0.04,
    'google_ads': 0.12,
    'yahoo_ads': 0.05,
    'direct': 0.12,
    'email': 0.05,
    'affiliate': 0.04,
}

for date in dates:
    daily_row = df_daily[df_daily['date'] == date.strftime('%Y-%m-%d')].iloc[0]
    total_sessions = daily_row['sessions']
    total_cv = daily_row['conversions']
    total_revenue = daily_row['revenue']

    for ref in referrers:
        weight = ref_weights.get(ref['referrer'], 0.05)
        sessions = int(total_sessions * weight * np.random.uniform(0.8, 1.2))

        # 流入元によってCVRが異なる
        if ref['referrer_type'] == 'Paid Search':
            cvr_factor = 1.3
        elif ref['referrer_type'] == 'Email':
            cvr_factor = 1.5
        elif ref['referrer_type'] == 'Organic Search':
            cvr_factor = 1.0
        elif ref['referrer_type'] == 'Direct':
            cvr_factor = 1.2
        else:
            cvr_factor = 0.8

        cv = int(sessions * (total_cv / total_sessions) * cvr_factor * np.random.uniform(0.7, 1.3)) if total_sessions > 0 else 0
        revenue = int(cv * (total_revenue / total_cv)) if total_cv > 0 else 0

        referrer_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'referrer': ref['referrer'],
            'referrer_type': ref['referrer_type'],
            'sessions': sessions,
            'visitors': int(sessions * np.random.uniform(0.7, 0.9)),
            'pageviews': int(sessions * np.random.uniform(3.0, 5.0)),
            'conversions': cv,
            'revenue': revenue,
            'bounce_rate': round(np.random.uniform(0.3, 0.55), 4),
        })

df_referrers = pd.DataFrame(referrer_data)
df_referrers.to_csv('/Users/yoheinakanishi/Dev/test/sample_data/referrer_metrics.csv', index=False, encoding='utf-8-sig')
print(f"referrer_metrics.csv: {len(df_referrers)} rows")

# ============================================================
# 4. デバイス・ブラウザ別データ（日別）
# ============================================================
device_data = []

for date in dates:
    daily_row = df_daily[df_daily['date'] == date.strftime('%Y-%m-%d')].iloc[0]
    total_sessions = daily_row['sessions']
    total_cv = daily_row['conversions']
    total_revenue = daily_row['revenue']

    for i, device in enumerate(devices):
        weight = device_weights[i]
        sessions = int(total_sessions * weight * np.random.uniform(0.9, 1.1))

        # デバイスによるCVR差
        if device == 'desktop':
            cvr_factor = 1.3
        elif device == 'mobile':
            cvr_factor = 0.85
        else:
            cvr_factor = 1.0

        cv = int(sessions * (total_cv / total_sessions) * cvr_factor) if total_sessions > 0 else 0
        revenue = int(cv * (total_revenue / total_cv)) if total_cv > 0 else 0

        device_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'device': device,
            'sessions': sessions,
            'visitors': int(sessions * np.random.uniform(0.7, 0.9)),
            'pageviews': int(sessions * np.random.uniform(3.5, 5.5)),
            'conversions': cv,
            'revenue': revenue,
            'bounce_rate': round(np.random.uniform(0.3, 0.5), 4),
        })

df_devices = pd.DataFrame(device_data)
df_devices.to_csv('/Users/yoheinakanishi/Dev/test/sample_data/device_metrics.csv', index=False, encoding='utf-8-sig')
print(f"device_metrics.csv: {len(df_devices)} rows")

# ============================================================
# 5. 地域別データ（日別）
# ============================================================
region_data = []

for date in dates:
    daily_row = df_daily[df_daily['date'] == date.strftime('%Y-%m-%d')].iloc[0]
    total_sessions = daily_row['sessions']
    total_cv = daily_row['conversions']
    total_revenue = daily_row['revenue']

    for i, region in enumerate(regions):
        weight = region_weights[i]
        sessions = int(total_sessions * weight * np.random.uniform(0.85, 1.15))
        cv = int(total_cv * weight * np.random.uniform(0.8, 1.2))
        revenue = int(cv * (total_revenue / total_cv)) if total_cv > 0 else 0

        region_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'region': region,
            'sessions': sessions,
            'visitors': int(sessions * np.random.uniform(0.7, 0.9)),
            'pageviews': int(sessions * np.random.uniform(3.5, 5.0)),
            'conversions': cv,
            'revenue': revenue,
        })

df_regions = pd.DataFrame(region_data)
df_regions.to_csv('/Users/yoheinakanishi/Dev/test/sample_data/region_metrics.csv', index=False, encoding='utf-8-sig')
print(f"region_metrics.csv: {len(df_regions)} rows")

# ============================================================
# 6. 商品別売上データ（日別）
# ============================================================
product_data = []

for date in dates:
    daily_row = df_daily[df_daily['date'] == date.strftime('%Y-%m-%d')].iloc[0]
    total_cv = daily_row['conversions']

    # 商品の人気度
    product_weights = [0.25, 0.15, 0.20, 0.12, 0.10, 0.10, 0.08]

    for i, product in enumerate(products):
        weight = product_weights[i]
        quantity = int(total_cv * weight * np.random.uniform(0.7, 1.3))
        revenue = quantity * product['price']

        product_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'product_id': product['product_id'],
            'product_name': product['product_name'],
            'product_category': product['product_category'],
            'unit_price': product['price'],
            'quantity': quantity,
            'revenue': revenue,
        })

df_products = pd.DataFrame(product_data)
df_products.to_csv('/Users/yoheinakanishi/Dev/test/sample_data/product_sales.csv', index=False, encoding='utf-8-sig')
print(f"product_sales.csv: {len(df_products)} rows")

# ============================================================
# 7. CVファネルデータ（日別）
# ============================================================
funnel_data = []

funnel_steps = ['商品閲覧', 'カート追加', '購入手続き開始', '購入完了']

for date in dates:
    daily_row = df_daily[df_daily['date'] == date.strftime('%Y-%m-%d')].iloc[0]

    # ファネルの各ステップの数
    product_views = int(daily_row['sessions'] * np.random.uniform(0.6, 0.8))
    cart_adds = int(product_views * np.random.uniform(0.15, 0.25))
    checkout_starts = int(cart_adds * np.random.uniform(0.5, 0.7))
    purchases = daily_row['conversions']

    step_values = [product_views, cart_adds, checkout_starts, purchases]

    for i, step in enumerate(funnel_steps):
        funnel_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'step_number': i + 1,
            'step_name': step,
            'users': step_values[i],
            'conversion_rate_from_prev': round(step_values[i] / step_values[i-1], 4) if i > 0 and step_values[i-1] > 0 else 1.0,
            'conversion_rate_from_start': round(step_values[i] / step_values[0], 4) if step_values[0] > 0 else 0,
        })

df_funnel = pd.DataFrame(funnel_data)
df_funnel.to_csv('/Users/yoheinakanishi/Dev/test/sample_data/conversion_funnel.csv', index=False, encoding='utf-8-sig')
print(f"conversion_funnel.csv: {len(df_funnel)} rows")

print("\n✅ サンプルデータ生成完了!")
print(f"出力先: /Users/yoheinakanishi/Dev/test/sample_data/")
