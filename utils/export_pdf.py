"""
utils/export_pdf.py

Moduł odpowiedzialny za eksport statystyk i dzienników nawyków użytkownika do plików PDF.
"""

import os
from datetime import datetime
from typing import List

from fpdf import FPDF
from sqlalchemy.orm import Session

from db.models import Habit, HabitLog, User
from db.session import get_engine
from logic.habit_service import (
    get_habits_by_user_id,
    get_habit_logs_by_user_id
)
from utils.statistics import calculate_max_streak


class PDFExporter:
    """
    Klasa odpowiadająca za generowanie raportów PDF:
    - statystyk globalnych i per-nawykowych,
    - dziennika wszystkich nawyków użytkownika.
    """

    def __init__(self, user: User) -> None:
        """
        Inicjalizuje eksportera PDF.

        :param user: obiekt użytkownika, dla którego mają zostać wygenerowane raporty
        """
        self.user = user
        # Ścieżka do czcionki DejaVuSans.ttf obok tego pliku
        self.font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")

    def export_stats_to_pdf(self) -> str:
        """
        Eksportuje statystyki nawyków użytkownika do pliku PDF.

        :return: Zwraca bezwzględną ścieżkę do wygenerowanego pliku.
        """
        # Przygotowanie ścieżki i pobranie danych
        exports_dir = "exports"
        os.makedirs(exports_dir, exist_ok=True)
        filename = os.path.join(
            exports_dir,
            f"{datetime.today():%Y-%m-%d}_{self.user.username}_habits_stats.pdf",
        )
        habits = get_habits_by_user_id(self.user.user_id)
        habit_logs = get_habit_logs_by_user_id(self.user.user_id)

        # Obliczenia globalne
        created_dates = [h.created_at for h in habits if h.created_at]
        total_logs = len(habit_logs)
        completed = sum(1 for h in habit_logs if h.completed_at)
        uncompleted = total_logs - completed
        global_streak = calculate_max_streak(habit_logs)

        # Statystyki per-nawykowe
        habits_stats: List[dict] = []
        for habit in habits:
            logs = [h for h in habit_logs if h.habit_id == habit.habit_id]
            stats = {
                "id": habit.habit_id,
                "name": habit.name,
                "description": habit.description,
                "total": len(logs),
                "completed": sum(1 for l in logs if l.completed_at),
                "uncompleted": len(logs) - sum(1 for l in logs if l.completed_at),
                "streak": calculate_max_streak(logs),
            }
            habits_stats.append(stats)

        # Inicjalizacja PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("DejaVu", "", self.font_path, uni=True)

        # Nagłówek raportu
        first_date = min(created_dates).strftime("%Y-%m-%d") if created_dates else "-"
        last_date = max(created_dates).strftime("%Y-%m-%d") if created_dates else "-"
        pdf.set_font("DejaVu", "", 14)
        pdf.cell(0, 10, f"Statystyki Nawyków - {self.user.username}", ln=True, align="C")
        pdf.set_font("DejaVu", "", 11)
        pdf.cell(0, 8, f"Okres: {first_date} – {last_date}", ln=True, align="C")
        pdf.cell(0, 8, f"Wygenerowano: {datetime.today():%Y-%m-%d}", ln=True, align="C")
        pdf.ln(4)

        # --- Statystyki globalne ---
        pdf.set_font("DejaVu", "", 12)
        pdf.cell(0, 8, "=== Statystyki globalne ===", ln=True)
        pdf.set_font("DejaVu", "", 11)
        pdf.cell(0, 6, f"Liczba wpisów: {total_logs}", ln=True)
        pdf.cell(0, 6, f"Wykonano: {completed}", ln=True)
        pdf.cell(0, 6, f"Nie wykonano: {uncompleted}", ln=True)
        pdf.cell(0, 6, f"Najdłuższa seria: {global_streak}", ln=True)
        pdf.ln(4)

        # --- Statystyki pojedynczych nawyków ---
        pdf.set_font("DejaVu", "", 12)
        pdf.cell(0, 8, "=== Statystyki pojedynczych nawyków ===", ln=True)
        pdf.set_font("DejaVu", "", 11)
        if not habits_stats:
            pdf.cell(0, 6, "Brak nawyków w wybranym okresie.", ln=True)
        else:
            for idx, stat in enumerate(habits_stats, start=1):
                pdf.cell(0, 5, f"{idx}. Nawyk: {stat['name']}", ln=True)
                pdf.cell(0, 5, f"   Opis: {stat['description']}", ln=True)
                pdf.cell(0, 5, f"   Liczba wpisów: {stat['total']}", ln=True)
                pdf.cell(0, 5, f"   Wykonano: {stat['completed']}", ln=True)
                pdf.cell(0, 5, f"   Nie wykonano: {stat['uncompleted']}", ln=True)
                pdf.cell(0, 5, f"   Najdłuższa seria: {stat['streak']}", ln=True)
                pdf.ln(2)
                self._add_logs_table(pdf, [h for h in habit_logs if h.habit_id == stat["id"]])
                pdf.ln(4)

        pdf.output(filename)
        return os.path.abspath(filename)

    @staticmethod
    def _add_logs_table(pdf: FPDF, logs: List[HabitLog]) -> None:
        """
        Dodaje tabelę logów dla pojedynczego nawyku w PDF.

        :param pdf: obiekt FPDF do rysowania
        :param logs: lista obiektów HabitLog do wyświetlenia
        """
        # Nagłówek tabeli
        pdf.set_font("DejaVu", "", 11)
        pdf.cell(30, 6, "Data", border=1, align="C")
        pdf.cell(90, 6, "Szczegóły", border=1, align="C")
        pdf.cell(45, 6, "Data wykonania", border=1, align="C")
        pdf.cell(25, 6, "Wykonano", border=1, align="C")
        pdf.ln()

        # Wiersze
        if not logs:
            pdf.cell(190, 6, "Brak wpisów dla tego nawyku.", border=1, align="C")
            pdf.ln()
            return

        for log in logs:
            date_str = log.date.strftime("%Y-%m-%d") if log.date else ""
            completed_str = log.completed_at.strftime("%Y-%m-%d %H:%M") if log.completed_at else ""
            done = "TAK" if log.completed_at else "NIE"
            pdf.cell(30, 6, date_str, border=1)
            pdf.cell(90, 6, log.description or "", border=1)
            pdf.cell(45, 6, completed_str, border=1)
            pdf.cell(25, 6, done, border=1, align="C")
            pdf.ln()

    def export_habits_logs_to_pdf(self) -> str:
        """
        Eksportuje dziennik wszystkich nawyków użytkownika do pliku PDF.

        :return: Zwraca bezwzględną ścieżkę do wygenerowanego pliku.
        """
        exports_dir = "exports"
        os.makedirs(exports_dir, exist_ok=True)
        filename = os.path.join(
            exports_dir,
            f"{datetime.today():%Y-%m-%d}_{self.user.username}_habits_logs.pdf",
        )

        engine = get_engine()
        with Session(engine) as session:
            habits = (
                session.query(Habit)
                .filter_by(user_id=self.user.user_id)
                .order_by(Habit.created_at.desc())
                .all()
            )

        pdf = FPDF("P", "mm", "A4")
        pdf.add_page()
        pdf.set_display_mode("default")
        pdf.add_font("DejaVu", "", self.font_path, uni=True)
        pdf.set_font("DejaVu", "", 12)

        pdf.cell(0, 10, f"Dziennik Nawyków - {self.user.username}", ln=True, align="C")
        pdf.ln(4)

        if not habits:
            pdf.cell(0, 8, "Brak zapisanych nawyków.", ln=True)
        else:
            for habit in habits:
                name = habit.name or "Brak nazwy"
                desc = habit.description or "Brak opisu"
                created = habit.created_at.strftime("%Y-%m-%d %H:%M") if habit.created_at else "-"
                text = f"=== Nawyk: {name} ===\nOpis: {desc}\nDodano: {created}"
                pdf.multi_cell(0, 8, text)
                pdf.ln(2)

        pdf.output(filename)
        return os.path.abspath(filename)
