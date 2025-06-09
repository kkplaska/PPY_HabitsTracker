"""
gui/statistics_view.py

Zawiera klasę StatisticsView, która odpowiada za:
- wybór zakresu dat do analizy,
- wyświetlanie statystyk globalnych (wszystkie nawyki),
- wyświetlanie statystyk wybranego nawyku,
- generowanie i wyświetlanie wykresu słupkowego wykonanych/niewykonanych wpisów.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date, timedelta
from typing import List, Dict

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry
from sqlalchemy.orm import Session

from db.models import Habit, HabitLog
from db.session import get_engine
from utils.statistics import calculate_max_streak


class StatisticsView(tk.Toplevel):
    """
    Okno dialogowe do wyświetlania statystyk nawyków użytkownika.
    """

    def __init__(
        self,
        parent: tk.Widget,
        user_id: int,
        from_date: date = None,
        to_date: date = None
    ) -> None:
        """
        Inicjalizuje widok statystyk.

        :param parent: rodzicielski widget (root lub inne Toplevel)
        :param user_id: identyfikator zalogowanego użytkownika
        :param from_date: data początkowa zakresu (domyślnie 30 dni temu)
        :param to_date: data końcowa zakresu (domyślnie dzisiaj)
        """
        super().__init__(parent)
        self.title("Statystyki nawyków")
        self.geometry("700x1000")
        self.user_id = user_id

        # Domyślny zakres: ostatnie 30 dni
        today = datetime.now().date()
        self.from_date = from_date or (today - timedelta(days=30))
        self.to_date = to_date or today

        self._create_widgets()
        self._load_habits_and_refresh()

    def _create_widgets(self) -> None:
        """
        Tworzy i układa wszystkie widgety w oknie.
        """
        # Nagłówek wyboru dat
        ttk.Label(
            self,
            text="Okres statystyk",
            font=("Arial", 12, "bold")
        ).pack(pady=(15, 5))

        dates_frame = ttk.Frame(self)
        dates_frame.pack(pady=10)

        ttk.Label(dates_frame, text="Od:").grid(row=0, column=0, padx=5)
        self.from_date_entry = DateEntry(
            dates_frame,
            date_pattern="dd.mm.yyyy"
        )
        self.from_date_entry.set_date(self.from_date)
        self.from_date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(dates_frame, text="Do:").grid(row=0, column=2, padx=5)
        self.to_date_entry = DateEntry(
            dates_frame,
            date_pattern="dd.mm.yyyy"
        )
        self.to_date_entry.set_date(self.to_date)
        self.to_date_entry.grid(row=0, column=3, padx=5)

        ttk.Button(
            dates_frame,
            text="Odśwież",
            command=self.refresh_stats
        ).grid(row=0, column=4, padx=10)

        # Separator
        ttk.Separator(self, orient="horizontal")\
            .pack(fill=tk.X, pady=10)

        # Statystyki globalne
        ttk.Label(
            self,
            text="Statystyki globalne (wszystkie nawyki)",
            font=("Arial", 12, "bold")
        ).pack(pady=(15, 5))
        self.global_stats_label = ttk.Label(
            self,
            text="",
            justify="left"
        )
        self.global_stats_label.pack(
            pady=5,
            fill=tk.X
        )

        # Ramka na wykres
        self.chart_frame = tk.Frame(self)
        self.chart_frame.pack(
            fill=tk.BOTH,
            expand=True,
            pady=10
        )

        # Separator
        ttk.Separator(self, orient="horizontal")\
            .pack(fill=tk.X, pady=10)

        # Statystyki pojedynczego nawyku
        ttk.Label(
            self,
            text="Statystyki wybranego nawyku",
            font=("Arial", 12, "bold")
        ).pack(pady=(15, 5))

        habit_frame = ttk.Frame(self)
        habit_frame.pack(pady=10, fill=tk.X)
        ttk.Label(habit_frame, text="Wybierz nawyk:")\
            .grid(row=0, column=0, padx=5)

        self.habit_var = tk.StringVar()
        self.habit_combo = ttk.Combobox(
            habit_frame,
            textvariable=self.habit_var,
            state="readonly",
            width=30
        )
        self.habit_combo.grid(row=0, column=1, padx=5)
        self.habit_combo.bind(
            "<<ComboboxSelected>>",
            lambda _: self.refresh_habit_stats()
        )

        self.habit_stats_label = ttk.Label(
            self,
            text="",
            justify="left"
        )
        self.habit_stats_label.pack(
            pady=5,
            fill=tk.X
        )

    def _load_habits_and_refresh(self) -> None:
        """
        Ładuje listę nawyków i od razu odświeża wszystkie widoki.
        """
        self.load_habits()
        self.refresh_stats()

    def load_habits(self) -> None:
        """
        Pobiera z bazy wszystkie nawyki zalogowanego użytkownika
        i uzupełnia combobox.
        """
        engine = get_engine()
        with Session(engine) as session:
            habits = session.query(Habit)\
                            .filter_by(user_id=self.user_id)\
                            .all()

        # Słownik: etykieta -> obiekt Habit
        self.habits: Dict[str, Habit] = {
            f"{h.name}: {h.description}": h
            for h in habits
        }
        values = list(self.habits.keys())
        self.habit_combo['values'] = values
        if values:
            self.habit_combo.current(0)

    def refresh_stats(self) -> None:
        """
        Odświeża statystyki globalne, statystyki wybranego nawyku
        oraz generuje wykres słupkowy.
        """
        date_from = self.from_date_entry.get_date()
        date_to = self.to_date_entry.get_date()
        if date_from > date_to:
            messagebox.showerror(
                "Błąd",
                "Data początkowa nie może być po dacie końcowej."
            )
            return

        self.show_global_stats(date_from, date_to)
        self.refresh_habit_stats(date_from, date_to)
        self.show_chart(date_from, date_to)

    def show_global_stats(self, date_from: date, date_to: date) -> None:
        """
        Oblicza i wyświetla:
         - liczba wszystkich wpisów,
         - liczba wykonanych i niewykonanych,
         - najdłuższa seria w danym okresie.
        """
        engine = get_engine()
        with Session(engine) as session:
            logs: List[HabitLog] = (
                session.query(HabitLog)
                .join(Habit)
                .filter(
                    Habit.user_id == self.user_id,
                    HabitLog.date >= date_from,
                    HabitLog.date <= date_to
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

    def refresh_habit_stats(self, date_from: date = None, date_to: date = None) -> None:
        """
        Oblicza i wyświetla statystyki wybranego nawyku:
         - liczba wpisów,
         - liczba wykonanych/niewykonanych,
         - najdłuższa seria.
        """
        if date_from is None or date_to is None:
            date_from = self.from_date_entry.get_date()
            date_to = self.to_date_entry.get_date()

        habit_key = self.habit_var.get()
        habit = self.habits.get(habit_key)
        if habit is None:
            self.habit_stats_label.config(text="Brak danych.")
            return

        if date_from > date_to:
            self.habit_stats_label.config(text="Błąd zakresu dat.")
            return

        engine = get_engine()
        with Session(engine) as session:
            logs: List[HabitLog] = (
                session.query(HabitLog)
                .filter(
                    HabitLog.habit_id == habit.habit_id,
                    HabitLog.date >= date_from,
                    HabitLog.date <= date_to
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

    def show_chart(self, date_from: date, date_to: date) -> None:
        """
        Generuje wykres słupkowy dla każdego nawyku
        – liczba dni wykonanych i niewykonanych.
        """
        completed_counts: List[int] = []
        uncompleted_counts: List[int] = []
        labels = list(self.habits.keys())

        engine = get_engine()
        with Session(engine) as session:
            for key in labels:
                habit = self.habits[key]
                logs: List[HabitLog] = (
                    session.query(HabitLog)
                    .filter(
                        HabitLog.habit_id == habit.habit_id,
                        HabitLog.date >= date_from,
                        HabitLog.date <= date_to
                    )
                    .all()
                )
                completed = sum(1 for log in logs if log.completed_at)
                uncompleted = sum(1 for log in logs if not log.completed_at)
                completed_counts.append(completed)
                uncompleted_counts.append(uncompleted)

        self._plot_bar_chart(labels, completed_counts, uncompleted_counts)

    def _plot_bar_chart(
        self,
        habit_names: List[str],
        completed: List[int],
        uncompleted: List[int]
    ) -> None:
        """
        Rysuje i umieszcza w oknie wykres słupkowy.
        """
        # Wyczyść poprzedni wykres
        for w in self.chart_frame.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(8, 4))
        x = range(len(habit_names))
        width = 0.35

        ax.bar(
            [i - width/2 for i in x],
            completed,
            width,
            label='Wykonano',
            color='green'
        )
        ax.bar(
            [i + width/2 for i in x],
            uncompleted,
            width,
            label='Nie wykonano',
            color='red'
        )
        ax.set_xticks(list(x))
        ax.set_xticklabels(habit_names, rotation=45, ha='right')
        ax.set_ylabel('Liczba dni')
        ax.set_title('Statystyki nawyków')
        ax.legend()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(
            fill=tk.BOTH,
            expand=True
        )
