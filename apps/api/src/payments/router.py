
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.auth import require_role, get_current_user
from src.core.ownership import ensure_account_access
from src.payments.models import Transfer
from src.payments.service import create_transfer, authorize_transfer

router = APIRouter(prefix='/transfers', tags=['payments'])


@router.post('', dependencies=[Depends(require_role('admin','teller','customer'))])
def create(payload: dict, idempotency_key: str = Header(..., alias='Idempotency-Key'), db: Session = Depends(get_db), user=Depends(get_current_user)):
    ensure_account_access(db, user, payload['from_account_id'])
    t = create_transfer(db, payload, idempotency_key)
    return {'id': t.id, 'status': t.status}


@router.get('/{transfer_id}', dependencies=[Depends(require_role('admin','teller','customer'))])
def get_transfer(transfer_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.get(Transfer, transfer_id)
    if not t:
        return {'detail':'not found'}
    ensure_account_access(db, user, t.from_account_id)
    return {
        'id': t.id,
        'status': t.status,
        'amount': str(t.amount),
        'currency': t.currency,
        'type': t.transfer_type,
        'from_account_id': t.from_account_id,
        'to_account_id': t.to_account_id,
        'created_at': str(t.created_at),
    }


@router.post('/{transfer_id}/authorize', dependencies=[Depends(require_role('admin','teller'))])
def authorize(transfer_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t0 = db.get(Transfer, transfer_id)
    if t0:
        ensure_account_access(db, user, t0.from_account_id)
    t, hold = authorize_transfer(db, transfer_id)
    return {'transfer_id': t.id, 'status': t.status, 'hold_id': hold.id if hold else None}
