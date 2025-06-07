from sqlalchemy.orm import Session

from db.models import Habit
from db.session import get_engine


def load_habits_for_user(user_id):
    engine = get_engine()
    with Session(engine) as session:
        return session.query(Habit).filter(Habit.user_id == user_id).all()