from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP, func
from app.utils.database import Base 


class ChatRequest(BaseModel):
    user_id: str
    session_id: str = None  
    message: str
    


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)
    session_id = Column(String(255), nullable=False)
    role = Column(Enum('user', 'assistant'), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.current_timestamp())
