# PPY
# Habits Tracker
Aplikacja do śledzenia nawyków z GUI, bazą danych i szyfrowaniem haseł.

Użytkownik tworzy konto, loguje się, definiuje własne nawyki (np. „ćwiczenia”, „czytanie”, „medytacja”) i codziennie zaznacza, które udało mu się zrealizować. Aplikacja pokazuje statystyki i pozwala na eksport danych do PDF.

Użytkownik może tworzyć i zaznaczać wykonane nawyki (np. „piłem wodę”, „ćwiczyłem”). Użytkownik tworzy konto, loguje się, definiuje własne nawyki (np. „ćwiczenia”, „czytanie”, „medytacja”) i codziennie zaznacza, które udało mu się zrealizować. Aplikacja pokazuje statystyki i pozwala na eksport danych do PDF. Funkcje:
GUI
Rejestracja/logowanie
Baza danych użytkowników + nawyków
Statystyki tygodniowe
Eksport PDF

Główne komponenty projektu:
1. GUI (interfejs graficzny) – tkinter
login_screen – ekran logowania i rejestracji
- dashboard – główny widok użytkownika z listą nawyków
- habit_editor – dodawanie i edytowanie nawyków
- statistics_view – statystyki realizacji nawyków
- menu – menu główne (wyloguj, eksport, ustawienia itd.)

2. Baza danych – SQLAlchemy ORM + SQLite
- User – dane użytkownika (login, zaszyfrowane hasło)
- Habit – zdefiniowane nawyki użytkownika
- HabitLog – zapisy codziennej realizacji nawyków
- relacje User <-> Habit i Habit <-> HabitLog

3. Logika aplikacji
- auth.py – rejestracja, logowanie, weryfikacja danych użytkownika
- habit_manager.py – dodawanie/usuwanie/edycja nawyków
- tracker.py – oznaczanie wykonanych nawyków, logowanie dat
- stats.py – obliczanie statystyk (np. dni z rzędu)

4. Szyfrowanie danych – cryptography
- Generowanie i zarządzanie kluczem szyfrującym
- Szyfrowanie i odszyfrowywanie haseł użytkowników

5. Eksport danych – fpdf
- Eksport wyników/statystyk do pliku PDF
- Możliwość eksportu dziennika nawyków

6. Ustawienia i konfiguracja
- Przechowywanie ustawień GUI (np. motyw, język)
- Możliwość zmiany hasła użytkownika
- Wybór zakresu dat do eksportu PDF

## Struktura plików (propozycja)
````
habit_tracker/
├── main.py
├── gui/
│   ├── login_screen.py
│   ├── dashboard.py
│   ├── habit_editor.py
│   ├── statistics_view.py
├── db/
│   ├── models.py
│   ├── session.py
├── logic/
│   ├── auth.py
│   ├── habit_manager.py
│   ├── tracker.py
│   ├── stats.py
├── utils/
│   ├── encryption.py
│   ├── pdf_export.py
├── requirements.txt
├── README.md
````



## Uruchomienie
```bash
pip install -r requirements.txt
python main.py
```