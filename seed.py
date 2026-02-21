from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app import models, database
import json

# DBの再作成（リセット用）
models.Base.metadata.drop_all(bind=database.engine)
models.Base.metadata.create_all(bind=database.engine)

db = database.SessionLocal()

# Seedデータ（とりあえず17日分の空枠だけ作成）
for i in range(1, 18):
    new_ans = models.UserAnswer(day=i, status="not_started")
    db.add(new_ans)

db.commit()
db.close()

print("Database seeded with 17 empty records for UserAnswers.")
