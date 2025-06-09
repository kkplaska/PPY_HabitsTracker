"""
db/models.py

Moduł zawiera definicje modeli ORM dla aplikacji Habit Tracker:
- User      – użytkownicy,
- Habit     – nawyki przypisane do użytkowników,
- HabitLog  – dzienne wpisy realizacji nawyków,
oraz funkcję inicjalizującą bazę danych SQLite na podstawie tych modeli.
"""

from sqlalchemy import (create_engine, Column, Integer, String, Float, DateTime, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from db.session import get_engine

Base = declarative_base()


class User(Base):
    """
    Model reprezentujący użytkownika aplikacji.

    Atrybuty:
        user_id       – unikalne ID użytkownika (klucz główny),
        username      – nazwa użytkownika (unikalna, niepusta),
        password_hash – skrót hasła użytkownika.
    """
    __tablename__ = 'users'

    user_id: int = Column(Integer, primary_key=True)
    username: str = Column(String, unique=True, nullable=False)
    password_hash: str = Column(String, nullable=False)


class Habit(Base):
    """
    Model reprezentujący nawyk przypisany do użytkownika.

    Atrybuty:
        habit_id    – unikalne ID nawyku (klucz główny),
        user_id     – ID właściciela nawyku (klucz obcy do users.user_id),
        name        – nazwa nawyku (niepusta),
        description – opis nawyku (opcjonalny),
        created_at  – data utworzenia nawyku.
    """
    __tablename__ = 'habits'

    habit_id: int = Column(Integer, primary_key=True)
    user_id: int = Column(
        Integer,
        ForeignKey('users.user_id'),
        nullable=False
    )
    name: str = Column(String, nullable=False)
    description: str = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)


class HabitLog(Base):
    """
    Model reprezentujący dzienny wpis logu realizacji nawyku.

    Atrybuty:
        habit_log_id – unikalne ID wpisu (klucz główny),
        habit_id     – ID nawyku (klucz obcy do habits.habit_id),
        description  – dodatkowy opis realizacji (opcjonalny),
        duration     – czas trwania aktywności w minutach (opcjonalny),
        date         – data wykonania wpisu,
        completed_at – znacznik czasu ukończenia (None jeśli nieukończone).
    """
    __tablename__ = 'habit_logs'

    habit_log_id: int = Column(Integer, primary_key=True)
    habit_id: int = Column(
        Integer,
        ForeignKey('habits.habit_id'),
        nullable=False
    )
    description: str = Column(String, nullable=True)
    duration: float = Column(Float, nullable=True)
    date = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True, default=None)


def init_db() -> None:
    """
    Inicjalizuje (tworzy) bazę danych SQLite na podstawie zdefiniowanych modeli.

    Tworzy plik 'habit_tracker.db' w bieżącym katalogu oraz tabele.
    """
    engine = get_engine()
    Base.metadata.create_all(engine)
