from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    skills = Column(Text, nullable=True)  # JSON с навыками по темам

    attempts = relationship("Attempt", back_populates="user")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    questions = relationship("Question", back_populates="topic")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    difficulty = Column(Float, nullable=False)
    text = Column(Text, nullable=False)
    options = Column(Text, nullable=False)      # JSON-строка
    answer = Column(String, nullable=False)
    explanation = Column(Text, nullable=True)

    topic = relationship("Topic", back_populates="questions")
    attempts = relationship("Attempt", back_populates="question")


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    answer_given = Column(String, nullable=False)
    response_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="attempts")
    question = relationship("Question", back_populates="attempts")