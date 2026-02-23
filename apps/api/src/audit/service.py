
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.core.utils import uid
from src.audit.models import OutboxEvent


def write_outbox(db: Session, event_type: str, payload: dict, dedup_key: str):
    e = OutboxEvent(id=uid(), event_type=event_type, payload_json=payload, dedup_key=dedup_key, status='NEW')
    db.add(e)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


def mark_processed(db: Session, outbox_id: str):
    e = db.get(OutboxEvent, outbox_id)
    if not e:
        return
    e.status = 'PROCESSED'
    e.processed_at = datetime.now(timezone.utc)
    db.commit()
