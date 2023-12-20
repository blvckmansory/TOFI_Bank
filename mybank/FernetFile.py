from mybank import settings
from cryptography.fernet import Fernet


key = settings.SECRET_KEY
fernet = Fernet(key)


def fernet_encrypt(message):
    return fernet.encrypt(message.encode())


def fernet_decrypt(message):
    return fernet.decrypt(eval(message)).decode()