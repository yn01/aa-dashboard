# AA Dashboard

Adobe Analytics データ分析用 Streamlit ダッシュボード

## 概要

Adobe Analytics の CSV エクスポートデータを可視化・分析するためのダッシュボードアプリケーションです。経営層向けにKPIを分かりやすく表示し、トラフィック・コンバージョン・ユーザー行動を多角的に分析できます。

## 機能

### KPI サマリー（ホーム）
- 主要指標の一覧表示（訪問者数、セッション数、PV、CV、売上など）
- 前期比較（前日/前週/前月）
- トレンドグラフ

### トラフィック分析
- 訪問者・セッション・PV の推移
- 流入元別分析（Organic、Paid、Social、Direct など）
- デバイス別・地域別の内訳

### コンバージョン分析
- 購入ファネル可視化
- 売上・CV 推移
- 商品別売上ランキング
- 流入元別 CV 貢献度

### ユーザー行動分析
- 新規/リピーター比率
- ページ別 PV ランキング
- 離脱率・滞在時間分析
- 入口ページ分析

## セットアップ

### 必要要件
- Python 3.10+

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/aa-dashboard.git
cd aa-dashboard

# 仮想環境を作成・有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 起動

```bash
streamlit run app.py
```

ブラウザで http://localhost:8501 にアクセス

## データ形式

`sample_data/` フォルダに以下の CSV ファイルを配置してください：

| ファイル名 | 内容 |
|-----------|------|
| `daily_summary.csv` | 日別サマリー（訪問者、セッション、PV、CV、売上など） |
| `page_metrics.csv` | ページ別メトリクス |
| `referrer_metrics.csv` | 流入元別メトリクス |
| `device_metrics.csv` | デバイス別メトリクス |
| `region_metrics.csv` | 地域別メトリクス |
| `product_sales.csv` | 商品別売上 |
| `conversion_funnel.csv` | CV ファネルデータ |

## プロジェクト構成

```
aa-dashboard/
├── app.py                 # メインアプリ（KPIサマリー）
├── pages/
│   ├── 1_Traffic.py       # トラフィック分析
│   ├── 2_Conversion.py    # コンバージョン分析
│   └── 3_Behavior.py      # ユーザー行動分析
├── utils/
│   ├── __init__.py
│   ├── data_loader.py     # データ読み込みユーティリティ
│   └── charts.py          # チャート作成ユーティリティ
├── sample_data/           # サンプルデータ
├── requirements.txt       # 依存パッケージ
└── README.md
```

## 技術スタック

- **Python 3.14**
- **Streamlit** - Web アプリケーションフレームワーク
- **Pandas** - データ処理
- **Plotly** - インタラクティブチャート
- **NumPy** - 数値計算

## ライセンス

MIT License
