
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import func

import src.models  # noqa: F401
from src.core.utils import uid
from src.fraud.models import FraudRule, Alert, AlertHistory
from src.payments.models import Transfer
from src.accounts.models import Account
from src.core.metrics import alert_transitions_total


DEFAULT_RULES = [
    {
        'name': 'amount_threshold_5000',
        'description': 'Flag transfers with amount >= 5000 TRY',
        'rule_type': 'AMOUNT_THRESHOLD',
        'severity': 'HIGH',
        'weight': '40.0',
        'params_json': {'threshold': '5000.00'},
    },
    {
        'name': 'velocity_3_in_2min',
        'description': 'Flag 3+ outgoing transfers within 120 seconds',
        'rule_type': 'VELOCITY',
        'severity': 'MEDIUM',
        'weight': '25.0',
        'params_json': {'count': 3, 'window_seconds': 120},
    },
]


SEVERITY_FACTOR = {'LOW': Decimal('0.80'), 'MEDIUM': Decimal('1.00'), 'HIGH': Decimal('1.20')}


def _norm_score(base: Decimal, hits: list[dict]) -> Decimal:
    s = base
    for h in hits:
        w = Decimal(str(h.get('weight', '0')))
        sev = (h.get('severity') or 'MEDIUM').upper()
        s += w * SEVERITY_FACTOR.get(sev, Decimal('1.00'))
    # clamp 0..100
    if s < 0:
        return Decimal('0')
    if s > 100:
        return Decimal('100')
    return s


def ensure_default_rules(db: Session):
    for d in DEFAULT_RULES:
        r = db.query(FraudRule).filter(FraudRule.name == d['name']).first()
        if not r:
            db.add(FraudRule(
                id=uid(),
                name=d['name'],
                description=d['description'],
                rule_type=d['rule_type'],
                severity=d['severity'],
                weight=Decimal(d['weight']),
                params_json=d['params_json'],
                enabled='YES',
                version=1,
            ))
    db.commit()


def list_rules(db: Session):
    return db.query(FraudRule).order_by(FraudRule.created_at.desc()).limit(200).all()


def create_rule(db: Session, payload: dict):
    r = FraudRule(
        id=uid(),
        name=payload['name'],
        description=payload.get('description'),
        rule_type=payload['rule_type'],
        severity=payload.get('severity', 'MEDIUM'),
        weight=Decimal(str(payload.get('weight', '10'))),
        params_json=payload.get('params_json') or {},
        enabled=payload.get('enabled', 'YES'),
        version=1,
    )
    db.add(r)
    db.commit(); db.refresh(r)
    return r


def update_rule(db: Session, rule_id: str, patch: dict):
    r = db.get(FraudRule, rule_id)
    if not r:
        return None

    changed = False
    for k in ['name', 'description', 'rule_type', 'severity', 'enabled']:
        if k in patch and getattr(r, k) != patch[k]:
            setattr(r, k, patch[k])
            if k in {'rule_type', 'severity', 'enabled'}:
                changed = True

    if 'weight' in patch:
        nw = Decimal(str(patch['weight']))
        if r.weight != nw:
            r.weight = nw
            changed = True

    if 'params_json' in patch:
        if r.params_json != patch['params_json']:
            r.params_json = patch['params_json']
            changed = True

    if changed:
        r.version = int(getattr(r, 'version', 1) or 1) + 1

    db.commit(); db.refresh(r)
    return r


def delete_rule(db: Session, rule_id: str) -> bool:
    r = db.get(FraudRule, rule_id)
    if not r:
        return False
    db.delete(r)
    db.commit()
    return True


def list_alerts(db: Session, status: str | None = None, limit: int = 200):
    q = db.query(Alert).order_by(Alert.created_at.desc())
    if status:
        q = q.filter(Alert.status == status)
    return q.limit(limit).all()


def evaluate_transfer(db: Session, transfer_id: str) -> list[Alert]:
    """Aggregate rule hits into one master alert per transfer.

    V10:
    - reason codes
    - dedupe by reason_code
    - top_reason_code
    - normalized score with severity multipliers and clamp 0..100
    - hits include rule_version
    """
    t = db.get(Transfer, transfer_id)
    if not t:
        return []
    acc = db.get(Account, t.from_account_id)
    customer_id = acc.customer_id if acc else None

    rules = db.query(FraudRule).filter(FraudRule.enabled == 'YES').all()
    hits: list[dict] = []

    for r in rules:
        rv = int(getattr(r, 'version', 1) or 1)
        if r.rule_type == 'AMOUNT_THRESHOLD':
            threshold = Decimal(str(r.params_json.get('threshold', '0')))
            amt = Decimal(str(t.amount))
            if amt >= threshold:
                hits.append({
                    'reason_code': 'RC_001_AMOUNT',
                    'rule_id': r.id,
                    'rule_name': r.name,
                    'rule_type': r.rule_type,
                    'rule_version': rv,
                    'severity': r.severity,
                    'weight': str(r.weight),
                    'inputs': {'amount': str(amt), 'threshold': str(threshold)},
                    'why': 'Transfer amount exceeds configured threshold.'
                })

        elif r.rule_type == 'VELOCITY':
            cnt = int(r.params_json.get('count', 3))
            window = int(r.params_json.get('window_seconds', 120))
            since = datetime.now(timezone.utc) - timedelta(seconds=window)
            n = int((db.query(func.count(Transfer.id))
                     .filter(Transfer.from_account_id == t.from_account_id, Transfer.created_at >= since)
                     .scalar() or 0))
            if n >= cnt:
                hits.append({
                    'reason_code': 'RC_010_VELOCITY',
                    'rule_id': r.id,
                    'rule_name': r.name,
                    'rule_type': r.rule_type,
                    'rule_version': rv,
                    'severity': r.severity,
                    'weight': str(r.weight),
                    'inputs': {'count': n, 'threshold_count': cnt, 'window_seconds': window},
                    'why': 'High frequency outgoing transfers detected.'
                })

    if not hits:
        return []

    # dedupe by reason_code, keep the highest-weight hit per reason_code
    by_code: dict[str, dict] = {}
    for h in hits:
        code = h.get('reason_code') or 'RC_UNKNOWN'
        w = Decimal(str(h.get('weight', '0')))
        cur = by_code.get(code)
        if (cur is None) or (w > Decimal(str(cur.get('weight', '0')))):
            by_code[code] = h
    deduped_hits = list(by_code.values())

    sev_rank = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
    agg_sev = max((h.get('severity', 'MEDIUM') for h in deduped_hits), key=lambda s: sev_rank.get(s, 2))
    agg_score = _norm_score(Decimal('50.0'), deduped_hits)
    reason_codes = sorted({h.get('reason_code') for h in deduped_hits if h.get('reason_code')})
    top_reason_code = max(deduped_hits, key=lambda x: Decimal(str(x.get('weight','0')))).get('reason_code')

    explain = {
        'transfer_id': t.id,
        'hit_count': len(deduped_hits),
        'reason_codes': reason_codes,
        'top_reason_code': top_reason_code,
        'hits': deduped_hits,
        'scoring': {
            'base': '50.0',
            'sum_weights': str(sum(Decimal(h.get('weight','0')) for h in deduped_hits)),
            'total': str(agg_score),
            'severity_factor': {k: str(v) for k, v in SEVERITY_FACTOR.items()},
        },
        'generated_at': datetime.now(timezone.utc).isoformat(),
    }
    reason = f"TM_HIT: {', '.join(reason_codes)}" if reason_codes else f"TM_HIT: {len(deduped_hits)} rule(s) matched"

    existing = db.query(Alert).filter(Alert.event_type == 'TRANSFER_SETTLED', Alert.transfer_id == t.id).first()
    if existing:
        existing.score = agg_score
        existing.severity = agg_sev
        existing.reason = reason
        existing.explain_json = explain
        existing.updated_at = datetime.now(timezone.utc)
        db.commit(); db.refresh(existing)
        return [existing]

    al = Alert(
        id=uid(),
        event_type='TRANSFER_SETTLED',
        entity_id=t.id,
        customer_id=customer_id,
        account_id=t.from_account_id,
        transfer_id=t.id,
        score=agg_score,
        severity=agg_sev,
        status='NEW',
        reason=reason,
        explain_json=explain,
    )
    db.add(al)
    db.commit(); db.refresh(al)
    return [al]


ALLOWED_TRANSITIONS = {
    'NEW': {'ACK', 'IN_REVIEW', 'CLOSED'},
    'IN_REVIEW': {'ACK', 'ESCALATED', 'CLOSED'},
    'ACK': {'ESCALATED', 'CLOSED'},
    'ESCALATED': {'CLOSED'},
    'CLOSED': set(),
}


def transition_alert(db: Session, alert_id: str, to_status: str, changed_by_user_id: str | None = None, note: str | None = None):
    al = db.get(Alert, alert_id)
    if not al:
        return None
    from_status = al.status
    to_status = to_status.upper()
    if to_status not in ALLOWED_TRANSITIONS.get(from_status, set()):
        return {'error': f'Invalid transition {from_status} -> {to_status}'}

    al.status = to_status
    al.updated_at = datetime.now(timezone.utc)
    db.add(AlertHistory(
        id=uid(),
        alert_id=al.id,
        from_status=from_status,
        to_status=to_status,
        changed_by_user_id=changed_by_user_id,
        note=note,
    ))
    db.commit(); db.refresh(al)
    try:
        alert_transitions_total.labels(from_status=from_status, to_status=to_status).inc()
    except Exception:
        pass
    return al
