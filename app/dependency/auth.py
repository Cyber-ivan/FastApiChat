from passlib.context import CryptContext

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

