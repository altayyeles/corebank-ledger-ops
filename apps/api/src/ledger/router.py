
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.auth import require_role
from src.ledger.models import JournalEntry, JournalLine
from src.ledger.service import trial_balance

router = APIRouter(prefix='/ledger', tags=['ledger'])


@router.get('/journal-entries', dependencies=[Depends(require_role('admin','teller'))])
def entries(db: Session = Depends(get_db)):
    es = db.query(JournalEntry).order_by(JournalEntry.created_at.desc()).limit(50).all()
    out=[]
    for e in es:
        ls = db.query(JournalLine).filter(JournalLine.entry_id==e.id).all()
        out.append({'id': e.id, 'entry_no': e.entry_no, 'business_tx_id': e.business_tx_id, 'description': e.description, 'created_at': str(e.created_at)})
    return out


@router.get('/trial-balance', dependencies=[Depends(require_role('admin','teller'))])
def tb(db: Session = Depends(get_db)):
    from decimal import Decimal
    rows = trial_balance(db)
    td = Decimal('0'); tc = Decimal('0')
    out=[]
    for code,name,d,c in rows:
        d=Decimal(str(d)); c=Decimal(str(c))
        td+=d; tc+=c
        out.append({'coa_code': code, 'coa_name': name, 'debit': str(d), 'credit': str(c)})
    return {'as_of': datetime.now(timezone.utc).isoformat(), 'rows': out, 'total_debit': str(td), 'total_credit': str(tc)}
