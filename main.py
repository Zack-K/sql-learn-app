from fastapi import FastAPI, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app import models, database
import logging
import sqlite3
import markdown
from typing import Optional

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DBの初期化（テーブル作成）
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="SOL Training App")

# 静的ファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Markdownカスタムフィルターの追加
def markdown_filter(text):
    if not text:
        return ""
    return markdown.markdown(text, extensions=['fenced_code', 'tables', 'nl2br'])

templates.env.filters["markdown"] = markdown_filter

@app.on_event("startup")
def startup_event():
    # 起動時にデータベースに17日分のレコードがなければ初期化する
    db = database.SessionLocal()
    try:
        count = db.query(models.UserAnswer).count()
        if count == 0:
            logger.info("Initializing 17 days of UserAnswer records...")
            for day_num in range(1, 18):
                new_record = models.UserAnswer(day=day_num)
                db.add(new_record)
            db.commit()
    finally:
        db.close()

@app.get("/")
def read_root(request: Request, db: Session = Depends(database.get_db)):
    # ドリル全体のデータ読み込み（とりあえずモックデータでも動くように空配列でもOK）
    drills = database.load_drills_data()
    
    # 全ての解答ステータスを取得（サイドバーのバッジ表示などに使う）
    user_answers = db.query(models.UserAnswer).order_by(models.UserAnswer.day).all()
    status_map = {ans.day: ans.status for ans in user_answers}
    
    # 完了率の計算
    total_days = 17
    completed_days = sum(1 for status in status_map.values() if status == "completed")
    progress_percent = int((completed_days / total_days) * 100) if total_days > 0 else 0
    
    # デフォルトはDay1を表示
    active_day = 1
    drill_data = next((d for d in drills if d.get("day") == active_day), None)
    current_answer = db.query(models.UserAnswer).filter(models.UserAnswer.day == active_day).first()

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "drills": drills,
        "status_map": status_map,
        "progress_percent": progress_percent,
        "active_day": active_day,
        "drill_data": drill_data,
        "current_answer": current_answer
    })

# HTMXによるタブ切り替えエンドポイント
@app.get("/day/{day_id}")
def get_day_content(request: Request, day_id: int, db: Session = Depends(database.get_db)):
    drills = database.load_drills_data()
    drill_data = next((d for d in drills if d.get("day") == day_id), None)
    current_answer = db.query(models.UserAnswer).filter(models.UserAnswer.day == day_id).first()
    
    # hx-requestからのアクセスなら、エディタ部分だけ（editor.html）を返す
    if "hx-request" in request.headers:
        return templates.TemplateResponse("editor.html", {
            "request": request,
            "active_day": day_id,
            "drill_data": drill_data,
            "current_answer": current_answer
        })
    # 直接URL指定された場合は全体(index)を返す
    return read_root(request, db)

# HTMXによる保存エンドポイント
@app.post("/save/{day_id}")
def save_answer(day_id: int, answer_text: str = Form(...), db: Session = Depends(database.get_db)):
    current_answer = db.query(models.UserAnswer).filter(models.UserAnswer.day == day_id).first()
    if not current_answer:
        current_answer = models.UserAnswer(day=day_id, status="in_progress")
        db.add(current_answer)
    
    current_answer.answer_text = answer_text
    
    # 簡易的に、何かしら入力があればin_progress扱いにする
    if answer_text.strip() != "":
        current_answer.status = "in_progress"
        
    db.commit()
    # 保存成功メッセージのHTML片を返す
    return "✅ 保存しました！"

# HTMXによる解答例取得エンドポイント
@app.get("/answer/{day_id}")
def get_example_answer(request: Request, day_id: int, db: Session = Depends(database.get_db)):
    drills = database.load_drills_data()
    drill_data = next((d for d in drills if d.get("day") == day_id), None)
    
    if not drill_data:
        return "<div class='toast-message' style='color:red;'>解答例が見つかりません。</div>"
        
    # 解答を見たらステータスを完了にするロジック（オプション）
    current_answer = db.query(models.UserAnswer).filter(models.UserAnswer.day == day_id).first()
    if current_answer and current_answer.status != "completed":
        current_answer.status = "completed"
        db.commit()
        
    return templates.TemplateResponse("answer_fragment.html", {
        "request": request,
        "example_answer": drill_data.get("example_answer", ""),
        "explanation": drill_data.get("explanation", "")
    })

# HTMXによるSQL実行(Playground)エンドポイント
@app.post("/run_sql/{day_id}")
def run_sql(request: Request, day_id: int, sql_query: str = Form(...)):
    drills = database.load_drills_data()
    drill_data = next((d for d in drills if d.get("day") == day_id), None)
    
    if not drill_data or not sql_query.strip():
        return templates.TemplateResponse("sql_result.html", {
            "request": request, "error": "Query is empty or drill not found."
        })
    
    # In-Memory Database 接続
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # mock_data の投入
        schemas = drill_data.get("schema", [])
        for schema in schemas:
            # UI表示名（例: users.csv, dest_table (既存データ)）から、直感的で実行可能なSQLのテーブル名（users_csv, dest_table）を生成
            raw_name = schema.get("table_name", "")
            table_name = raw_name.split(" ")[0].replace(".", "_")
            if "[" in table_name or "Task:" in table_name or "Source" in table_name or "DAG" in raw_name:
                continue # 概念的なテーブル記述はスキップ
            
            mock_data = schema.get("mock_data", [])
            if not mock_data:
                continue
            
            # 最初のレコードのキーを使ってCREATE TABLE (すべてTEXT型にする簡易実装)
            keys = list(mock_data[0].keys())
            cols = ", ".join([f'"{k}" TEXT' for k in keys])
            create_stmt = f'CREATE TABLE "{table_name}" ({cols})'
            cursor.execute(create_stmt)
            
            # データ挿入
            placeholders = ", ".join(["?"] * len(keys))
            insert_stmt = f'INSERT INTO "{table_name}" ({", ".join([f"{k}*" for k in keys]).replace("*", "")}) VALUES ({placeholders})'
            
            for row in mock_data:
                cursor.execute(insert_stmt, tuple(str(row.get(k, "")) for k in keys))
                
        # ユーザーのSQLを実行
        cursor.execute(sql_query)
        # SELECT結果であればフェッチする
        if sql_query.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description] if cursor.description else []
            return templates.TemplateResponse("sql_result.html", {
                "request": request, "columns": columns, "rows": [tuple(row) for row in rows]
            })
        else:
            conn.commit()
            return templates.TemplateResponse("sql_result.html", {
                "request": request, "error": "Query executed successfully, but no data returned (only SELECT is supported for preview)."
            })
            
    except Exception as e:
        return templates.TemplateResponse("sql_result.html", {
            "request": request, "error": str(e)
        })
    finally:
        conn.close()
