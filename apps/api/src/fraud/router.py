
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.auth import require_role, get_current_user
from src.fraud.service import (
    ensure_default_rules, list_rules, create_rule, update_rule, delete_rule,
    list_alerts, evaluate_transfer, transition_alert,
)

router = APIRouter(prefix='/fraud', tags=['fraud'])


@router.get('/rules', dependencies=[Depends(require_role('admin','teller'))])
def rules(db: Session = Depends(get_db)):
    ensure_default_rules(db)
    rs = list_rules(db)
    return [{
        'id': r.id,
        'name': r.name,
        'description': r.description,
        'rule_type': r.rule_type,
        'enabled': r.enabled,
        'severity': r.severity,
        'weight': str(r.weight),
        'params_json': r.params_json,
            'version': int(getattr(r,'version',1) or 1),
    } for r in rs]


@router.post('/rules', dependencies=[Depends(require_role('admin','teller'))])
def create(payload: dict, db: Session = Depends(get_db)):
    r = create_rule(db, payload)
    return {'id': r.id}


@router.patch('/rules/{rule_id}', dependencies=[Depends(require_role('admin','teller'))])
def patch(rule_id: str, payload: dict, db: Session = Depends(get_db)):
    r = update_rule(db, rule_id, payload)
    return {'id': r.id} if r else {'detail':'not found'}


@router.delete('/rules/{rule_id}', dependencies=[Depends(require_role('admin','teller'))])
def remove(rule_id: str, db: Session = Depends(get_db)):
    return {'deleted': delete_rule(db, rule_id)}


@router.get('/alerts', dependencies=[Depends(require_role('admin','teller'))])
def alerts(status: str | None = None, db: Session = Depends(get_db)):
    items = list_alerts(db, status=status)
    return [{
        'id': a.id,
        'severity': a.severity,
        'status': a.status,
        'reason': a.reason,
        'score': str(a.score),
        'transfer_id': a.transfer_id,
        'explain': a.explain_json,
        'created_at': str(a.created_at),
    } for a in items]


@router.get('/alerts/{alert_id}', dependencies=[Depends(require_role('admin','teller'))])
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    from src.fraud.models import Alert
    a = db.get(Alert, alert_id)
    if not a:
        return {'detail':'not found'}
    return {
        'id': a.id,
        'event_type': a.event_type,
        'entity_id': a.entity_id,
        'transfer_id': a.transfer_id,
        'customer_id': a.customer_id,
        'account_id': a.account_id,
        'score': str(a.score),
        'severity': a.severity,
        'status': a.status,
        'reason': a.reason,
        'explain': a.explain_json,
        'created_at': str(a.created_at),
        'updated_at': str(a.updated_at),
    }


@router.post('/alerts/{alert_id}/ack', dependencies=[Depends(require_role('admin','teller'))])
def ack(alert_id: str, payload: dict | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    a = transition_alert(db, alert_id, 'ACK', changed_by_user_id=user.id, note=(payload or {}).get('note'))
    return a if isinstance(a, dict) else {'id': a.id, 'status': a.status}


@router.post('/alerts/{alert_id}/escalate', dependencies=[Depends(require_role('admin','teller'))])
def escalate(alert_id: str, payload: dict | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    a = transition_alert(db, alert_id, 'ESCALATED', changed_by_user_id=user.id, note=(payload or {}).get('note'))
    return a if isinstance(a, dict) else {'id': a.id, 'status': a.status}


@router.post('/alerts/{alert_id}/close', dependencies=[Depends(require_role('admin','teller'))])
def close(alert_id: str, payload: dict | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    a = transition_alert(db, alert_id, 'CLOSED', changed_by_user_id=user.id, note=(payload or {}).get('note'))
    return a if isinstance(a, dict) else {'id': a.id, 'status': a.status}


@router.get('/alerts/{alert_id}/history', dependencies=[Depends(require_role('admin','teller'))])
def history(alert_id: str, db: Session = Depends(get_db)):
    from src.fraud.models import AlertHistory
    items = db.query(AlertHistory).filter(AlertHistory.alert_id == alert_id).order_by(AlertHistory.created_at.asc()).limit(200).all()
    return [{
        'id': h.id,
        'from_status': h.from_status,
        'to_status': h.to_status,
        'changed_by_user_id': h.changed_by_user_id,
        'note': h.note,
        'created_at': str(h.created_at),
    } for h in items]


@router.post('/evaluate/transfer/{transfer_id}', dependencies=[Depends(require_role('admin','teller'))])
def eval_transfer(transfer_id: str, db: Session = Depends(get_db)):
    alerts = evaluate_transfer(db, transfer_id)
    return {'created': len(alerts), 'alerts': [a.id for a in alerts]}
