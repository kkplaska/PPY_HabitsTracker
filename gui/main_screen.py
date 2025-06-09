import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import Optional

from db.models import HabitLog, Habit
from db.session import get_engine
from gui.daily_habit_editor import DailyHabitEditor
from gui.habits_manager import HabitsManager
from gui.statistics_view import StatisticsView
from utils.export_pdf import PDFExporter


class MainScreen:
    """
    Główny ekran aplikacji Habit Tracker.
    Pozwala na przeglądanie, dodawanie, edycję, usuwanie i oznaczanie nawyków,
    a także na eksport statystyk i logów do PDF.
    """

    def __init__(self, user):
        """
        Inicjalizuje główny ekran aplikacji.
        :param user: Obiekt użytkownika (z bazy danych)
        """
        self.user = user
        self.from_date: date = datetime.today().date()
        self.to_date: date = (datetime.today() + timedelta(days=30)).date()
        self.from_date_var: Optional[tk.StringVar] = None
        self.to_date_var: Optional[tk.StringVar] = None
        self.log_out: bool = False
        self.window = tk.Tk()
        self.window.title(f"Habit Tracker - {self.user.username}")
        self.window.geometry("1200x400")
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)

        self.main_frame = ttk.Frame(self.window)
        self.main_frame.grid(column=0, row=0, padx=10, sticky=tk.NSEW)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=8)

        self.habits_frame = ttk.Frame(self.main_frame)
        self.habits_tree: Optional[ttk.Treeview] = None
        self.habit_log_list: list = []
        self.selected_habitLog: Optional[HabitLog] = None

        self.create_widgets()
        self.set_date_and_refresh()
        self.window.mainloop()

    def create_widgets(self) -> None:
        """Tworzy wszystkie widżety GUI."""
        # Góra
        top_frame = ttk.Frame(self.main_frame)
        top_frame.grid(column=0, row=0, sticky=tk.NSEW, columnspan=2)
        ttk.Label(top_frame, text=f"Witaj, {self.user.username}!", font=("Arial", 16)).pack(side=tk.LEFT)

        # Wybór daty
        date_frame = ttk.Frame(top_frame)
        date_frame.pack(side=tk.RIGHT, pady=5)
        ttk.Label(date_frame, text="Wskaż datę: ", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.E, columnspan=2)
        self.from_date_var = tk.StringVar(value=self.from_date.strftime("%d.%m.%Y"))
        self.to_date_var = tk.StringVar(value=self.to_date.strftime("%d.%m.%Y"))

        ttk.Label(date_frame, text="Od:").grid(row=1, column=0, padx=5)
        from_date_entry = DateEntry(
            date_frame,
            date_pattern="dd.mm.yyyy",
            textvariable=self.from_date_var
        )
        from_date_entry.set_date(self.from_date)
        from_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.E)

        ttk.Label(date_frame, text="Do:").grid(row=1, column=2, padx=5)
        to_date_entry = DateEntry(
            date_frame,
            date_pattern="dd.mm.yyyy",
            textvariable=self.to_date_var
        )
        to_date_entry.set_date(self.to_date)
        to_date_entry.grid(row=1, column=3, padx=5, pady=5, sticky=tk.E)

        ttk.Button(
            date_frame,
            text="Odśwież",
            command=self.set_date_and_refresh
        ).grid(row=0, column=3, padx=5, pady=5, sticky=tk.NSEW, columnspan=2)

        # Lista czynności - środek
        self.refresh_habits()

        # Przyciski dotyczące czynności - prawo
        right_button_frame = ttk.Frame(self.main_frame)
        right_button_frame.grid(column=1, row=1, sticky=tk.E)
        ttk.Button(right_button_frame, text="Dodaj czynność", command=self.add_habit_for_day).grid(column=0, row=0, padx=5, pady=5, sticky=tk.NSEW)

        mark_habit_frame = ttk.LabelFrame(right_button_frame, text="Wybrana czynność:")
        mark_habit_frame.grid(column=0, row=1, padx=5, pady=5, sticky=tk.E)
        ttk.Button(mark_habit_frame, text="Edytuj czynność", command=self.edit_habit_for_day).grid(column=0, row=0, padx=5, pady=5, sticky=tk.NSEW)
        ttk.Button(mark_habit_frame, text="Usuń czynność", command=self.delete_habit_for_day).grid(column=0, row=1, padx=5, pady=5, sticky=tk.NSEW)
        ttk.Button(mark_habit_frame, text="Wykonano", command=self.mark_habit_as_done).grid(column=0, row=2, padx=5, pady=5, sticky=tk.NSEW)
        ttk.Button(mark_habit_frame, text="Nie wykonano", command=self.mark_habit_as_undone).grid(column=0, row=3, padx=5, pady=5, sticky=tk.NSEW)

        # Przyciski ogólne - dół
        bottom_button_frame = ttk.Frame(self.main_frame)
        bottom_button_frame.grid(column=0, row=3, columnspan=2, pady=10, sticky=tk.S)
        ttk.Button(bottom_button_frame, text="Menadżer czynności", command=self.manage_habits).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="Statystyki", command=self.show_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="Eksport do PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="Wyloguj", command=self.logout).pack(side=tk.LEFT, padx=5)

    def clean_and_create_treeview(self) -> None:
        """Czyści i tworzy Treeview z listą czynności."""
        for widget in self.habits_frame.winfo_children():
            widget.destroy()

        self.habits_tree = ttk.Treeview(
            self.habits_frame,
            columns=("name", "date", "description", "details", "duration", "completed_at", "is_completed"),
            show="headings"
        )
        self.habits_tree.heading("name", text="Nazwa")
        self.habits_tree.heading("date", text="Data")
        self.habits_tree.heading("description", text="Opis")
        self.habits_tree.heading("details", text="Szczegóły")
        self.habits_tree.heading("duration", text="Czas trwania [min]")
        self.habits_tree.heading("completed_at", text="Ukończono")
        self.habits_tree.heading("is_completed", text="Wykonano")
        self.habits_tree.pack(fill=tk.BOTH, expand=True)
        self.habits_frame.grid(column=0, row=1, rowspan=2, sticky=tk.NSEW)
        self.habits_tree.bind("<<TreeviewSelect>>", self.on_row_selected)

    def on_row_selected(self, event) -> None:
        """Obsługuje wybór wiersza w Treeview."""
        selected = self.habits_tree.selection()
        if selected:
            habitLog_id = int(selected[0])
            habitLog = next(
                (habitLog for habit, habitLog in self.habit_log_list if habitLog.habitLog_id == habitLog_id),
                None
            )
            if habitLog:
                self.selected_habitLog = habitLog

    def refresh_dates(self) -> None:
        """Aktualizuje zakres dat na podstawie pól wejściowych."""
        try:
            self.from_date = datetime.strptime(self.from_date_var.get(), "%d.%m.%Y").date()
            self.to_date = datetime.strptime(self.to_date_var.get(), "%d.%m.%Y").date()
        except ValueError:
            messagebox.showerror("Błąd daty", "Nieprawidłowy format daty. Użyj DD.MM.YYYY.")

    def set_date_and_refresh(self) -> None:
        """Ustawia zakres dat i odświeża listę czynności."""
        self.refresh_dates()
        self.refresh_habits()

    def refresh_habits(self) -> None:
        """Odświeża listę czynności użytkownika."""
        self.refresh_dates()
        self.clean_and_create_treeview()

        engine = get_engine()
        from_date_for_query = datetime.combine(self.from_date, datetime.min.time())
        to_date_for_query = datetime.combine(self.to_date, datetime.max.time())
        with Session(engine) as session:
            self.habit_log_list = (
                session.query(Habit, HabitLog)
                .join(HabitLog)
                .filter(Habit.user_id == self.user.user_id)
                .filter(HabitLog.date >= from_date_for_query)
                .filter(HabitLog.date <= to_date_for_query)
                .all()
            )

        if not self.habit_log_list:
            ttk.Label(self.habits_frame, text="Brak czynności. Dodaj pierwszą czynność!").pack()
        else:
            for habit, habitLog in self.habit_log_list:
                values = (
                    habit.name,
                    habitLog.date.strftime("%d.%m.%Y") if isinstance(habitLog.date, (datetime, date)) else habitLog.date,
                    habit.description,
                    habitLog.description,
                    habitLog.duration,
                    habitLog.completed_at.strftime("%d.%m.%Y %H:%M") if habitLog.completed_at else None,
                    "✔️" if habitLog.completed_at else "❌"
                )
                self.habits_tree.insert("", tk.END, iid=habitLog.habitLog_id, values=values)

    def add_habit_for_day(self) -> None:
        """Otwiera okno dodawania czynności."""
        DailyHabitEditor(self.window, self.from_date, self.user.user_id, refresh_callback=self.refresh_habits)

    def edit_habit_for_day(self) -> None:
        """Otwiera okno edycji wybranej czynności."""
        if not self.habits_tree.selection():
            messagebox.showerror("Edytor czynności", "Brak wybranej czynności do edycji")
            return
        DailyHabitEditor(
            self.window,
            self.selected_habitLog.date,
            self.user.user_id,
            refresh_callback=self.refresh_habits,
            habitLog_to_edit=self.selected_habitLog
        )

    def delete_habit_for_day(self) -> None:
        """Usuwa wybraną czynność."""
        if not self.habits_tree.selection():
            messagebox.showerror("Usuwanie", "Brak wybranej czynności!")
            return
        habitLog = self.selected_habitLog
        engine = get_engine()
        with Session(engine) as session:
            session.delete(habitLog)
            session.commit()
        messagebox.showinfo("Usuwanie", "Czynność z danego dnia została pomyślnie usunięta")
        self.refresh_habits()

    def mark_habit_as_done(self) -> None:
        """Oznacza czynność jako wykonaną."""
        if not self.habits_tree.selection():
            messagebox.showerror("Wykonano", "Brak wybranej czynności!")
            return
        habitLog = self.selected_habitLog
        engine = get_engine()
        with Session(engine) as session:
            session.query(HabitLog).filter(HabitLog.habitLog_id == habitLog.habitLog_id).update(
                {HabitLog.completed_at: datetime.now().replace(microsecond=0)}
            )
            session.commit()
        self.refresh_habits()

    def mark_habit_as_undone(self) -> None:
        """Oznacza czynność jako niewykonaną."""
        if not self.habits_tree.selection():
            messagebox.showerror("Nie wykonano", "Brak wybranej czynności!")
            return
        habitLog = self.selected_habitLog
        engine = get_engine()
        with Session(engine) as session:
            session.query(HabitLog).filter(HabitLog.habitLog_id == habitLog.habitLog_id).update(
                {HabitLog.completed_at: None}
            )
            session.commit()
        self.refresh_habits()

    def manage_habits(self) -> None:
        """Otwiera menadżer czynności."""
        HabitsManager(self.window, user_id=self.user.user_id)

    def show_stats(self) -> None:
        """Otwiera widok statystyk."""
        StatisticsView(self.window, self.user.user_id, self.from_date, self.to_date)

    def export_pdf(self) -> None:
        """Eksportuje statystyki i logi do plików PDF."""
        try:
            exporter = PDFExporter(self.user)
            stats_path = exporter.export_stats_to_pdf()
            logs_path = exporter.export_habits_logs_to_pdf()
            messagebox.showinfo(
                "Eksport PDF",
                f"Pliki PDF zostały zapisane w:\n1. {stats_path}\n2. {logs_path}"
            )
        except Exception as e:
            messagebox.showerror("Eksport PDF", f"Wystąpił błąd podczas eksportu danych do pliku PDF:\n{e}")

    def logout(self) -> None:
        """Wylogowuje użytkownika i zamyka okno."""
        self.log_out = True
        self.window.destroy()
        # Powrót do ekranu logowania
