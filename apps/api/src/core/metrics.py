
from prometheus_client import Counter, Gauge, Histogram

transfers_total = Counter('corebank_transfers_total', 'Total transfers by status', labelnames=['status'])
alerts_total = Counter('corebank_alerts_total', 'Total alerts created')
sla_breaches_total = Counter('corebank_sla_breaches_total', 'Total SLA breaches detected')

notifications_total = Counter('corebank_notifications_total', 'Total notifications emitted', labelnames=['channel','status'])
alert_transitions_total = Counter('corebank_alert_transitions_total', 'Total alert status transitions', labelnames=['from_status','to_status'])

outbox_lag_seconds = Gauge('corebank_outbox_lag_seconds', 'Outbox lag seconds')
posting_latency = Histogram('corebank_posting_latency_seconds', 'Posting latency seconds', buckets=(0.01,0.05,0.1,0.25,0.5,1,2,5))
