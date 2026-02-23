
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.auth import require_role, get_current_user
from src.cases.service import create_case, assign_case, close_case, add_note, list_cases, export_sar
from src.cases.models import Case

router = APIRouter(prefix='/cases', tags=['cases'])


@router.get('', dependencies=[Depends(require_role('admin','teller'))])
def cases(status: str | None = None, db: Session = Depends(get_db)):
    items = list_cases(db, status=status)
    return [{
        'id': c.id,
        'alert_id': c.alert_id,
        'status': c.status,
        'priority': c.priority,
        'assignee_user_id': c.assignee_user_id,
        'sla_due_at': str(c.sla_due_at) if c.sla_due_at else None,
        'sla_breached': c.sla_breached,
        'breached_at': str(c.breached_at) if c.breached_at else None,
        'created_at': str(c.created_at),
    } for c in items]


@router.get('/{case_id}', dependencies=[Depends(require_role('admin','teller'))])
def get_case(case_id: str, db: Session = Depends(get_db)):
    c = db.get(Case, case_id)
    if not c:
        return {'detail':'not found'}
    return {
        'id': c.id,
        'alert_id': c.alert_id,
        'status': c.status,
        'priority': c.priority,
        'assignee_user_id': c.assignee_user_id,
        'sla_due_at': str(c.sla_due_at) if c.sla_due_at else None,
        'sla_breached': c.sla_breached,
        'breached_at': str(c.breached_at) if c.breached_at else None,
        'created_at': str(c.created_at),
        'updated_at': str(c.updated_at),
    }


@router.post('', dependencies=[Depends(require_role('admin','teller'))])
def create(payload: dict, db: Session = Depends(get_db)):
    c = create_case(db, payload)
    return {'id': c.id, 'status': c.status}


@router.post('/{case_id}/assign', dependencies=[Depends(require_role('admin','teller'))])
def assign(case_id: str, payload: dict, db: Session = Depends(get_db)):
    c = assign_case(db, case_id, payload)
    return {'id': c.id, 'status': c.status} if c else {'detail':'not found'}


@router.post('/{case_id}/close', dependencies=[Depends(require_role('admin','teller'))])
def close(case_id: str, db: Session = Depends(get_db)):
    c = close_case(db, case_id)
    return {'id': c.id, 'status': c.status} if c else {'detail':'not found'}


@router.post('/{case_id}/notes', dependencies=[Depends(require_role('admin','teller'))])
def add_note_route(case_id: str, payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    n = add_note(db, case_id, author_user_id=user.id, note=payload.get('note',''))
    return {'id': n.id}


@router.post('/{case_id}/sar', dependencies=[Depends(require_role('admin','teller'))])
def sar(case_id: str, payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    r = export_sar(db, case_id, narrative=payload.get('narrative',''), reporter=user.email)
    return {'sar_report_id': r.id, 'content': r.content_json} if r else {'detail':'not found'}


@router.get('/sla-breaches', dependencies=[Depends(require_role('admin','teller'))])
def breaches(db: Session = Depends(get_db)):
    items = db.query(Case).filter(Case.sla_breached=='YES').order_by(Case.breached_at.desc()).limit(200).all()
    return [{
        'id': c.id,
        'alert_id': c.alert_id,
        'status': c.status,
        'priority': c.priority,
        'assignee_user_id': c.assignee_user_id,
        'sla_due_at': str(c.sla_due_at) if c.sla_due_at else None,
        'breached_at': str(c.breached_at) if c.breached_at else None,
    } for c in items]
