from fpdf import FPDF
from datetime import datetime
from logic.habit_manager import *
import os

from utils.statistics import calculate_max_streak

class PDFExporter:
    def __init__(self, user):
        self.user = user
        self.font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")

    def export_stats_to_pdf(self):
        filename = f"exports/{datetime.today().strftime('%Y-%m-%d')}_{self.user.username}_habits_statistics.pdf"
        habits = get_habits_by_user_id(self.user.user_id)
        habit_logs = get_habits_logs_by_user_id(self.user.user_id)
        created_dates = [h.created_at for h in habits if h.created_at]
        total_habits_log = len(habit_logs)
        completed = sum([1 for h in habit_logs if h.completed_at])
        uncompleted = sum([1 for h in habit_logs if not h.completed_at])
        global_streak = calculate_max_streak(habit_logs)

        habits_stats = []
        for habit in habits:
            specifics_habit_logs = [h for h in habit_logs if h.habit_id == habit.habit_id]
            h_total = len(specifics_habit_logs)
            h_completed = sum(1 for log in specifics_habit_logs if log.completed_at)
            h_uncompleted = h_total - h_completed
            h_streak = calculate_max_streak(specifics_habit_logs)
            habits_stats.append({
                "id": habit.habit_id,
                "name": habit.name,
                "description": habit.description,
                "total": h_total,
                "completed": h_completed,
                "uncompleted": h_uncompleted,
                "streak": h_streak,
            })

        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("DejaVu", "", self.font_path, uni=True)

        first_date = min(created_dates).strftime("%Y-%m-%d")
        last_date = max(created_dates).strftime("%Y-%m-%d")

        pdf.set_font("DejaVu", "", 14)
        pdf.cell(200, 10, f"Statystyki Nawyków użytkownika {self.user.username}", ln=True, align="C")
        pdf.set_font("DejaVu", "", 11)
        pdf.cell(200, 10, f"w okresie {first_date} - {last_date}", ln=True, align="C")
        pdf.cell(200, 10, f"wygenerowane {datetime.today().strftime('%Y-%m-%d')}", ln=True, align="C")
        pdf.ln(2)

        # --- Global statistics ---
        pdf.cell(0,8,"==========================================================", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.cell(0, 10, "Statystyki globalne (wszystkie nawyki)", ln=True)
        pdf.set_font("DejaVu", "", 11)
        pdf.cell(0, 8, f"Liczba wpisów: {total_habits_log}", ln=True)
        pdf.cell(0, 8, f"Wykonano: {completed}", ln=True)
        pdf.cell(0, 8, f"Nie wykonano: {uncompleted}", ln=True)
        pdf.cell(0, 8, f"Najdłuższa seria (dowolny nawyk): {global_streak}", ln=True)
        pdf.ln(2)

        # --- Per-habit statistics ---
        pdf.cell(0,8,"==========================================================", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.cell(0, 10, "Statystyki pojedynczych nawyków", ln=True)
        pdf.set_font("DejaVu", "", 11)
        if not habits_stats:
            pdf.cell(0, 8, "Brak nawyków w wybranym okresie.", ln=True)
        else:
            order = 1
            for stat in habits_stats:
                pdf.cell(0,8,"----------------------------------------------------------", ln=True)
                pdf.set_font("DejaVu", "", 11)
                pdf.cell(0, 8, f"{order}.Nawyk: {stat['name']}", ln=True)
                order += 1
                pdf.cell(0, 8, f"Opis: {stat['description']}", ln=True)
                pdf.cell(0, 8, f"Liczba wpisów: {stat['total']}", ln=True)
                pdf.cell(0, 8, f"Wykonano: {stat['completed']}", ln=True)
                pdf.cell(0, 8, f"Nie wykonano: {stat['uncompleted']}", ln=True)
                pdf.cell(0, 8, f"Najdłuższa seria: {stat['streak']}", ln=True)
                pdf.ln(4)
                self.get_pdf_table(pdf, [h for h in habit_logs if h.habit_id == stat['id']])

        pdf.output(filename)
        return os.path.abspath(filename)

    @staticmethod
    def get_pdf_table(pdf, habit_logs: list[HabitLog]):
        pdf.set_font("DejaVu", "", 11)
        pdf.cell(30, 8, "Data", border=1, align="C")
        pdf.cell(90, 8, "Szczegóły", border=1, align="C")
        pdf.cell(45, 8, "Data wykonania", border=1, align="C")
        pdf.cell(25, 8, "Wykonano", border=1, align="C")
        pdf.ln()

        pdf.set_font("DejaVu", "", 11)
        if not habit_logs:
            pdf.cell(190, 8, "Brak wpisów dla tego nawyku.", border=1, align="C")
            pdf.ln()
        else:
            for log in habit_logs:
                date_str = log.date.strftime("%Y-%m-%d") if log.date else ""
                details = log.description
                completed_date = log.completed_at.strftime("%Y-%m-%d %H:%M") if log.completed_at else ""
                done = "TAK" if log.completed_at else "NIE"
                pdf.cell(30, 8, date_str, border=1)
                pdf.cell(90, 8, details, border=1)
                pdf.cell(45, 8, completed_date, border=1)
                pdf.cell(25, 8, done, border=1, align="C")
                pdf.ln()

    def export_habits_logs_to_pdf(self):
        filename = f"exports/{datetime.today().strftime('%Y-%m-%d')}_{self.user.username}_habits_logs.pdf"
        engine = get_engine()
        with Session(engine) as session:
            habits = session.query(Habit).filter_by(user_id=self.user.user_id).order_by(Habit.created_at.desc()).all()

            pdf = FPDF('P', 'mm', 'A4')
            pdf.add_page()
            pdf.set_display_mode("default")
            pdf.add_font("DejaVu", "", self.font_path, uni=True)
            pdf.set_font("DejaVu", "", 12)

            pdf.cell(200, 10, f"Dziennik Nawyków użytkownika {self.user.username}", ln=True, align="C")
            pdf.ln(10)

            if not habits:
                pdf.cell(200, 10, "Brak zapisanych nawyków.", ln=True)
            else:
                for habit in habits:
                    name = habit.name or "Brak nazwy"
                    desc = habit.description or "Brak opisu"
                    created = habit.created_at.strftime("%Y-%m-%d %H:%M") if habit.created_at else "Brak daty"

                    pdf.multi_cell(0, 10, f"Nawyk: {name}\nOpis: {desc}\nDodano: {created}\n---")
                    pdf.ln(2)

            pdf.output(filename)
            return os.path.abspath(filename)
