"""
main.py

Moduł główny aplikacji Habit Tracker.
Inicjuje bazę danych i uruchamia pętlę logowania oraz główny ekran aplikacji.
"""

import sys

from db.session import get_engine
import db.models as db
from gui.login_screen import LoginScreen
from gui.main_screen import MainScreen


def main() -> None:
    """
    Główna funkcja uruchamiająca aplikację.
    - Tworzy i inicjalizuje bazę danych.
    - Wyświetla ekran logowania.
    - Po poprawnym logowaniu otwiera główny ekran aplikacji.
    - Powtarza proces do momentu wylogowania się użytkownika.
    """
    # Inicjalizacja bazy danych
    engine = get_engine()
    db.Base.metadata.create_all(engine)
    db.init_db()

    # Pętla logowania i działania aplikacji
    running = True
    while running:
        login_screen = LoginScreen()
        user = login_screen.user
        if user is None:
            sys.exit("Nie udało się zalogować. Aplikacja zostanie zakończona.")
        main_screen = MainScreen(user)
        # Po zamknięciu głównego ekranu sprawdzamy czy użytkownik się wylogował
        running = main_screen.log_out


if __name__ == "__main__":
    main()
