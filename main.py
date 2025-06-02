import sys
import db.models as db
from gui.login_screen import LoginScreen
from gui.main_screen import MainScreen
from db.session import get_engine

if __name__ == "__main__":
    # Inicjalizacja bazy danych
    engine = get_engine()
    db.Base.metadata.create_all(engine)
    db.init_db()

    # GUI
    running_loop = True
    while running_loop:
        user = LoginScreen().user
        if user is None:
            sys.exit("Login failed")
        ms = MainScreen(user)
        running_loop = ms.log_out