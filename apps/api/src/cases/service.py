
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.core.utils import uid
from src.cases.models import Case, CaseNote, SarReport
from src.fraud.models import Alert
from src.audit.service import write_outbox


def create_case(db: Session, payload: dict):
    sla = payload.get('sla_due_at')
    sla_dt = datetime.fromisoformat(sla) if sla else None
    c = Case(
        id=uid(),
        alert_id=payload.get('alert_id'),
        status='OPEN',
        priority=payload.get('priority','MEDIUM'),
        assignee_user_id=payload.get('assignee_user_id'),
        sla_due_at=sla_dt,
    )
    db.add(c)
    if c.alert_id:
        al = db.get(Alert, c.alert_id)
        if al:
            al.status = 'IN_REVIEW'
    db.commit(); db.refresh(c)
    return c


def assign_case(db: Session, case_id: str, payload: dict):
    c = db.get(Case, case_id)
    if not c:
        return None
    c.assignee_user_id = payload.get('assignee_user_id')
    c.priority = payload.get('priority', c.priority)
    sla = payload.get('sla_due_at')
    c.sla_due_at = datetime.fromisoformat(sla) if sla else c.sla_due_at
    c.status = 'ASSIGNED'
    c.assigned_at = datetime.now(timezone.utc)
    c.updated_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(c)
    return c


def close_case(db: Session, case_id: str):
    c = db.get(Case, case_id)
    if not c:
        return None
    c.status = 'CLOSED'
    c.updated_at = datetime.now(timezone.utc)
    if c.alert_id:
        al = db.get(Alert, c.alert_id)
        if al:
            al.status = 'CLOSED'
    db.commit(); db.refresh(c)
    return c


def add_note(db: Session, case_id: str, author_user_id: str | None, note: str):
    n = CaseNote(id=uid(), case_id=case_id, author_user_id=author_user_id, note=note)
    db.add(n); db.commit(); db.refresh(n)
    return n


def list_cases(db: Session, status: str | None = None):
    q = db.query(Case).order_by(Case.created_at.desc())
    if status:
        q = q.filter(Case.status == status)
    return q.limit(200).all()


def export_sar(db: Session, case_id: str, narrative: str, reporter: str):
    c = db.get(Case, case_id)
    if not c:
        return None
    al = db.get(Alert, c.alert_id) if c.alert_id else None
    content = {
        'case_id': c.id,
        'status': c.status,
        'priority': c.priority,
        'assignee_user_id': c.assignee_user_id,
        'sla_due_at': c.sla_due_at.isoformat() if c.sla_due_at else None,
        'sla_breached': c.sla_breached,
        'breached_at': c.breached_at.isoformat() if c.breached_at else None,
        'alert': {
            'id': al.id,
            'severity': al.severity,
            'reason': al.reason,
            'score': str(al.score),
            'explain': al.explain_json,
            'transfer_id': al.transfer_id,
        } if al else None,
        'narrative': narrative,
        'reporter': reporter,
        'exported_at': datetime.now(timezone.utc).isoformat(),
    }
    r = SarReport(id=uid(), case_id=c.id, content_json=content)
    db.add(r); db.commit(); db.refresh(r)
    return r


def detect_sla_breaches(db: Session, now=None) -> int:
    now = now or datetime.now(timezone.utc)
    items = (
        db.query(Case)
        .filter(Case.status.in_(['OPEN','ASSIGNED']))
        .filter(Case.sla_due_at.isnot(None))
        .filter(Case.sla_due_at < now)
        .filter(Case.sla_breached == 'NO')
        .all()
    )
    for c in items:
        c.sla_breached = 'YES'
        c.breached_at = now
        c.updated_at = now
        try:
            write_outbox(db, 'SlaBreached', {
                'case_id': c.id,
                'alert_id': c.alert_id,
                'assignee_user_id': c.assignee_user_id,
                'sla_due_at': c.sla_due_at.isoformat() if c.sla_due_at else None,
            }, dedup_key=f'sla:{c.id}')
        except Exception:
            pass
    db.commit()
    return len(items)
