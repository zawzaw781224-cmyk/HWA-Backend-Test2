from passlib.context import CryptContext

context_password = CryptContext(schemes=["bcrypt"],deprecated = "auto")
def hash_context (password:str):
    return context_password.hash(password)
def verify_password(password:str,hashed:str):
    return context_password.verify(password,hashed)
