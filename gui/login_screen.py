"""
gui/login_screen.py

Moduł ekranu logowania do aplikacji Habit Tracker.
Zawiera klasę LoginScreen odpowiedzialną za obsługę logowania i przejście do rejestracji.
"""

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from sqlalchemy.orm import Session

from db.session import get_engine
from gui import register_screen
from logic import auth


class LoginScreen:
    """
    Klasa wyświetlająca ekran logowania użytkownika.
    Pozwala na podanie loginu i hasła oraz przejście do rejestracji.
    """

    def __init__(self) -> None:
        """
        Inicjalizuje okno logowania, ustawia układ GUI i obsługuje zdarzenia.
        """
        self.user = None
        self.window = tk.Tk()
        self.window.title("Habit Tracker - Logowanie")
        self.window.geometry("350x250")
        self.window.resizable(False, False)

        # Główny kontener
        root = ttk.Frame(self.window, padding=20)
        root.pack(expand=True, fill=tk.BOTH)

        # Sekcja logowania
        login_frame = ttk.LabelFrame(root, text="Logowanie")
        login_frame.pack(expand=True, fill=tk.BOTH)

        # Pole: nazwa użytkownika
        ttk.Label(login_frame, text="Użytkownik:").grid(
            row=0, column=0, sticky=tk.E, pady=(0, 5), padx=5
        )
        user_entry = ttk.Entry(login_frame, width=35)
        user_entry.grid(
            row=0, column=1, sticky=tk.W, pady=(0, 5), padx=(0, 5)
        )

        # Pole: hasło
        ttk.Label(login_frame, text="Hasło:").grid(
            row=1, column=0, sticky=tk.E, pady=(0, 5), padx=5
        )
        password_entry = ttk.Entry(login_frame, show="*", width=35)
        password_entry.grid(
            row=1, column=1, sticky=tk.W, pady=(0, 5), padx=(0, 5)
        )

        # Obsługa klawisza Enter
        self.window.bind("<Return>", lambda event: self.attempt_login(user_entry.get(), password_entry.get()))

        # Przycisk logowania
        ttk.Button(
            login_frame,
            text="Zaloguj",
            command=lambda: self.attempt_login(
                user_entry.get(), password_entry.get()
            ),
        ).grid(row=3, column=0, columnspan=2, pady=(5, 0))

        # Sekcja rejestracji
        register_frame = ttk.LabelFrame(root, text="Rejestracja")
        register_frame.pack(expand=True, fill=tk.BOTH)

        # Przycisk rejestracji
        ttk.Button(
            register_frame,
            text="Zarejestruj się",
            command=lambda: register_screen.RegisterScreen(),
        ).pack(expand=True, fill=tk.BOTH, pady=20, padx=20)

        self.window.mainloop()

    def attempt_login(self, username: str, password: str) -> None:
        """
        Próbuje zalogować użytkownika na podstawie podanych danych.
        Wyświetla komunikat o sukcesie lub błędzie.
        :param username: Nazwa użytkownika
        :param password: Hasło użytkownika
        """
        engine = get_engine()
        with Session(engine) as session:
            user = auth.login(session, username, password)
            if user:
                messagebox.showinfo("Sukces", "Zalogowano!")
                self.user = user
                self.window.destroy()
            else:
                messagebox.showerror("Błąd", "Nieprawidłowy login lub hasło.")
