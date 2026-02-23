
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.identity.service import login
from src.core.auth import get_current_user

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login')
def login_route(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token = login(db, form.username, form.password)
    if not token:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return {'access_token': token, 'token_type': 'bearer'}


@router.get('/me')
def me(user=Depends(get_current_user)):
    return {'id': user.id, 'email': user.email, 'roles': [r.name for r in user.roles], 'customer_id': user.customer_id}
