
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.auth import require_role, get_current_user
from src.core.ownership import ensure_account_access
from src.accounts.models import Account
from src.accounts.service import get_balance

router = APIRouter(tags=['accounts'])


@router.get('/accounts', dependencies=[Depends(require_role('admin','teller','customer'))])
def list_accounts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(Account).order_by(Account.opened_at.desc())
    if not any(r.name in {'admin','teller'} for r in user.roles):
        q = q.filter(Account.customer_id == user.customer_id)
    items = q.limit(200).all()
    return [{'id': a.id, 'iban': a.iban, 'status': a.status, 'customer_id': a.customer_id} for a in items]


@router.get('/accounts/{account_id}/balances', dependencies=[Depends(require_role('admin','teller','customer'))])
def balances(account_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ensure_account_access(db, user, account_id)
    bal = get_balance(db, account_id)
    return {'ledger_balance': str(bal.ledger_balance), 'available_balance': str(bal.available_balance)}
