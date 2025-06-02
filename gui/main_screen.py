import datetime
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from sqlalchemy.orm import Session

from db.models import HabitLog, Habit
from db.session import get_engine
from gui.daily_habit_editor import DailyHabitEditor
from gui.habits_manager import HabitsManager


class MainScreen:
    def __init__(self, user):
        self.user = user
        self.date = datetime.date.today()
        self.date_var = None
        self.log_out = False
        self.window = tk.Tk()
        self.window.title(f"Habit Tracker - {self.user.username}")
        self.window.geometry("1200x400")
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.grid(column=0, row=0, padx=10, pady=10, sticky=tk.NSEW)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=8)

        self.habits_frame = ttk.Frame(self.main_frame)
        self.habit_log_list = None
        self.selected_habitLog = None

        self.create_widgets()
        self.window.mainloop()

    def create_widgets(self):
        # Góra
        top_frame = ttk.Frame(self.main_frame)
        top_frame.grid(column=0, row=0, sticky=tk.NSEW)
        # topFrame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NW)
        ttk.Label(top_frame, text=f"Witaj, {self.user.username}!", font=("Arial", 16)).pack(side=tk.LEFT)

        # Wybór daty - prawy górny róg
        date_frame = ttk.Frame(self.main_frame)
        date_frame.grid(column=1, row=0, sticky=tk.E)
        ttk.Label(date_frame, text="Wskaż datę: ", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.date_var = tk.StringVar()
        DateEntry(date_frame, text=f"{self.date}", date_pattern="dd.mm.yyyy", textvariable=self.date_var).grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        # Przycisk do odświeżania listy czynności po zmianie daty
        ttk.Button(date_frame, text="Odśwież", command=self.set_date_and_refresh).grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)


        # Lista czynności - środek
        # Tabela
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
        bottom_button_frame.grid(column=0, row=2, columnspan=2, sticky=tk.S)

        ttk.Button(bottom_button_frame, text="Menadżer czynności", command=self.manage_habits).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="Statystyki", command=self.show_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="Eksport do PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="Wyloguj", command=self.logout).pack(side=tk.LEFT, padx=5)

    def clean_and_create_treeview(self):
        # Wyczyść poprzednią listę
        for widget in self.habits_frame.winfo_children():
            widget.destroy()

        # Utwórz nowy Treeview
        self.habits_tree = ttk.Treeview(self.habits_frame,
                                        columns=("name", "description", "details", "duration", "completed_at", "is_completed"),
                                        show="headings")
        self.habits_tree.heading("name", text="Nazwa")
        self.habits_tree.heading("description", text="Opis")
        self.habits_tree.heading("details", text="Szczegóły")
        self.habits_tree.heading("duration", text="Czas trwania [min]")
        self.habits_tree.heading("completed_at", text="Ukończono")
        self.habits_tree.heading("is_completed", text="Wykonano")
        self.habits_tree.pack(fill=tk.BOTH, expand=True)
        self.habits_frame.grid(column=0, row=1, sticky=tk.NSEW)
        self.habits_tree.bind("<<TreeviewSelect>>", self.on_row_selected)

    def on_row_selected(self, event):
        selected = self.habits_tree.selection()
        if selected:
            habitLog_id = int(selected[0])
            habitLog = next((habitLog for habit, habitLog in self.habit_log_list if habitLog.habitLog_id == habitLog_id), None)
            if habitLog:
                self.selected_habitLog = habitLog

    def set_date_and_refresh(self):
        self.date = datetime.datetime.strptime(self.date_var.get(), "%d.%m.%Y")
        self.refresh_habits()


    def refresh_habits(self):
        self.clean_and_create_treeview()

        # Pobierz czynności użytkownika z bazy
        engine = get_engine()
        date_for_query = datetime.datetime.fromisoformat(self.date.isoformat())
        with Session(engine) as session:
            self.habit_log_list = session.query(Habit, HabitLog).join(HabitLog).filter(Habit.user_id == self.user.user_id).filter(HabitLog.date == date_for_query).all()

        if not self.habit_log_list:
            ttk.Label(self.habits_frame, text="Brak czynności. Dodaj pierwszą czynność!").pack()
        else:
            for habit, habitLog in self.habit_log_list:
                if habitLog.completed_at is None:
                    self.habits_tree.insert("", tk.END, iid=habitLog.habitLog_id, values=(
                        habit.name, habit.description, habitLog.description, habitLog.duration, None, "❌"
                    ))
                else:
                    self.habits_tree.insert("", tk.END, iid=habitLog.habitLog_id, values=(
                        habit.name, habit.description, habitLog.description, habitLog.duration, habitLog.completed_at, "✔️"
                    ))

    def add_habit_for_day(self):
        DailyHabitEditor(self.window, self.date, self.user.user_id, refresh_callback=self.refresh_habits)

    def edit_habit_for_day(self):
        DailyHabitEditor(self.window, self.date, self.user.user_id, refresh_callback=self.refresh_habits, habitLog_to_edit=self.selected_habitLog)

    def delete_habit_for_day(self):
        habitLog = self.selected_habitLog
        engine = get_engine()
        with Session(engine) as session:
            session.delete(habitLog)
            session.commit()
        messagebox.showinfo("Usuwanie", "Czynność z danego dnia została pomyślnie usunięta")
        self.refresh_habits()

    def mark_habit_as_done(self):
        habitLog = self.selected_habitLog
        engine = get_engine()
        with Session(engine) as session:
            session.query(HabitLog).filter(HabitLog.habitLog_id == habitLog.habitLog_id).update({HabitLog.completed_at: datetime.datetime.now().replace(microsecond=0)})
            session.commit()
        self.refresh_habits()

    def mark_habit_as_undone(self):
        habitLog = self.selected_habitLog
        engine = get_engine()
        with Session(engine) as session:
            session.query(HabitLog).filter(HabitLog.habitLog_id == habitLog.habitLog_id).update({HabitLog.completed_at: None})
            session.commit()
        self.refresh_habits()

    def manage_habits(self):
        HabitsManager(self.window, user_id=self.user.user_id)

    def show_stats(self):
        messagebox.showinfo("Statystyki", "Funkcja statystyk (do zaimplementowania)")

    def export_pdf(self):
        messagebox.showinfo("Eksport", "Funkcja eksportu do PDF (do zaimplementowania)")

    def logout(self):
        self.log_out = True
        self.window.destroy()
        # Powrót do ekranu logowania