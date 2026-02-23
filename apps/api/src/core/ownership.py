
from sqlalchemy.orm import Session

from src.accounts.models import Account
from src.identity.models import User
from src.core.errors import forbidden, not_found


def ensure_account_access(db: Session, user: User, account_id: str) -> Account:
    acc = db.get(Account, account_id)
    if not acc:
        not_found('Account not found')
    if any(r.name in {'admin','teller'} for r in user.roles):
        return acc
    if not user.customer_id or acc.customer_id != user.customer_id:
        forbidden('Not your account')
    return acc
