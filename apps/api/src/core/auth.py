
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette.requests import Request

from src.core.db import get_db
from src.core.security import decode_token
from src.identity.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
        user_id = payload.get('sub')
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    request.state.user_id = user.id
    return user


def require_role(*roles: str):
    def _inner(user: User = Depends(get_current_user)):
        if any(r.name in set(roles) for r in user.roles):
            return user
        raise HTTPException(status_code=403, detail='Insufficient role')

    return _inner
