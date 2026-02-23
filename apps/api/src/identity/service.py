
from sqlalchemy.orm import Session

from src.core.security import verify_password, create_access_token
from src.identity.models import User


def login(db: Session, email: str, password: str) -> str:
    u = db.query(User).filter(User.email == email).first()
    if not u:
        return ''
    if not verify_password(password, u.password_hash):
        return ''
    return create_access_token(u.id)
