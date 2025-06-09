"""
logic/auth.py

Moduł auth.py zawiera funkcje odpowiedzialne za:
- rejestrację nowych użytkowników (register)
- logowanie istniejących użytkowników (login)

Funkcje operują na sesji SQLAlchemy i wykorzystują mechanizm haszowania haseł.
"""

from sqlalchemy.orm import Session

from db.models import User
from utils.encryption import hash_password, check_password


def register(session: Session, username: str, password: str) -> User:
    """
    Rejestruje nowego użytkownika w bazie danych.

    :param session: aktywna sesja SQLAlchemy
    :param username: nazwa użytkownika (unikalna)
    :param password: hasło w postaci jawnej
    :return: obiekt User zapisany w bazie
    :raises ValueError: gdy użytkownik o podanej nazwie już istnieje
    """
    # Sprawdź, czy użytkownik już istnieje
    existing = session.query(User).filter_by(username=username).first()
    if existing:
        raise ValueError(f"Użytkownik o nazwie '{username}' już istnieje.")

    # Utwórz i zapisz nowego użytkownika z haszowanym hasłem
    user = User(username=username, password_hash=hash_password(password))
    session.add(user)
    session.commit()
    return user


def login(session: Session, username: str, password: str) -> User | None:
    """
    Próbuje zalogować użytkownika na podstawie podanego loginu i hasła.

    :param session: aktywna sesja SQLAlchemy
    :param username: nazwa użytkownika
    :param password: hasło w postaci jawnej
    :return: obiekt User, jeśli dane są prawidłowe; w przeciwnym razie None
    """
    user = session.query(User).filter_by(username=username).first()
    if user and check_password(password, user.password_hash):
        return user
    return None
