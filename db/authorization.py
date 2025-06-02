from sqlalchemy.orm import Session
from models import User
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register(session: Session, username: str, password: str):
    if session.query(User).filter_by(username=username).first():
        raise ValueError("Użytkownik już istnieje")
    user = User(username=username, password_hash=hash_password(password))
    session.add(user)
    session.commit()

def login(session: Session, username: str, password: str) -> bool:
    user = session.query(User).filter_by(username=username).first()
    if user and check_password(password, user.password_hash):
        return True
    return False