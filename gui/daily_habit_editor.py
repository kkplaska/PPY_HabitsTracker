import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from sqlalchemy.orm import Session
from db.models import HabitLog, Habit
from db.session import get_engine
from datetime import datetime

from logic import habit_manager


class DailyHabitEditor(tk.Toplevel):
    def __init__(self, parent, date, user_id, refresh_callback=None, habitLog_to_edit: HabitLog = None):
        super().__init__(parent)
        self.user_id = user_id
        self.title("Daily Habit Editor")
        self.geometry("300x250")
        self.dhe_frame = ttk.Frame(self)
        self.refresh_callback = refresh_callback
        self.habitLog_to_edit = habitLog_to_edit
        self.habits = habit_manager.load_habits_for_user(self.user_id)
        self.date = date

        self.dhe_frame = ttk.Frame(self)
        self.dhe_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Czynność (OptionMenu) ---
        ttk.Label(self.dhe_frame, text="Czynność:").grid(row=0, column=0, sticky="e", pady=5)
        self.habit_var = tk.StringVar()
        habit_names = [f"{habit.name}: {habit.description}" for habit in self.habits]
        self.habit_menu = ttk.OptionMenu(self.dhe_frame, self.habit_var, habit_names[0] if habit_names else "", *habit_names)
        self.habit_menu.grid(row=0, column=1, sticky="w", pady=5)

        # --- Szczegóły (Entry) ---
        ttk.Label(self.dhe_frame, text="Szczegóły:").grid(row=1, column=0, sticky="e", pady=5)
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(self.dhe_frame, textvariable=self.description_var, width=28)
        self.description_entry.grid(row=1, column=1, sticky="w", pady=5)

        # --- Czas trwania (Entry) ---
        self.duration_var = tk.StringVar()
        validate_cmd = (self.dhe_frame.register(self.validate_float), '%P')
        ttk.Label(self.dhe_frame, text="Czas trwania (h):").grid(row=2, column=0, sticky="e", pady=5)
        self.duration_entry = ttk.Entry(self.dhe_frame, textvariable=self.duration_var, width=10, validate='key', validatecommand=validate_cmd)
        self.duration_entry.grid(row=2, column=1, sticky="w", pady=5)


        # --- Data (Entry) ---
        self.date_var = tk.StringVar()
        ttk.Label(self.dhe_frame, text="Data:").grid(row=3, column=0, sticky="e", pady=5)
        self.date_entry = DateEntry(self.dhe_frame, textvariable=self.date_var, date_pattern='yyyy-mm-dd', width=12)
        self.date_entry.grid(row=3, column=1, sticky="w", pady=5)

        # --- Ukończono (Entry) ---
        self.completed_at_var = tk.StringVar()
        ttk.Label(self.dhe_frame, text="Zakończono dnia:").grid(row=4, column=0, sticky="e", pady=5)
        self.completed_at_entry = ttk.Entry(self.dhe_frame, textvariable=self.completed_at_var, width=24, )
        self.completed_at_entry.grid(row=4, column=1, sticky="w", pady=5)

        # --- Przycisk zapisu ---
        ttk.Button(self.dhe_frame, text="Zapisz", command=self.save_habit_log, takefocus=True).grid(row=5, column=0, columnspan=2, pady=15)

        # Edycja czynności
        if self.habitLog_to_edit:
            self.fill_fields()

    @staticmethod
    def validate_float(num):
        if num == "":
            return True
        try:
            n = float(num)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_float(num):
        try:
            n = float(num)
            return n
        except ValueError:
            return 0.0

    @staticmethod
    def is_valid_date(date_text):
        if date_text == "" or date_text == "None" or date_text is None:
            return None
        try:
            date = datetime.strptime(date_text, "%Y-%m-%d %H:%M")
            return date
        except ValueError:
            try:
                date = datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S")
                return date
            except ValueError:
                messagebox.showerror("Błąd", "Nieprawidłowy format daty i godziny. Użyj: YYYY-MM-DD HH:MM")
                return False

    def fill_fields(self):
        # Set habit selection and details from existing HabitLog
        habit = next((h for h in self.habits if h.habit_id == self.habitLog_to_edit.habit_id), None)
        if habit:
            self.habit_var.set(f"{habit.name}: {habit.description}")
            self.description_var.set(self.habitLog_to_edit.description if hasattr(self.habitLog_to_edit, "description") else "")
            self.duration_var.set(self.habitLog_to_edit.duration if hasattr(self.habitLog_to_edit, "duration") else "")
            self.completed_at_var.set(str(self.habitLog_to_edit.completed_at) if hasattr(self.habitLog_to_edit, "completed_at") else "")


    def save_habit_log(self):
        habit_name = self.habit_var.get()
        description = self.description_var.get().strip()

        if not habit_name:
            messagebox.showwarning("Błąd", "Musisz wybrać czynność.")
            return

        selected_habit = next((h for h in self.habits if f"{h.name}: {h.description}" == habit_name), None)
        if not selected_habit:
            messagebox.showerror("Błąd", "Wybrana czynność nie istnieje.")
            return
        completed_at_date = None
        if self.completed_at_var.get() != "":
            completed_at_date = self.is_valid_date(self.completed_at_var.get())

        session = Session(bind=get_engine())
        try:
            if self.habitLog_to_edit:
                # Update existing HabitLog
                self.habitLog_to_edit.habit_id = selected_habit.habit_id
                self.habitLog_to_edit.description = description
                self.habitLog_to_edit.duration = self.get_float(self.duration_var.get())
                self.habitLog_to_edit.date = datetime.strptime(self.date_var.get(), "%Y-%m-%d")
                self.habitLog_to_edit.completed_at = completed_at_date
                if completed_at_date is not None:
                    (session.query(HabitLog).filter(HabitLog.habitLog_id == self.habitLog_to_edit.habitLog_id).update({
                        HabitLog.habit_id: self.habitLog_to_edit.habit_id,
                        HabitLog.description: self.habitLog_to_edit.description,
                        HabitLog.duration: self.habitLog_to_edit.duration,
                        HabitLog.date: self.habitLog_to_edit.date,
                        HabitLog.completed_at: self.habitLog_to_edit.completed_at,
                    }))
                else:
                    (session.query(HabitLog).filter(HabitLog.habitLog_id == self.habitLog_to_edit.habitLog_id).update({
                        HabitLog.habit_id: self.habitLog_to_edit.habit_id,
                        HabitLog.description: self.habitLog_to_edit.description,
                        HabitLog.duration: self.habitLog_to_edit.duration,
                        HabitLog.date: self.habitLog_to_edit.date
                    }))
                session.commit()
                messagebox.showinfo("Sukces", "Dzienny wpis zaktualizowany.")
            else:
                # Create new HabitLog
                new_log = HabitLog(
                    habit_id=selected_habit.habit_id,
                    description=description,
                    duration=self.get_float(self.duration_var.get()),
                    date=datetime.strptime(self.date_var.get(), "%Y-%m-%d"),
                    completed_at=completed_at_date
                )
                session.add(new_log)
                session.commit()
                messagebox.showinfo("Sukces", "Dzienny wpis zapisany.")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Błąd", f"Nie udało się zapisać wpisu.\n{e}")
        finally:
            session.close()

        if self.refresh_callback:
            self.refresh_callback()

        self.destroy()
