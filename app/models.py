from sqlalchemy import Column, Integer, String, Text
from .database import Base

class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(Integer, unique=True, index=True, nullable=False)
    answer_text = Column(Text, default="")
    status = Column(String, default="not_started") # not_started, in_progress, completed 
