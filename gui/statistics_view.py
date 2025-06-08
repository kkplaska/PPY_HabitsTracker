import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from tkcalendar import DateEntry
from sqlalchemy.orm import Session
from db.models import Habit, HabitLog
from db.session import get_engine
from datetime import datetime, timedelta
from utils.statistics import calculate_max_streak

from logic import habit_manager

class StatisticsView(tk.Toplevel):
    def __init__(self, parent, user_id, from_date=None, to_date=None):
        super().__init__(parent)
        self.title("Statystyki nawyków")
        self.geometry("700x1000")
        self.user_id = user_id

        # Domyślny zakres dat: ostatnie 30 dni
        self.from_date = (datetime.now() - timedelta(days=30)).date() if from_date == to_date else from_date
        self.to_date = to_date or datetime.now().date()


        # --- Wybór zakresu dat ---
        ttk.Label(self, text=f"Okres statystyk", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        dates_frame = ttk.Frame(self)
        dates_frame.pack(pady=10)
        ttk.Label(dates_frame, text="Od:").grid(row=0, column=0, padx=5)
        self.from_date_entry = DateEntry(dates_frame, date_pattern="dd.mm.yyyy")
        self.from_date_entry.set_date(self.from_date)
        self.from_date_entry.grid(row=0, column=1, padx=5)
        ttk.Label(dates_frame, text="Do:").grid(row=0, column=2, padx=5)
        self.to_date_entry = DateEntry(dates_frame, date_pattern="dd.mm.yyyy")
        self.to_date_entry.set_date(self.to_date)
        self.to_date_entry.grid(row=0, column=3, padx=5)
        ttk.Button(dates_frame, text="Odśwież", command=self.refresh_stats).grid(row=0, column=4, padx=10)

        # --- Separator <hr>
        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, pady=10)

        # --- Statystyki globalne ---
        ttk.Label(self, text=f"Statystyki globalne (wszystkie nawyki)", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        self.global_stats_label = ttk.Label(self, text="", justify="left")
        self.global_stats_label.pack(pady=5, fill=tk.X)

        # --- Wykres ---
        self.chart_frame = tk.Frame(self)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # # --- Przycisk do wyświetlania wykresu ---
        # ttk.Button(self, text="Pokaż wykres", command=self.show_chart).pack(pady=10)

        # --- Separator <hr>
        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, pady=10)

        # --- Statystyki pojedynczego nawyku ---
        ttk.Label(self, text="Statystyki wybranego nawyku", font=("Arial", 12, "bold")).pack(pady=(15, 5))

        habit_frame = ttk.Frame(self)
        habit_frame.pack(pady=10, fill=tk.X)
        ttk.Label(habit_frame, text="Wybierz nawyk:").grid(row=0, column=0, padx=5)
        self.habit_var = tk.StringVar()
        self.habit_combo = ttk.Combobox(habit_frame, textvariable=self.habit_var, state="readonly", width=30)
        self.habit_combo.grid(row=0, column=1, padx=5)
        self.habit_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_habit_stats())

        self.habit_stats_label = ttk.Label(self, text="", justify="left")
        self.habit_stats_label.pack(pady=5, fill=tk.X)

        # Załaduj nawyki i wyświetl statystyki
        self.habits = {}  # nazwa -> obiekt Habit
        self.load_habits()
        self.refresh_stats()

    def load_habits(self):
        """Załaduj nawyki użytkownika i wypełnij combobox."""
        engine = get_engine()
        with Session(engine) as session:
            habits = session.query(Habit).filter_by(user_id=self.user_id).all()
            self.habits = {f"{habit.name}: {habit.description}": habit for habit in habits}
        self.habit_combo['values'] = list(self.habits.keys())
        if self.habits:
            self.habit_combo.current(0)

    def refresh_stats(self):
        """Odśwież statystyki globalne i dla wybranego nawyku."""
        try:
            self.show_global_stats()
            self.refresh_habit_stats()
            self.show_chart()
        except:
            messagebox.showerror("Błąd", "Data początkowa nie może być po dacie końcowej.")
            return

    def show_global_stats(self):
        """Oblicz i wyświetl statystyki dla wszystkich nawyków w zakresie dat."""
        date_from = self.from_date_entry.get_date()
        date_to = self.to_date_entry.get_date()
        if date_from > date_to:
            raise Exception()

        engine = get_engine()
        with Session(engine) as session:
            logs = (
                session.query(HabitLog)
                .join(Habit)
                .filter(
                    Habit.user_id == self.user_id,
                    HabitLog.date >= date_from,
                    HabitLog.date <= date_to,
                )
                .all()
            )

        total = len(logs)
        completed = sum(1 for log in logs if log.completed_at)
        uncompleted = total - completed
        streak = calculate_max_streak(logs)

        self.global_stats_label.config(
            text=(
                f"Liczba wpisów: {total}\n"
                f"Wykonano: {completed}\n"
                f"Nie wykonano: {uncompleted}\n"
                f"Najdłuższa seria (dowolny nawyk): {streak}"
            )
        )

    def refresh_habit_stats(self):
        """Oblicz i wyświetl statystyki dla wybranego nawyku."""
        habit_name = self.habit_var.get()
        if not habit_name or habit_name not in self.habits:
            self.habit_stats_label.config(text="Brak danych.")
            return

        habit = self.habits[habit_name]
        date_from = self.from_date_entry.get_date()
        date_to = self.to_date_entry.get_date()
        if date_from > date_to:
            self.habit_stats_label.config(text="Błąd zakresu dat.")
            return

        engine = get_engine()
        with Session(engine) as session:
            logs = (
                session.query(HabitLog)
                .filter(
                    HabitLog.habit_id == habit.habit_id,
                    HabitLog.date >= date_from,
                    HabitLog.date <= date_to,
                )
                .all()
            )

        total = len(logs)
        completed = sum(1 for log in logs if log.completed_at)
        uncompleted = total - completed
        streak = calculate_max_streak(logs)

        self.habit_stats_label.config(
            text=(
                f"Liczba wpisów: {total}\n"
                f"Wykonano: {completed}\n"
                f"Nie wykonano: {uncompleted}\n"
                f"Najdłuższa seria: {streak}"
            )
        )

    def show_chart(self):
        """Wyświetl wykres słupkowy wykonanych/niewykonanych dla każdego nawyku."""
        date_from = self.from_date_entry.get_date()
        date_to = self.to_date_entry.get_date()
        if date_from > date_to:
            raise Exception()

        completed_counts = []
        uncompleted_counts = []
        habit_names = list(self.habits.keys())

        engine = get_engine()
        with Session(engine) as session:
            for habit_name in habit_names:
                habit = self.habits[habit_name]
                logs = session.query(HabitLog).filter(
                    HabitLog.habit_id == habit.habit_id,
                    HabitLog.date >= date_from,
                    HabitLog.date <= date_to
                ).all()
                completed = sum(1 for log in logs if log.completed_at)
                total_days = (date_to - date_from).days + 1
                uncompleted = sum(1 for log in logs if log.completed_at is None)
                completed_counts.append(completed)
                uncompleted_counts.append(uncompleted)

        self.plot_bar_chart(habit_names, completed_counts, uncompleted_counts)

    def plot_bar_chart(self, habit_names, completed_counts, uncompleted_counts):
        # Wyczyść poprzedni wykres
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(8, 4))
        x = range(len(habit_names))
        width = 0.35

        ax.bar([i - width/2 for i in x], completed_counts, width, label='Wykonano', color='green')
        ax.bar([i + width/2 for i in x], uncompleted_counts, width, label='Nie wykonano', color='red')
        ax.set_xticks(list(x))
        ax.set_xticklabels(habit_names, rotation=45, ha='right')
        ax.set_ylabel('Liczba dni')
        ax.set_title('Statystyki nawyków')
        ax.legend()

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
