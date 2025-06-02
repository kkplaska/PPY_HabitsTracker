from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

class Habit(Base):
    __tablename__ = 'habits'
    habit_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    name = Column(String)
    description = Column(String)
    created_at = Column(DateTime)

class HabitLog(Base):
    __tablename__ = 'habit_logs'
    habitLog_id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.habit_id'))
    description = Column(String)
    duration = Column(Float)
    date = Column(DateTime)
    completed_at = Column(DateTime, default=None)


def init_db():
    engine = create_engine('sqlite:///habit_tracker.db')
    Base.metadata.create_all(engine)