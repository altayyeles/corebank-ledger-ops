
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from src.core.utils import uid
from src.notifications.models import Notification


def enqueue_notification(
    db: Session,
    *,
    channel: str,
    recipient: str,
    subject: str,
    body: str,
    meta: dict | None = None,
    simulate_fail_once: bool = False,
    max_attempts: int = 5,
) -> Notification:
    meta_json = meta or {}
    if simulate_fail_once:
        meta_json['simulate_fail_once'] = True

    n = Notification(
        id=uid(),
        channel=channel,
        recipient=recipient,
        subject=subject,
        body=body,
        status='PENDING',
        meta_json=meta_json,
        attempt_count=0,
        max_attempts=max_attempts,
        next_attempt_at=datetime.now(timezone.utc),
        last_error=None,
    )
    db.add(n)
    db.commit(); db.refresh(n)
    return n


def _backoff_seconds(attempt: int) -> int:
    return min(300, 2 ** max(0, attempt))


def send_pending_notifications(db: Session, limit: int = 50) -> dict:
    """Simulated sender with retry/backoff + max_attempts.

    Returns counts per (channel,status) to drive metrics.
    """
    now = datetime.now(timezone.utc)
    items = (
        db.query(Notification)
        .filter(Notification.status.in_(['PENDING','RETRY']))
        .filter(Notification.next_attempt_at <= now)
        .order_by(Notification.created_at.asc())
        .limit(limit)
        .all()
    )

    counts: dict[tuple[str,str], int] = {}

    for n in items:
        n.attempt_count = int(n.attempt_count) + 1

        if int(n.attempt_count) > int(n.max_attempts):
            n.status = 'FAILED'
            n.last_error = n.last_error or 'Max attempts exceeded'
            n.next_attempt_at = now
            counts[(n.channel, 'FAILED')] = counts.get((n.channel,'FAILED'),0) + 1
            continue

        if n.meta_json.get('simulate_fail_once') and not n.meta_json.get('failed_once'):
            n.meta_json['failed_once'] = True
            n.status = 'RETRY'
            n.last_error = 'Simulated transient failure'
            n.next_attempt_at = now + timedelta(seconds=_backoff_seconds(int(n.attempt_count)))
            counts[(n.channel, 'RETRY')] = counts.get((n.channel,'RETRY'),0) + 1
            continue

        n.status = 'SENT'
        n.last_error = None
        n.next_attempt_at = now
        counts[(n.channel, 'SENT')] = counts.get((n.channel,'SENT'),0) + 1

    db.commit()

    out = {}
    for (ch, st), c in counts.items():
        out.setdefault(ch, {})[st] = c
    out['processed'] = len(items)
    return out
