"""
gui/habit_editor.py

Moduł ekranu edycji nawyku w aplikacji Habit Tracker.
Zawiera klasę HabitEditor odpowiedzialną za edycję nawyku.
"""

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from sqlalchemy.orm import Session
from db.models import Habit
from db.session import get_engine
from datetime import datetime


class HabitEditor(tk.Toplevel):
    """
    Okno dialogowe do dodawania lub edycji nawyku użytkownika.
    Pozwala wprowadzić nazwę i opis nawyku oraz zapisać zmiany do bazy danych.
    """

    def __init__(
        self,
        parent: tk.Tk,
        user_id: int,
        refresh_callback=None,
        habit_to_edit: Habit = None
    ):
        """
        Inicjalizuje okno edytora nawyku.

        :param parent: Okno nadrzędne (root lub inne Toplevel)
        :param user_id: ID użytkownika, do którego należy nawyk
        :param refresh_callback: Funkcja do odświeżenia listy nawyków po zapisie
        :param habit_to_edit: Obiekt Habit do edycji (jeśli None, tryb dodawania)
        """
        super().__init__(parent)
        self.title("Habit Editor")
        self.geometry("360x120")
        self.resizable(False, False)
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.habit_to_edit = habit_to_edit

        self._build_ui()

        # Jeśli edytujemy istniejący nawyk, wypełnij pola
        if self.habit_to_edit:
            self.fill_fields()

    def _build_ui(self) -> None:
        """
        Tworzy i rozmieszcza widżety w oknie edytora.
        """
        root = ttk.Frame(self, padding=20)
        root.pack(expand=True, fill=tk.BOTH)

        # Pole: nazwa czynności
        ttk.Label(root, text="Nazwa czynności:").grid(
            row=0, column=0, sticky=tk.E, pady=(0, 5), padx=5
        )
        self.name_entry = ttk.Entry(root, width=35)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5), padx=(0, 5))

        # Pole: opis nawyku
        ttk.Label(root, text="Opis:").grid(
            row=1, column=0, sticky=tk.E, pady=(0, 5), padx=5
        )
        self.desc_entry = ttk.Entry(root, width=35)
        self.desc_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 5), padx=(0, 5))

        # Przycisk zapisu
        ttk.Button(
            root, text="Zapisz", command=self.save_habit
        ).grid(row=2, column=0, columnspan=2, pady=(5, 0))

        # Obsługa klawisza Enter
        self.bind("<Return>", lambda event: self.save_habit())

    def fill_fields(self) -> None:
        """
        Wypełnia pola edytora danymi istniejącego nawyku (tryb edycji).
        """
        self.name_entry.insert(0, self.habit_to_edit.name)
        self.desc_entry.insert(0, self.habit_to_edit.description)

    def save_habit(self) -> None:
        """
        Zapisuje nowy nawyk lub aktualizuje istniejący w bazie danych.
        Waliduje dane wejściowe i obsługuje wyjątki.
        """
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()

        if not name:
            messagebox.showwarning("Błąd", "Nazwa nie może być pusta.")
            return

        session = Session(bind=get_engine())
        try:
            if self.habit_to_edit:
                self._update_habit(session, name, desc)
            else:
                self._add_new_habit(session, name, desc)
            session.commit()
        except Exception as e:
            session.rollback()
            messagebox.showerror("Błąd", f"Nie udało się zapisać czynności.\n{e}")
        finally:
            session.close()

        if self.refresh_callback:
            self.refresh_callback()  # Odśwież listę nawyków

        self.destroy()

    def _update_habit(self, session: Session, name: str, desc: str) -> None:
        """
        Aktualizuje istniejący nawyk w bazie danych.

        :param session: Aktywna sesja SQLAlchemy
        :param name: Nowa nazwa nawyku
        :param desc: Nowy opis nawyku
        """
        self.habit_to_edit.name = name
        self.habit_to_edit.description = desc
        session.query(Habit).filter(
            Habit.habit_id == self.habit_to_edit.habit_id,
            Habit.user_id == self.habit_to_edit.user_id
        ).update({
            Habit.name: name,
            Habit.description: desc,
            Habit.created_at: datetime.now()
        })
        messagebox.showinfo("Sukces", "Czynność zaktualizowana.")

    def _add_new_habit(self, session: Session, name: str, desc: str) -> None:
        """
        Dodaje nowy nawyk do bazy danych.

        :param session: Aktywna sesja SQLAlchemy
        :param name: Nazwa nowego nawyku
        :param desc: Opis nowego nawyku
        """
        new_habit = Habit(
            user_id=self.user_id,
            name=name,
            description=desc,
            created_at=datetime.now()
        )
        session.add(new_habit)
        messagebox.showinfo("Sukces", "Czynność zapisana.")
