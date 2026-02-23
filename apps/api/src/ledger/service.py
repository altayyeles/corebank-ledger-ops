
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.core.utils import uid, gen_entry_no
from src.core.errors import bad_request
from src.ledger.models import CoaAccount, JournalEntry, JournalLine
from src.accounts.models import AccountBalance


def ensure_core_coa(db: Session):
    def up(code, name, type_):
        acc = db.query(CoaAccount).filter(CoaAccount.code == code).first()
        if not acc:
            acc = CoaAccount(id=uid(), code=code, name=name, type=type_)
            db.add(acc)
        return acc
    up('101.01','Cash','ASSET')
    up('201.01','Customer Deposits','LIABILITY')
    up('220.01','Clearing Payable','LIABILITY')
    db.commit()


def post_entry(db: Session, business_tx_id: str, description: str, currency: str, lines: list[dict]) -> JournalEntry:
    td = sum(Decimal(str(l.get('debit',0))) for l in lines)
    tc = sum(Decimal(str(l.get('credit',0))) for l in lines)
    if td != tc:
        bad_request('Unbalanced journal entry')

    e = JournalEntry(id=uid(), entry_no=gen_entry_no(), business_tx_id=business_tx_id, description=description, currency=currency)
    db.add(e)
    for l in lines:
        db.add(JournalLine(id=uid(), entry_id=e.id, coa_account_id=l['coa_account_id'], debit=Decimal(str(l.get('debit',0))), credit=Decimal(str(l.get('credit',0))), account_id=l.get('account_id')))
    db.commit(); db.refresh(e)
    return e


def apply_balance_projection_from_entry(db: Session, entry: JournalEntry):
    lines = db.query(JournalLine).filter(JournalLine.entry_id == entry.id).all()
    for l in lines:
        if not l.account_id:
            continue
        bal = db.get(AccountBalance, l.account_id)
        if not bal:
            continue
        delta = Decimal(str(l.credit)) - Decimal(str(l.debit))
        bal.ledger_balance = bal.ledger_balance + delta
        bal.available_balance = bal.available_balance + delta
    db.commit()


def trial_balance(db: Session):
    rows = (
        db.query(CoaAccount.code, CoaAccount.name, func.coalesce(func.sum(JournalLine.debit),0), func.coalesce(func.sum(JournalLine.credit),0))
        .join(JournalLine, JournalLine.coa_account_id == CoaAccount.id)
        .group_by(CoaAccount.code, CoaAccount.name)
        .order_by(CoaAccount.code)
        .all()
    )
    return rows
