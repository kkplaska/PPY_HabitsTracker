import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from sqlalchemy.orm import Session
from db.models import Habit
from db.session import get_engine
from datetime import datetime

class HabitEditor(tk.Toplevel):
    def __init__(self, parent, user_id, refresh_callback=None, habit_to_edit: Habit = None):
        super().__init__(parent)
        self.title("Habit Editor")
        self.geometry("300x250")
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.habit_to_edit = habit_to_edit

        # Pole: nazwa czynności
        ttk.Label(self, text="Nazwa czynności:").pack(pady=5)
        self.name_entry = ttk.Entry(self, width=30)
        self.name_entry.pack()

        # Pole: opis nawyku
        ttk.Label(self, text="Opis:").pack(pady=5)
        self.desc_entry = ttk.Entry(self, width=30)
        self.desc_entry.pack()

        # Przycisk zapisu
        ttk.Button(self, text="Zapisz", command=self.save_habit).pack(pady=15)

        # Edycja czynności
        if self.habit_to_edit:
            self.fill_fields()

    def fill_fields(self):
        self.name_entry.insert(0, self.habit_to_edit.name)
        self.desc_entry.insert(0, self.habit_to_edit.description)

    def save_habit(self):
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()

        if not name:
            messagebox.showwarning("Błąd", "Nazwa nie może być pusta.")
            return

        session = Session(bind=get_engine())

        try:
            if self.habit_to_edit:
                # Tryb edycji czynności
                self.habit_to_edit.name = name
                self.habit_to_edit.description = desc
                (session.query(Habit)
                 .filter(Habit.habit_id == self.habit_to_edit.habit_id)
                 .filter(Habit.user_id == self.habit_to_edit.user_id)
                 .update({
                    Habit.name: self.habit_to_edit.name,
                    Habit.description: self.habit_to_edit.description,
                    Habit.created_at: datetime.now()
                }))
                session.commit()
                messagebox.showinfo("Sukces", "Czynność zaktualizowana.")
            else:
                # Dodawanie nowej czynności
                new_habit = Habit(
                    user_id=self.user_id,
                    name=name,
                    description=desc,
                    created_at=datetime.now()
                )
                session.add(new_habit)
                session.commit()
                messagebox.showinfo("Sukces", "Czynność zapisana.")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Błąd", f"Nie udało się zapisać czynności.\n{e}")
        finally:
            session.close()

        if self.refresh_callback:
            self.refresh_callback()  # odśwież listę czynności w menadżerze czynności

        self.destroy()
