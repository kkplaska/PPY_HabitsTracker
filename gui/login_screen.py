import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from sqlalchemy.orm import Session
from db.session import get_engine
from gui import register_screen
from logic import auth

class LoginScreen:
    def __init__(self):
        self.user = None
        self.window = tk.Tk()
        self.window.title("Habit Tracker - Logowanie")
        self.window.geometry("400x300")

        ttk.Label(self.window, text="Użytkownik:").pack(pady=(30, 5))
        user_entry = ttk.Entry(self.window)
        user_entry.pack(pady=5)

        ttk.Label(self.window, text="Hasło:").pack(pady=5)
        password_entry = ttk.Entry(self.window, show="*")
        password_entry.pack(pady=5)

        ttk.Button(
            self.window,
            text="Zarejestruj się",
            command=register_screen.RegisterScreen
        ).pack(pady=20)

        ttk.Button(
            self.window,
            text="Zaloguj",
            command=lambda: self.attempt_login(user_entry.get(), password_entry.get())
        ).pack(pady=20)

        self.window.mainloop()

    def attempt_login(self, username, password):
        engine = get_engine()
        with Session(engine) as session:
            user = auth.login(session, username, password)
            if user:
                messagebox.showinfo("Sukces", "Zalogowano!")
                self.user = user
                self.window.destroy()
            else:
                messagebox.showerror("Błąd", "Nieprawidłowy login lub hasło.")
