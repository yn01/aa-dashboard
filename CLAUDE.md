# AA Dashboard

Adobe Analytics データ分析用 Streamlit ダッシュボード

## 技術スタック

- Python 3.14
- Streamlit 1.53+
- Pandas / NumPy
- Plotly（チャート）

## ディレクトリ構成

- `app.py` - メインアプリ（KPIサマリー）
- `pages/` - 各分析ページ（Traffic, Conversion, Behavior）
- `utils/` - 共通ユーティリティ（data_loader.py, charts.py）
- `sample_data/` - CSVデータ

## 開発コマンド

```bash
# 仮想環境の有効化
source venv/bin/activate

# アプリ起動
streamlit run app.py

# 依存パッケージ追加時
pip install <package> && pip freeze > requirements.txt
```

## コーディング規約

- 日本語コメント可
- チャート作成は `utils/charts.py` の関数を使用
- データ読み込みは `utils/data_loader.py` の `load_data()` を使用
- 新しいページは `pages/` に `N_PageName.py` 形式で追加

## 注意事項

- CSVデータは `sample_data/` フォルダに配置
- 日付カラムは `date` という名前で統一
- 経営層向けUIのため、シンプルで分かりやすい表示を心がける
