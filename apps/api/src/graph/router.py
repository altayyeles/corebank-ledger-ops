
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.auth import require_role
from src.customer.models import Customer
from src.accounts.models import Account
from src.payments.models import Transfer
from src.fraud.models import Alert
from src.cases.models import Case

router = APIRouter(prefix='/graph', tags=['graph'])


@router.get('/customer/{customer_id}', dependencies=[Depends(require_role('admin','teller'))])
def customer_graph(customer_id: str, db: Session = Depends(get_db)):
    cust = db.get(Customer, customer_id)
    if not cust:
        return {'detail':'Customer not found'}

    nodes=[]
    edges=[]

    def add_node(id_, type_, label, meta=None):
        meta = meta or {}
        if type_ == 'account':
            meta.setdefault('href', f'/account/{id_}')
        elif type_ == 'transfer':
            meta.setdefault('href', f'/transfer/{id_}')
        elif type_ == 'alert':
            meta.setdefault('href', f'/alert-history?alert_id={id_}')
        elif type_ == 'case':
            meta.setdefault('href', f'/cases')
        nodes.append({'id': id_, 'type': type_, 'label': label, 'meta': meta})

    add_node(cust.id, 'customer', cust.full_name, {'email': cust.email})

    accounts = db.query(Account).filter(Account.customer_id==cust.id).all()
    for a in accounts:
        add_node(a.id, 'account', a.iban, {'status': a.status})
        edges.append({'from': cust.id, 'to': a.id, 'type': 'OWNS'})

    acc_ids = [a.id for a in accounts]
    transfers = db.query(Transfer).filter(Transfer.from_account_id.in_(acc_ids)).order_by(Transfer.created_at.desc()).limit(200).all() if acc_ids else []
    for t in transfers:
        add_node(t.id, 'transfer', f"{t.status} {t.amount}", {'created_at': str(t.created_at), 'type': t.transfer_type})
        edges.append({'from': t.from_account_id, 'to': t.id, 'type': 'SENT'})
        edges.append({'from': t.id, 'to': t.to_account_id, 'type': 'TO'})

    transfer_ids = [t.id for t in transfers]
    alerts = db.query(Alert).filter(Alert.transfer_id.in_(transfer_ids)).order_by(Alert.created_at.desc()).limit(200).all() if transfer_ids else []
    for al in alerts:
        add_node(al.id, 'alert', f"{al.severity} {al.reason}", {'status': al.status, 'score': str(al.score)})
        edges.append({'from': al.transfer_id, 'to': al.id, 'type': 'TRIGGERS'})

    alert_ids = [a.id for a in alerts]
    cases = db.query(Case).filter(Case.alert_id.in_(alert_ids)).order_by(Case.created_at.desc()).limit(200).all() if alert_ids else []
    for c in cases:
        add_node(c.id, 'case', f"{c.status} {c.priority}", {'assignee': c.assignee_user_id, 'sla_due_at': str(c.sla_due_at) if c.sla_due_at else None})
        edges.append({'from': c.alert_id, 'to': c.id, 'type': 'CASE'})

    return {'nodes': nodes, 'edges': edges}
