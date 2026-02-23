
from decimal import Decimal
from sqlalchemy.orm import Session

from src.core.utils import uid, gen_iban
from src.core.errors import bad_request
from src.accounts.models import Product, Account, AccountBalance, Hold


def create_account(db: Session, customer_id: str, product_id: str) -> Account:
    a = Account(id=uid(), customer_id=customer_id, product_id=product_id, iban=gen_iban())
    db.add(a)
    db.add(AccountBalance(account_id=a.id, ledger_balance=Decimal('0'), available_balance=Decimal('0')))
    db.commit(); db.refresh(a)
    return a


def get_balance(db: Session, account_id: str) -> AccountBalance:
    bal = db.get(AccountBalance, account_id)
    if not bal:
        bad_request('Balance not found')
    return bal


def place_hold(db: Session, account_id: str, amount: Decimal, reason: str) -> Hold:
    bal = get_balance(db, account_id)
    if bal.available_balance < amount:
        bad_request('Insufficient available balance')
    h = Hold(id=uid(), account_id=account_id, amount=amount, reason=reason)
    bal.available_balance = bal.available_balance - amount
    db.add(h)
    db.commit(); db.refresh(h)
    return h


def release_hold(db: Session, hold_id: str):
    h = db.get(Hold, hold_id)
    if not h or h.status != 'ACTIVE':
        return
    bal = get_balance(db, h.account_id)
    bal.available_balance = bal.available_balance + h.amount
    h.status = 'RELEASED'
    db.commit()
