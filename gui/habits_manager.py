"""
gui/habits_manager.py

Moduł ekranu zarządzania nawykami w aplikacji Habit Tracker.
Zawiera klasę HabitsManager odpowiedzialną za obsługę nawyków.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session
from typing import Optional

from db.models import Habit, HabitLog
from db.session import get_engine
from gui.habit_editor import HabitEditor


class HabitsManager(tk.Toplevel):
    """
    Okno menadżera nawyków.
    Pozwala na przeglądanie, dodawanie, edycję i usuwanie nawyków użytkownika.
    """

    def __init__(self, parent: tk.Tk, user_id: int) -> None:
        """
        Inicjalizuje okno menadżera nawyków.
        :param parent: Okno nadrzędne (root lub inne Toplevel)
        :param user_id: ID aktualnie zalogowanego użytkownika
        """
        super().__init__(parent)
        self.title("Menadżer nawyków")
        self.geometry("600x500")
        self.user_id: int = user_id
        self.habits: Optional[list[Habit]] = None
        self.selected_habit: Optional[Habit] = None

        # Tabela (Treeview)
        table_frame = ttk.Frame(self)
        self.tree = ttk.Treeview(
            table_frame,
            columns=("name", "description", "created_at"),
            show="headings",
            selectmode="browse"
        )
        self.tree.heading("name", text="Nazwa")
        self.tree.heading("description", text="Opis")
        self.tree.heading("created_at", text="Utworzono")
        self.tree.pack(fill=tk.BOTH, expand=True)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Przyciski akcji
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Dodaj czynność", command=self.add_habit).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="Edytuj czynność", command=self.edit_selected_habit).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="Usuń czynność", command=self.delete_habit).pack(side=tk.LEFT, padx=5, pady=5)

        self.load_table()

        # Obsługa zaznaczenia wiersza w tabeli
        self.tree.bind("<<TreeviewSelect>>", self.on_row_selected)

    def on_row_selected(self, event) -> None:
        """
        Obsługuje zaznaczenie wiersza w tabeli.
        Ustawia wybrany nawyk jako aktywny.
        """
        selected = self.tree.selection()
        if selected:
            habit_id = int(selected[0])
            habit = next((h for h in self.habits if h.habit_id == habit_id), None)
            if habit:
                self.selected_habit = habit

    def add_habit(self) -> None:
        """
        Otwiera okno dodawania nowego nawyku.
        """
        HabitEditor(self, user_id=self.user_id, refresh_callback=self.load_table)

    def edit_selected_habit(self) -> None:
        """
        Otwiera okno edycji wybranego nawyku.
        """
        if not self.selected_habit:
            messagebox.showerror("Błąd", "Nie został wybrany nawyk do edycji!")
            return
        HabitEditor(self, user_id=self.user_id, refresh_callback=self.load_table, habit_to_edit=self.selected_habit)

    def load_habits(self) -> Optional[list[Habit]]:
        """
        Pobiera listę nawyków użytkownika z bazy danych.
        :return: Lista obiektów Habit lub None, jeśli brak nawyków
        """
        engine = get_engine()
        with Session(engine) as session:
            habits = session.query(Habit).filter_by(user_id=self.user_id).all()
            if not habits:
                messagebox.showerror("Błąd", "Brak zdefiniowanych czynności.")
                return None
            return habits

    def load_table(self) -> None:
        """
        Ładuje dane do tabeli (Treeview) na podstawie nawyków użytkownika.
        """
        self.habits = self.load_habits()
        if self.habits is not None:
            self.tree.delete(*self.tree.get_children())
            for habit in self.habits:
                self.tree.insert(
                    "",
                    tk.END,
                    iid=habit.habit_id,
                    values=(habit.name, habit.description, habit.created_at)
                )
            self.selected_habit = None

    def delete_habit(self) -> None:
        """
        Usuwa wybrany nawyk oraz powiązane wpisy HabitLog z bazy danych.
        """
        habit = self.selected_habit
        if not habit:
            messagebox.showerror("Błąd", "Nie wybrano nawyku do usunięcia!")
            return
        confirm_box = messagebox.askyesno(
            title="Usuwanie nawyku",
            message=f"Czy na pewno chcesz usunąć '{habit.name}'?"
        )
        if confirm_box:
            engine = get_engine()
            with Session(engine) as session:
                session.query(HabitLog).filter_by(habit_id=habit.habit_id).delete()
                session.delete(habit)
                session.commit()
            self.load_table()
