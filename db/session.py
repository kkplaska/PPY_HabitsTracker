"""
db/session.py

Moduł odpowiedzialny za konfigurację i tworzenie instancji silnika (Engine)
SQLAlchemy dla połączenia z bazą danych SQLite.
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# Ścieżka do bazy danych SQLite
DATABASE_URL: str = "sqlite:///habit_tracker.db"


def get_engine() -> Engine:
    """
    Tworzy i zwraca instancję obiektu Engine służącą do obsługi połączeń
    z bazą danych SQLite.

    :return: obiekt Engine skonfigurowany pod DATABASE_URL
    """
    return create_engine(
        DATABASE_URL,
        echo=False,  # wyłącz logowanie SQL w konsoli
        future=True  # użyj nowego stylu SQLAlchemy 2.0
    )
