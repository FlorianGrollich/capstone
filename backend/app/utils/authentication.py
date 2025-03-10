from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return settings.pwd_ctx.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return settings.pwd_ctx.hash(password)
