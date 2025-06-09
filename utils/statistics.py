"""
utils/statistics.py

Moduł statystyk nawyków.

Zawiera:
    - calculate_max_streak: funkcję obliczającą najdłuższą serię dni, w których nawyk był wykonany,
    - load_habits: metodę do załadowania nawyków użytkownika do widżetu Combobox.
"""

from typing import Sequence
from db.models import HabitLog


def calculate_max_streak(logs: Sequence[HabitLog]) -> int:
    """
    Oblicza najdłuższą serię kolejnych dni, w których nawyk został wykonany.

    :param logs: sekwencja obiektów HabitLog zawierających pola .date oraz .completed_at
    :return: długość najdłuższej serii dni z rzędu, gdy .completed_at nie jest None
    """
    # Wyciągamy i sortujemy daty zakończonych wpisów
    dates = sorted(log.date for log in logs if log.completed_at)
    if not dates:
        return 0

    max_streak = 1
    current_streak = 1

    # Iterujemy po kolejnych datach, porównując różnicę dni
    for prev, curr in zip(dates, dates[1:]):
        if (curr - prev).days == 1:
            current_streak += 1
        else:
            max_streak = max(max_streak, current_streak)
            current_streak = 1

    return max(max_streak, current_streak)
