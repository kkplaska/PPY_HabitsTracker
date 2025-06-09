"""
gui/daily_habit_editor.py

Moduł ekranu edycji nawyku dla danego dnia w aplikacji Habit Tracker.
Zawiera klasę DailyHabitEditor odpowiedzialną za edycję wpisu.
"""

import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
from tkcalendar import DateEntry
from datetime import datetime
from typing import Optional, Callable

from sqlalchemy.orm import Session

from db.session import get_engine
from db.models import HabitLog, Habit
from logic.habit_service import get_habits_by_user_id


class DailyHabitEditor(tk.Toplevel):
    """
    Okno do dodawania lub edycji dziennego wpisu nawyku (HabitLog).
    """

    def __init__(
        self,
        parent: tk.Widget,
        date: datetime.date,
        user_id: int,
        refresh_callback: Optional[Callable[[], None]] = None,
        habit_log_to_edit: Optional[HabitLog] = None,
    ) -> None:
        """
        Inicjalizuje GUI, pobiera listę nawyków i ewentualnie wypełnia pola
        jeśli edytujemy istniejący wpis.

        :param parent: rodzicielski widget (zwykle główne okno)
        :param date: data wpisu (datetime)
        :param user_id: ID zalogowanego użytkownika
        :param refresh_callback: funkcja odświeżająca listę w MainScreen
        :param habit_log_to_edit: obiekt HabitLog do edycji (opcjonalnie)
        """
        super().__init__(parent)
        self.user_id = user_id
        self.date = date
        self.refresh_callback = refresh_callback
        self.habit_log_to_edit = habit_log_to_edit
        self.habits = get_habits_by_user_id(self.user_id)

        self.title("Daily Habit Editor")
        self.geometry("300x250")

        self._create_widgets()
        if self.habit_log_to_edit:
            self.fill_fields()

    def _create_widgets(self) -> None:
        """
        Tworzy i rozmieszcza wszystkie kontrolki GUI.
        """
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Czynność
        ttk.Label(frame, text="Czynność:").grid(row=0, column=0, sticky="e", pady=5)
        self.habit_var = tk.StringVar()
        names = [f"{h.name}: {h.description}" for h in self.habits]
        default = names[0] if names else ""
        ttk.OptionMenu(frame, self.habit_var, default, *names).grid(
            row=0, column=1, sticky="w", pady=5
        )

        # Szczegóły
        ttk.Label(frame, text="Szczegóły:").grid(row=1, column=0, sticky="e", pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.description_var, width=28).grid(
            row=1, column=1, sticky="w", pady=5
        )

        # Czas trwania
        ttk.Label(frame, text="Czas trwania (h):").grid(
            row=2, column=0, sticky="e", pady=5
        )
        self.duration_var = tk.StringVar()
        vcmd = (self.register(self._validate_float), "%P")
        ttk.Entry(
            frame,
            textvariable=self.duration_var,
            width=10,
            validate="key",
            validatecommand=vcmd,
        ).grid(row=2, column=1, sticky="w", pady=5)

        # Data
        ttk.Label(frame, text="Data:").grid(row=3, column=0, sticky="e", pady=5)
        self.date_var = tk.StringVar(value=self.date.strftime("%Y-%m-%d"))
        DateEntry(
            frame,
            textvariable=self.date_var,
            date_pattern="yyyy-mm-dd",
            width=12,
        ).grid(row=3, column=1, sticky="w", pady=5)

        # Ukończono
        ttk.Label(frame, text="Zakończono dnia:").grid(
            row=4, column=0, sticky="e", pady=5
        )
        self.completed_at_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.completed_at_var, width=24).grid(
            row=4, column=1, sticky="w", pady=5
        )

        # Przycisk Zapisz + Enter
        ttk.Button(frame, text="Zapisz", command=self.save_habit_log).grid(
            row=5, column=0, columnspan=2, pady=15
        )
        self.bind("<Return>", lambda event: self.save_habit_log())

    @staticmethod
    def _validate_float(value: str) -> bool:
        """
        Waliduje, czy wpisany ciąg można skonwertować na float.
        :param value: wprowadzony tekst
        :return: True jeśli puste lub prawidłowy float, False w przeciwnym razie
        """
        if not value:
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def _parse_datetime(text: str) -> Optional[datetime]:
        """
        Parsuje datę z formatu 'YYYY-MM-DD HH:MM[:SS]'.
        :param text: tekst daty
        :return: obiekt datetime lub None jeśli puste; wyświetla błąd w GUI
        """
        if not text or text.lower() == "none":
            return None
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

        messagebox.showerror(
            "Błąd", "Nieprawidłowy format daty. Użyj: YYYY-MM-DD HH:MM"
        )
        return None

    def fill_fields(self) -> None:
        """
        Wypełnia pola danymi z istniejącego HabitLog (edycja).
        """
        log = self.habit_log_to_edit
        habit = next((h for h in self.habits if h.habit_id == log.habit_id), None)
        if not habit:
            return

        self.habit_var.set(f"{habit.name}: {habit.description}")
        self.date_var.set(log.date.strftime("%Y-%m-%d"))
        self.description_var.set(log.description or "")
        self.duration_var.set(str(log.duration or ""))
        self.completed_at_var.set(
            log.completed_at.strftime("%Y-%m-%d %H:%M")
            if log.completed_at
            else ""
        )

    def save_habit_log(self) -> None:
        """
        Zapisuje nowy lub aktualizuje istniejący wpis HabitLog w bazie.
        """
        name = self.habit_var.get().strip()
        if not name:
            messagebox.showwarning("Błąd", "Musisz wybrać czynność.")
            return

        habit = next(
            (h for h in self.habits if f"{h.name}: {h.description}" == name), None
        )
        if not habit:
            messagebox.showerror("Błąd", "Wybrana czynność nie istnieje.")
            return

        # Parsowanie pól
        desc = self.description_var.get().strip()
        dur = float(self.duration_var.get()) if self.duration_var.get() else 0.0
        date_entry = datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        completed = self._parse_datetime(self.completed_at_var.get())

        try:
            with Session(bind=get_engine()) as session:
                if self.habit_log_to_edit:
                    # Update
                    session.query(HabitLog).filter(
                        HabitLog.habitLog_id == self.habit_log_to_edit.habitLog_id
                    ).update(
                        {
                            HabitLog.habit_id: habit.habit_id,
                            HabitLog.description: desc,
                            HabitLog.duration: dur,
                            HabitLog.date: date_entry,
                            HabitLog.completed_at: completed,
                        }
                    )
                    message = "Dzienny wpis zaktualizowany."
                else:
                    # Insert
                    new_log = HabitLog(
                        habit_id=habit.habit_id,
                        description=desc,
                        duration=dur,
                        date=date_entry,
                        completed_at=completed,
                    )
                    session.add(new_log)
                    message = "Dzienny wpis zapisany."

                session.commit()
                messagebox.showinfo("Sukces", message)

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać wpisu:\n{e}")
            return

        if self.refresh_callback:
            self.refresh_callback()
        self.destroy()
