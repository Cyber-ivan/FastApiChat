from passlib.context import CryptContext
from fastapi import HTTPException

from app.core.security import decode_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """
    :param plain_password:
    :param hashed_password:
    :return: Bool
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    :param password:
    :return: hashed_password
    """
    return pwd_context.hash(password)


def get_user_id_in_token(token):
    """
    :param token:
    :return: user_id : int
    """
    if not token:
        raise HTTPException(status_code=401, detail="Access token not found")
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return int(user_id)
