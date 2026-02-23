
from decimal import Decimal
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.utils import uid
from src.core.errors import bad_request
from src.accounts.service import place_hold
from src.payments.models import Transfer
from src.audit.service import write_outbox


def create_transfer(db: Session, payload: dict, idempotency_key: str):
    if payload.get('currency','TRY') != settings.APP_CURRENCY:
        bad_request(f'Currency must be {settings.APP_CURRENCY}')
    existing = db.query(Transfer).filter(Transfer.idempotency_key == idempotency_key).first()
    if existing:
        return existing

    t = Transfer(
        id=uid(),
        from_account_id=payload['from_account_id'],
        to_account_id=payload['to_account_id'],
        amount=Decimal(str(payload['amount'])),
        currency=payload.get('currency','TRY'),
        status='INITIATED',
        idempotency_key=idempotency_key,
        reference=payload.get('reference'),
        transfer_type=payload.get('transfer_type','INTERNAL'),
    )
    db.add(t)
    db.commit(); db.refresh(t)
    return t


def authorize_transfer(db: Session, transfer_id: str):
    t = db.get(Transfer, transfer_id)
    if not t:
        bad_request('Transfer not found')
    if t.status != 'INITIATED':
        return t, None

    hold = place_hold(db, t.from_account_id, Decimal(str(t.amount)), reason=f'TRANSFER {t.id}')
    t.status = 'AUTHORIZED'
    t.hold_id = hold.id
    db.commit(); db.refresh(t)

    write_outbox(db, 'TransferAuthorized', {'transfer_id': t.id, 'hold_id': hold.id}, dedup_key=f'auth:{t.id}')
    return t, hold
