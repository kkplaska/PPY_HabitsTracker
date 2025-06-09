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
        self.window.geometry("350x250")
        self.window.resizable(False, False)

        root = ttk.Frame(self.window, padding=20)
        root.pack(expand=True, fill=tk.BOTH)

        loginFrame = ttk.LabelFrame(root, text="Logowanie")
        loginFrame.pack(expand=True, fill=tk.BOTH)

        # Username
        ttk.Label(loginFrame, text="Użytkownik:").grid(row=0, column=0, sticky=tk.E, pady=(0, 5), padx=5)
        user_entry = ttk.Entry(loginFrame, width=35)
        user_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5), padx=(0,5))

        # Password
        ttk.Label(loginFrame, text="Hasło:").grid(row=1, column=0, sticky=tk.E, pady=(0, 5), padx=5)
        password_entry = ttk.Entry(loginFrame, show="*", width=35)
        password_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 5), padx=(0,5))

        def key_enter(event):
            self.attempt_login(user_entry.get(), password_entry.get())
        self.window.bind("<Return>", key_enter)

        # Login button
        ttk.Button(
            loginFrame,
            text="Zaloguj",
            command=lambda: self.attempt_login(
                user_entry.get(), password_entry.get()
            )
        ).grid(row=3, column=0, columnspan=2, pady=(5, 0))

        registerFrame = ttk.LabelFrame(root, text="Rejestracja")
        registerFrame.pack(expand=True, fill=tk.BOTH)
        # Register button
        ttk.Button(
            registerFrame,
            text="Zarejestruj się",
            command=lambda: register_screen.RegisterScreen()
        ).pack(expand=True, fill=tk.BOTH, pady=20, padx=20)

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
