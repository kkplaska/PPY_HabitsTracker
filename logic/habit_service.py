"""
logic/habit_service.py

Moduł logiczny odpowiedzialny za pobieranie nawyków i ich dzienników (logów)
z bazy danych dla wskazanego użytkownika.
"""

from typing import List

from sqlalchemy.orm import Session

from db.models import Habit, HabitLog
from db.session import get_engine


def get_habits_by_user_id(user_id: int) -> List[Habit]:
    """
    Zwraca listę wszystkich nawyków (Habit) przypisanych do danego użytkownika.

    :param user_id: identyfikator użytkownika
    :return: lista obiektów Habit
    """
    engine = get_engine()
    with Session(engine) as session:
        habits: List[Habit] = (
            session
            .query(Habit)
            .filter(Habit.user_id == user_id)
            .all()
        )
    return habits


def get_habit_logs_by_user_id(user_id: int) -> List[HabitLog]:
    """
    Zwraca listę wpisów dziennika nawyków (HabitLog) dla danego użytkownika.
    Do zapytania dołączony jest model Habit, aby móc korzystać z relacji.

    :param user_id: identyfikator użytkownika
    :return: lista obiektów HabitLog
    """
    engine = get_engine()
    with Session(engine) as session:
        habit_logs: List[HabitLog] = (
            session
            .query(HabitLog)
            .join(Habit)
            .filter(Habit.user_id == user_id)
            .all()
        )
    return habit_logs