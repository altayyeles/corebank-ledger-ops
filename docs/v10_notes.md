
# V10 Notes

## Dead-letter queue (DLQ) for notifications
- Notifications can end as `FAILED` when `attempt_count > max_attempts`.
- Added `/notifications/failed` to list DLQ.
- Added `/notifications/{id}/requeue` to reset and re-queue a FAILED notification.

## Fraud rule versioning + normalized scoring
- Added `fraud_rules.version` (auto-increment on meaningful updates).
- Alert hits include `rule_version`.
- Score is normalized with severity multipliers and clamped to 0..100.

## Graph UX
- Alert node panel includes a **Create Case** action (creates case with 1h SLA).
