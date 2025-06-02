from sqlalchemy.orm import Session
from utils.encryption import *
from db.models import User

def register(session: Session, username: str, password: str):
    # Czy użytkownik już istnieje
    if session.query(User).filter_by(username=username).first():
        raise ValueError("Użytkownik o takiej nazwie już istnieje.")
    # Tworzymy nowego użytkownika z haszowanym hasłem
    user = User(username=username, password_hash=hash_password(password))
    session.add(user)
    session.commit()
    return user

def login(session, username, password):
    user = session.query(User).filter_by(username=username).first()
    if user and check_password(password, user.password_hash):
        return user
    return None