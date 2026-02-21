# SQL Training App (SOL 17-Days Drill)

> **Note:** 本プロジェクトは、作者自身のSQLおよびデータパイプライン思考の学習用ツールとして、またAIコーディングアシスタント「[Antigravity](https://gemini.google.com/)」のコード生成・アーキテクチャ設計能力を検証・試用する目的で協働開発されました。

データエンジニアリングの実務に必要な思考力（ETLパイプライン設計、データ変換、品質保証、dbtのDAG設計など）を、疑似コード「SOL」を用いて鍛え上げるための17日間学習アプリケーションです。

## 🎯 概要・目的
本来、SQL構文の暗記に終始しがちな学習を一段高い抽象度（アルゴリズム設計）へ引き上げるため、意図的に実行環境のない疑似コード「SOL」を使って課題を解くドリル形式を採用しています。
コーディングではなく「データパイプラインのアーキテクチャ設計」にフォーカスするための専用トレーニングツールです。

## ✨ 主な機能

1. **17日間のカリキュラム (drills)**
   - Day1からDay17まで、順を追ってデータエンジニアリングの基本（抽出、条件分岐、ループ）から、実務的な概念（インクリメンタル更新、テストアサーション、DAGによる依存関係）を学習できます。
2. **SQL Playground（データ探索機能）**
   - 疑似コードを書く前に、前提となる各お題のダミーテーブルに対して実際に生の `SELECT` 文を発行できます。
   - バックエンドで使い捨てのインメモリSQLiteデータベースを生成し、完全に安全なサンドボックス内でデータをプレビューできます。
3. **高速＆軽量な非同期UI（HTMX）**
   - React等の複雑なフロントエンドを使わず、FastAPI + HTMX によるSPA風の俊敏な画面遷移を実現。
4. **学習記録のローカル保存**
   - 自分専用のローカル学習アプリとして、学習進捗や入力したSOLコードをSQLiteデータベース（ファイル）に自動保存します。

## 🛠️ 技術スタック
- **Backend:** Python 3, FastAPI, SQLite, SQLAlchemy
- **Frontend:** HTML5, Vanilla CSS, HTMX, Jinja2 Templates
- **UI Design:** ダークモード基調（VS Codeライク）、プログラミング特化フォント最適化（HackGen, UDEV Gothic, BIZ UDGothic）

## 🚀 ローカルでの動かし方

### 1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/sql-learn-app.git
cd sql-learn-app
```

### 2. 仮想環境の作成とパッケージのインストール（推奨）
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

pip install fastapi uvicorn sqlalchemy jinja2
```

### 3. アプリケーションの起動
```bash
uvicorn main:app --reload --port 8000
```
起動後、ブラウザで `http://localhost:8000` にアクセスしてください。

## 📁 ディレクトリ構成

```text
sql-learn-app/
├── main.py                # FastAPI メインアプリケーション・ルーティング
├── app/
│   ├── database.py        # SQLite接続およびデータロード設定
│   └── models.py          # SQLAlchemy パブリックスキーマ（学習進捗用）
├── data/
│   └── drills.json        # 17日分の問題データ・ダミーデータ・解答例
├── templates/             # Jinja2 HTMLテンプレート群（HTMX部品含む）
│   ├── index.html
│   ├── editor.html
│   └── sql_result.html
├── static/
│   └── css/
│       └── style.css      # UIスタイリング
└── sql_app.db             # 自動生成されるローカルDB（学習履歴保存用）
```

## 📝 備考
本プロジェクトは、データエンジニアの思考プロセス訓練を目的とした個人学習ツールとして作成されました。問題の解答やシステムについてフィードバック大歓迎です。
