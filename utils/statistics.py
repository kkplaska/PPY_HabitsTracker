from sqlalchemy.orm import Session
from db.session import get_engine
from logic.habit_manager import get_habits_by_user_id

def calculate_max_streak(logs):
    """Calculate the longest streak of consecutive completed days."""
    dates = sorted([log.date for log in logs if log.completed_at])
    if not dates:
        return 0
    max_streak = 1
    current_streak = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            current_streak += 1
        else:
            max_streak = max(max_streak, current_streak)
            current_streak = 1
    return max(max_streak, current_streak)

def load_habits(self, user_id):
    engine = get_engine()
    with Session(engine) as session:
        habits = get_habits_by_user_id(user_id)
        self.habits = {f"{habit.name}: {habit.description}": habit for habit in habits}
    self.habit_combo['values'] = list(self.habits.keys())
    if self.habits:
        self.habit_combo.current(0)