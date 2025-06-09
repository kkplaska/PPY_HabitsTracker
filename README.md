# PPY
# Habits Tracker
Aplikacja desktopowa do śledzenia nawyków z graficznym interfejsem użytkownika (Tkinter), bazą danych (SQLite + SQLAlchemy) oraz szyfrowaniem haseł.

Użytkownik tworzy konto, loguje się, definiuje własne nawyki (np. „ćwiczenia”, „czytanie”, „medytacja”, „piłem wodę”) i codziennie zaznacza, które udało mu się zrealizować. Aplikacja pokazuje statystyki i pozwala na eksport danych do PDF.

## Główne funkcje:
- Rejestracja i logowanie użytkowników  
- Definiowanie własnych nawyków (np. „ćwiczenia”, „czytanie”, „medytacja”)  
- Codzienne zaznaczanie wykonania nawyków
- Generowanie statystyk dotyczących wykonywania nawyków  
- Eksport dziennika i statystyk nawyków do plików PDF

## Główne komponenty projektu:
1. GUI (interfejs graficzny) – tkinter
- daily_habit_editor.py – dodawanie i edytowanie nawyków dla konkretnego dnia
- habit_editor.py – dodawanie i edytowanie nawyków
- habits_manager.py – zarządzanie wszystkimi nawykami użytkownika
- login_screen.py – ekran logowania i rejestracji
- main_screen.py – główny widok użytkownika z listą nawyków i możliwością zarządzania nawykami dla konkretnych dni
- register_screen.py - ekran rejestracji użytkownika
- statistics_view.py – statystyki realizacji nawyków

2. Baza danych – SQLAlchemy ORM + SQLite
- User – dane użytkownika (login, zaszyfrowane hasło)
- Habit – zdefiniowane nawyki użytkownika
- HabitLog – zapisy codziennej realizacji nawyków
- relacje User <-> Habit i Habit <-> HabitLog

3. Logika aplikacji
- Rejestracja, logowanie, weryfikacja danych użytkownika
- Dodawanie/usuwanie/edycja nawyków
- Dodawanie/usuwanie/edycja nawyków dla konkretnych dni
- Generowanie statystyk

4. Szyfrowanie danych – bcrypt
- Szyfrowanie i odszyfrowywanie haseł użytkowników

5. Eksport danych – fpdf
- Eksport statystyk nawyków do pliku PDF
- Możliwość eksportu dziennika nawyków do pliku PDF

## Struktura plików
````
PPY_HabitsTracker/
├── main.py
├── db/
│   ├── models.py
│   ├── session.py
├── docs/ # folder z dokumentacją 
├── exports/ # folder z eksportowanymi plikami użytkowników 
├── gui/
│   ├── daily_habit_editor.py
│   ├── habit_editor.py
│   ├── habits_manager.py
│   ├── login_screen.py
│   ├── main_screen.py
│   ├── register_screen.py
│   ├── statistics_view.py
├── logic/
│   ├── auth.py
│   ├── habit_service.py
├── utils/
│   ├── encryption.py
│   ├── export_pdf.py
│   ├── statistics.py
├── habit_tracker.db
├── requirements.txt
├── README.md
├── .gitignore
````
## Wymagania
- Python 3.8+
- Biblioteki zdefiniowane w pliku `requirements.txt`
  - sqlalchemy
  - tkcalendar
  - matplotlib
  - fpdf
  - bcrypt

## Uruchomienie
W głównym katalogu projektu uruchom:
```bash
pip install -r requirements.txt
python main.py
```
Program uruchomi ekran logowania/rejestracji. Po zalogowaniu zobaczysz główne okno aplikacji, z którego możesz:
- Dodawać/usunąć/edytować nawyki
- Zaznaczać wykonanie nawyków dla wybranej daty
- Przeglądać statystyki globalne i dla pojedynczych nawyków
- Eksportować dane do pliku PDF

## Licencja
Projekt udostępniony na licencji MIT.