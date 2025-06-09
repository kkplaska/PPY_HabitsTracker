"""
utils/encryption.py

Moduł odpowiedzialny za hashowanie i weryfikację haseł użytkowników
z wykorzystaniem biblioteki bcrypt.
"""

import bcrypt

def hash_password(password: str) -> str:
    """
    Generuje bezpieczny hasz z podanego hasła.

    :param password: hasło w postaci jawnej (string)
    :return: hasz hasła zakodowany jako string
    """
    # bcrypt.hashpw zwraca bytes, dlatego dekodujemy wynik na UTF-8
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def check_password(password: str, hashed: str) -> bool:
    """
    Weryfikuje, czy podane hasło odpowiada wcześniej wygenerowanemu hashowi.

    :param password: hasło w postaci jawnej (string)
    :param hashed: hasz hasła, wygenerowany wcześniej przez hash_password (string)
    :return: True, jeśli hasło jest poprawne, w przeciwnym razie False
    """
    # bcrypt.checkpw oczekuje parametrów typu bytes
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
