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
        window.geometry("375x150")
        window.resizable(False, False)

        root = ttk.Frame(window, padding=20)
        root.pack(expand=True, fill=tk.BOTH)

        ttk.Label(root, text="Nazwa użytkownika:").grid(row=0, column=0, sticky=tk.E, pady=(0, 5), padx=5)
        user_entry = ttk.Entry(root, width=35)
        user_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5), padx=(0,5))

        ttk.Label(root, text="Hasło:").grid(row=1, column=0, sticky=tk.E, pady=(0, 5), padx=5)
        password_entry = ttk.Entry(root, show="*")
        password_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 5), padx=(0,5))

        ttk.Label(root, text="Powtórz hasło:").grid(row=2, column=0, sticky=tk.E, pady=(0, 5), padx=5)
        re_password_entry = ttk.Entry(root, show="*")
        re_password_entry.grid(row=2, column=1, sticky=tk.W, pady=(0, 5), padx=(0,5))

        def key_enter(event):
            attempt_register(user_entry.get(), password_entry.get(), re_password_entry.get(), window)
        window.bind("<Return>", key_enter)

        ttk.Button(
            root,
            text="Zarejestruj",
            command=lambda: attempt_register(
                user_entry.get(), password_entry.get(), re_password_entry.get(), window
            )
        ).grid(row=4, column=0, columnspan=2, pady=(5, 0))

        window.mainloop()

