import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from sqlalchemy.orm import Session
from db.session import get_engine
from logic.auth import register


def attempt_register(username, password, re_password, window):
    if not username or not password:
        messagebox.showerror("Błąd", "Wszystkie pola są wymagane.")
        return
    if password != re_password:
        messagebox.showerror("Błąd", "Hasła nie są identyczne.")
        return
    engine = get_engine()
    with Session(engine) as session:
        try:
            register(session, username, password)
            messagebox.showinfo("Sukces", "Rejestracja zakończona sukcesem!")
            window.destroy()  # Zamyka okno rejestracji
        except ValueError as e:
            messagebox.showerror("Błąd", str(e))


class RegisterScreen:
    def __init__(self):
        window = tk.Tk()
        window.title("Habit Tracker - Rejestracja")
        window.geometry("400x350")

        ttk.Label(window, text="Nazwa użytkownika:").pack(pady=(30, 5))
        user_entry = ttk.Entry(window)
        user_entry.pack(pady=5)

        ttk.Label(window, text="Hasło:").pack(pady=5)
        password_entry = ttk.Entry(window, show="*")
        password_entry.pack(pady=5)

        ttk.Label(window, text="Powtórz hasło:").pack(pady=5)
        re_password_entry = ttk.Entry(window, show="*")
        re_password_entry.pack(pady=5)

        ttk.Button(
            window,
            text="Zarejestruj",
            command=lambda: attempt_register(
                user_entry.get(), password_entry.get(), re_password_entry.get(), window
            )
        ).pack(pady=20)

        window.mainloop()

