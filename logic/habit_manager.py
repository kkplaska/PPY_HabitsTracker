from sqlalchemy.orm import Session

from db.models import Habit, HabitLog
from db.session import get_engine

def get_habits_by_user_id(user_id):
    engine = get_engine()
    with Session(engine) as session:
        return session.query(Habit).filter(Habit.user_id == user_id).all()

def get_habits_logs_by_user_id(user_id):
    engine = get_engine()
    with Session(engine) as session:
        return session.query(HabitLog).join(Habit).filter(Habit.user_id == user_id).all()
