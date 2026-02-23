
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.auth import require_role
from src.notifications.models import Notification

router = APIRouter(prefix='/notifications', tags=['notifications'])


@router.get('', dependencies=[Depends(require_role('admin','teller'))])
def list_notifications(limit: int = 200, db: Session = Depends(get_db)):
    items = db.query(Notification).order_by(Notification.created_at.desc()).limit(limit).all()
    return [{
        'id': n.id,
        'channel': n.channel,
        'recipient': n.recipient,
        'subject': n.subject,
        'status': n.status,
        'attempt_count': int(n.attempt_count),
        'max_attempts': int(n.max_attempts),
        'next_attempt_at': str(n.next_attempt_at),
        'last_error': n.last_error,
        'created_at': str(n.created_at),
        'meta': n.meta_json,
    } for n in items]



@router.get('/failed', dependencies=[Depends(require_role('admin','teller'))])
def list_failed(limit: int = 200, db: Session = Depends(get_db)):
    items = (db.query(Notification)
             .filter(Notification.status == 'FAILED')
             .order_by(Notification.created_at.desc())
             .limit(limit)
             .all())
    return [{
        'id': n.id,
        'channel': n.channel,
        'recipient': n.recipient,
        'subject': n.subject,
        'status': n.status,
        'attempt_count': int(n.attempt_count),
        'max_attempts': int(n.max_attempts),
        'next_attempt_at': str(n.next_attempt_at),
        'last_error': n.last_error,
        'created_at': str(n.created_at),
        'meta': n.meta_json,
    } for n in items]


@router.post('/{notification_id}/requeue', dependencies=[Depends(require_role('admin','teller'))])
def requeue(notification_id: str, db: Session = Depends(get_db)):
    from datetime import datetime, timezone

    n = db.get(Notification, notification_id)
    if not n:
        return {'detail': 'not found'}
    # reset back to queue
    n.status = 'PENDING'
    n.last_error = None
    n.attempt_count = 0
    n.next_attempt_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(n)
    return {'id': n.id, 'status': n.status, 'attempt_count': int(n.attempt_count)}
