"""
gui/register_screen.py

Zawiera ekran rejestracji użytkownika (GUI + logika walidacji danych i zapis do bazy).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session

from db.session import get_engine
from logic.auth import register


def attempt_register(
    username: str,
    password: str,
    re_password: str,
    window: tk.Tk
) -> None:
    """
    Waliduje dane rejestracyjne i próbuje zarejestrować nowego użytkownika w bazie.

    :param username: wprowadzona nazwa użytkownika
    :param password: wprowadzone hasło
    :param re_password: powtórzone hasło
    :param window: okno rejestracji, które zostanie zamknięte po udanej rejestracji
    """
    if not username or not password:
        messagebox.showerror("Błąd", "Wszystkie pola są wymagane.")
        return

    if password != re_password:
        messagebox.showerror("Błąd", "Hasła nie są identyczne.")
        return

    engine = get_engine()
    with Session(engine) as session:
        try:
            register(session, username, password)
            messagebox.showinfo("Sukces", "Rejestracja zakończona sukcesem!")
            window.destroy()
        except ValueError as error:
            messagebox.showerror("Błąd", str(error))


class RegisterScreen:
    """
    Klasa odpowiedzialna za wyświetlenie i obsługę ekranu rejestracji użytkownika.
    """

    def __init__(self) -> None:
        """
        Inicjalizuje komponenty GUI ekranu rejestracji i uruchamia pętlę zdarzeń.
        """
        self.window = tk.Tk()
        self.window.title("Habit Tracker - Rejestracja")
        self.window.geometry("375x150")
        self.window.resizable(width=False, height=False)

        self._create_widgets()
        self._on_enter_pressed()

        self.window.mainloop()

    def _create_widgets(self) -> None:
        """
        Tworzy i rozmieszcza widżety w oknie rejestracji.
        """
        root_frame = ttk.Frame(self.window, padding=20)
        root_frame.pack(expand=True, fill=tk.BOTH)

        # Nazwa użytkownika
        ttk.Label(root_frame, text="Nazwa użytkownika:")\
            .grid(row=0, column=0, sticky=tk.E, pady=(0, 5), padx=5)
        self.user_entry = ttk.Entry(root_frame, width=35)
        self.user_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5), padx=(0, 5))

        # Hasło
        ttk.Label(root_frame, text="Hasło:")\
            .grid(row=1, column=0, sticky=tk.E, pady=(0, 5), padx=5)
        self.password_entry = ttk.Entry(root_frame, show="*")
        self.password_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 5), padx=(0, 5))

        # Powtórz hasło
        ttk.Label(root_frame, text="Powtórz hasło:")\
            .grid(row=2, column=0, sticky=tk.E, pady=(0, 5), padx=5)
        self.re_password_entry = ttk.Entry(root_frame, show="*")
        self.re_password_entry.grid(row=2, column=1, sticky=tk.W, pady=(0, 5), padx=(0, 5))

        # Przycisk rejestracji
        ttk.Button(
            root_frame,
            text="Zarejestruj",
            command=self._on_register_clicked
        ).grid(row=3, column=0, columnspan=2, pady=(10, 0))

    def _on_enter_pressed(self) -> None:
        """
        Obsługuje naciśnięcie klawisza Enter – wyzwala próbę rejestracji.
        """
        self.window.bind("<Return>", lambda event: self._on_register_clicked())


    def _on_register_clicked(self) -> None:
        """
        Pobiera dane z pól wejściowych i wywołuje funkcję attempt_register.
        """
        attempt_register(
            username=self.user_entry.get(),
            password=self.password_entry.get(),
            re_password=self.re_password_entry.get(),
            window=self.window
        )
