import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session

from db.models import Habit
from db.session import get_engine
from gui.habit_editor import HabitEditor

class HabitsManager(tk.Toplevel):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.title("Habit Manager")
        self.geometry("600x500")
        self.user_id = user_id
        self.habits = None
        self.selected_habit = None
        self.on_edit = lambda: HabitEditor(self, user_id=self.user_id, refresh_callback=self.load_table, habit_to_edit=self.selected_habit)  # funkcja wywoływana przy edycji

        # Tabela (Treeview)
        table_frame = ttk.Frame(self)
        self.tree = ttk.Treeview(table_frame, columns=("name", "description", "created_at"), show="headings", selectmode="browse")
        self.tree.heading("name", text="Nazwa")
        self.tree.heading("description", text="Opis")
        self.tree.heading("created_at", text="Utworzono")
        self.tree.pack(fill=tk.BOTH, expand=True)
        table_frame.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Dodaj czynność", command=lambda: HabitEditor(self, user_id=self.user_id, refresh_callback=self.load_table)).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="Edytuj czynność", command=self.on_edit).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="Usuń czynność", command=self.delete_habit).pack(side=tk.LEFT, padx=5, pady=5)

        self.load_table()

        # Obsługa zaznaczenia wiersza
        self.tree.bind("<<TreeviewSelect>>", self.on_row_selected)

    def on_row_selected(self, event):
        selected = self.tree.selection()
        if selected:
            habit_id = int(selected[0])
            habit = next((h for h in self.habits if h.habit_id == habit_id), None)
            if habit:
                self.selected_habit = habit

    def load_habits(self):
        engine = get_engine()
        with Session(engine) as session:
            habits = session.query(Habit).filter_by(user_id=self.user_id).all()
            if not habits:
                messagebox.showerror("Błąd", "Brak zdefiniowanych czynności.")
                return None
            return habits

    def load_table(self):
        self.habits = self.load_habits()
        if self.habits is not None:
            self.tree.delete(*self.tree.get_children())
            for habit in self.habits:
                self.tree.insert("", tk.END, iid=habit.habit_id, values=(habit.name, habit.description, habit.created_at))

    def delete_habit(self):
        habit = self.selected_habit
        engine = get_engine()
        with Session(engine) as session:
            session.delete(habit)
            session.commit()
        self.load_table()