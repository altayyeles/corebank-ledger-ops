
from __future__ import annotations
import traceback

from celery import Celery
from sqlalchemy.orm import Session
from decimal import Decimal

from src.core.config import settings
from src.core.db import SessionLocal

import src.models  # noqa: F401  (tüm modelleri Base.metadata'ya register eder)
from src.audit.models import OutboxEvent
from src.audit.service import mark_processed
from src.payments.models import Transfer
from src.accounts.service import release_hold
from src.ledger.service import ensure_core_coa, post_entry, apply_balance_projection_from_entry
from src.ledger.models import CoaAccount
from src.fraud.service import evaluate_transfer
from src.cases.service import detect_sla_breaches
from src.notifications.service import enqueue_notification, send_pending_notifications

from src.core.metrics import transfers_total, outbox_lag_seconds, posting_latency, alerts_total, sla_breaches_total, notifications_total


celery_app = Celery('corebank', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)


def _db() -> Session:
    return SessionLocal()


@celery_app.task(name='src.worker.process_outbox')
def process_outbox(batch_size: int = 50):
    db = _db()
    try:
        events = (
            db.query(OutboxEvent)
            .filter(OutboxEvent.status=='NEW')
            .order_by(OutboxEvent.created_at.asc())
            .limit(batch_size)
            .all()
        )
        if not events:
            return 0

        try:
            from datetime import datetime, timezone
            lag = (datetime.now(timezone.utc) - events[0].created_at).total_seconds()
            outbox_lag_seconds.set(lag)
        except Exception:
            pass

        ensure_core_coa(db)
        coa_customer = db.query(CoaAccount).filter(CoaAccount.code=='201.01').first()
        coa_clearing = db.query(CoaAccount).filter(CoaAccount.code=='220.01').first()

        for e in events:
            if e.event_type == 'TransferAuthorized':
                transfer_id = e.payload_json['transfer_id']
                hold_id = e.payload_json['hold_id']
                t = db.get(Transfer, transfer_id)
                if not t or t.status != 'AUTHORIZED':
                    mark_processed(db, e.id)
                    continue

                lines = [
                    {"coa_account_id": coa_customer.id, "debit": Decimal(str(t.amount)), "credit": Decimal('0'), "account_id": t.to_account_id},
                    {"coa_account_id": coa_customer.id, "debit": Decimal('0'), "credit": Decimal(str(t.amount)), "account_id": t.from_account_id},
                ]

                with posting_latency.time():
                    je = post_entry(db, business_tx_id=t.id, description=f"Transfer {t.id}", currency=t.currency, lines=lines)
                apply_balance_projection_from_entry(db, je)
                release_hold(db, hold_id)

                t.status = 'SETTLED'
                db.commit()
                transfers_total.labels(status='SETTLED').inc()

                try:
                    new_alerts = evaluate_transfer(db, t.id)
                    if new_alerts:
                        alerts_total.inc(len(new_alerts))
                except Exception as e:
                    print(f"Error evaluating transfer {t.id}: {e}")
                    traceback.print_exc()
                    db.rollback()
                db.commit()

                mark_processed(db, e.id)
                continue

            if e.event_type == 'SlaBreached':
                payload = e.payload_json or {}
                case_id = payload.get('case_id')

                # queue email
                try:
                    enqueue_notification(db, channel='EMAIL', recipient='aml-team@demo.local', subject='SLA BREACH', body=f"Case {case_id} breached SLA", meta=payload, simulate_fail_once=False, max_attempts=5)
                    notifications_total.labels(channel='EMAIL', status='PENDING').inc()
                except Exception:
                    pass

                # queue slack (fail-once demo, fewer max attempts)
                try:
                    enqueue_notification(db, channel='SLACK', recipient='#aml-alerts', subject='SLA BREACH', body=f"Case {case_id} breached SLA", meta=payload, simulate_fail_once=True, max_attempts=3)
                    notifications_total.labels(channel='SLACK', status='PENDING').inc()
                except Exception:
                    pass

                mark_processed(db, e.id)
                continue

            mark_processed(db, e.id)

        return len(events)
    finally:
        db.close()


@celery_app.task(name='src.worker.check_sla_breaches')
def check_sla_breaches():
    db = _db()
    try:
        n = detect_sla_breaches(db)
        if n:
            sla_breaches_total.inc(n)
        return n
    finally:
        db.close()


@celery_app.task(name='src.worker.send_notifications')
def send_notifications():
    db = _db()
    try:
        result = send_pending_notifications(db)
        for channel, sts in result.items():
            if channel == 'processed':
                continue
            for status, cnt in (sts or {}).items():
                try:
                    notifications_total.labels(channel=channel, status=status).inc(cnt)
                except Exception:
                    pass
        return result
    finally:
        db.close()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(2.0, process_outbox.s(), name='poll_outbox')
    sender.add_periodic_task(30.0, check_sla_breaches.s(), name='check_sla_breaches')
    sender.add_periodic_task(15.0, send_notifications.s(), name='send_notifications')
