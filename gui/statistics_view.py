import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from sqlalchemy.orm import Session
from db.models import Habit, HabitLog
from db.session import get_engine
from datetime import datetime

from logic import habit_manager


class StatisticsView(tk.Toplevel):
    def __init__(self, parent, user_id):
        """
        Initialize the statistics window for analyzing habit performance.
        """
        super().__init__(parent)
        self.title("Statystyki nawyków")
        self.geometry("400x300")
        self.user_id = user_id

        # --- Habit selection dropdown ---
        ttk.Label(self, text="Wybierz nawyk:").pack(pady=5)
        self.habit_var = tk.StringVar()  # Variable to store selected habit name
        self.habit_combo = ttk.Combobox(self, textvariable=self.habit_var, state="readonly")
        self.habit_combo.pack(pady=5)
        self.load_habits()  # Populate the dropdown with user's habits

        # --- Date range selection (from - to) ---
        frame = ttk.Frame(self)
        frame.pack(pady=10)
        ttk.Label(frame, text="Od:").grid(row=0, column=0, padx=5)
        self.from_date = DateEntry(frame, date_pattern="dd.mm.yyyy")  # Start date picker
        self.from_date.grid(row=0, column=1, padx=5)
        ttk.Label(frame, text="Do:").grid(row=0, column=2, padx=5)
        self.to_date = DateEntry(frame, date_pattern="dd.mm.yyyy")    # End date picker
        self.to_date.grid(row=0, column=3, padx=5)

        # --- Button to trigger statistics calculation ---
        ttk.Button(self, text="Pokaż statystyki", command=self.show_stats).pack(pady=10)

        # --- Area to display results ---
        self.result_label = ttk.Label(self, text="", justify="left")
        self.result_label.pack(pady=10, fill=tk.X)

    def load_habits(self):
        """
        Load all habits for the current user and populate the dropdown.
        """
        engine = get_engine()
        with Session(engine) as session:
            habits = habit_manager.load_habits_for_user(self.user_id)
            self.habits = {f"{habit.name}: {habit.description}" : habit.habit_id for habit in habits}
            self.habit_combo['values'] = list(self.habits.keys())
            if habits:
                self.habit_combo.current(0)  # Select the first habit by default

    def show_stats(self):
        """
        Calculate and display statistics for the selected habit and date range.
        """
        habit_name = self.habit_var.get()
        if not habit_name:
            messagebox.showerror("Błąd", "Wybierz nawyk.")
            return
        habit_id = self.habits[habit_name]
        date_from = self.from_date.get_date()
        date_to = self.to_date.get_date()
        if date_from > date_to:
            messagebox.showerror("Błąd", "Data początkowa nie może być po dacie końcowej.")
            return

        # Query all logs for the selected habit and date range
        engine = get_engine()
        with Session(engine) as session:
            logs = session.query(HabitLog).filter(
                HabitLog.habit_id == habit_id,
                HabitLog.date >= date_from,
                HabitLog.date <= date_to
            ).all()

        # Calculate statistics
        total = len(logs)  # Total number of days/logs in the period
        completed = sum(1 for log in logs if log.completed_at)  # How many were completed
        streak = self.calculate_streak(logs)  # Longest streak of completed days

        # Display results
        self.result_label.config(
            text=f"Liczba wystąpień w powyższym okresie: {total}\n"
                 f"Wykonano: {completed}\n"
                 f"Najdłuższa seria: {streak}"
        )

    def calculate_streak(self, logs):
        """
        Calculate the longest streak of consecutive days with completed logs.
        """
        # Extract and sort dates where the habit was completed
        dates = sorted([log.date for log in logs if log.completed_at])
        if not dates:
            return 0  # No completions
        streak = max_streak = 1
        for i in range(1, len(dates)):
            # Check if the current date is consecutive to the previous
            if (dates[i] - dates[i-1]).days == 1:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 1  # Reset streak if not consecutive
        return max_streak
