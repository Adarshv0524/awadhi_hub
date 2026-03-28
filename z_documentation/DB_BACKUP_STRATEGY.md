# Database Backup Strategy

Last Updated: March 28, 2026
Scope: Production MySQL backing Awadhi New backend services.

## 1. Backup Objectives

- Guarantee recoverability for user submissions, moderation history, and canonical content.
- Keep Recovery Point Objective (RPO) <= 15 minutes.
- Keep Recovery Time Objective (RTO) <= 2 hours for full regional restore.

## 2. Backup Layers

- Full snapshot backup: daily at 02:00 UTC.
- Incremental binlog backup: every 15 minutes.
- Schema-only export: every deployment and before each migration.

## 3. Retention Policy

- Daily full backups retained for 35 days.
- Weekly full backups retained for 12 weeks.
- Monthly full backups retained for 12 months.
- Binlogs retained for 14 days.

## 4. Storage and Security

- Primary storage: object storage bucket with versioning enabled.
- Secondary copy: cross-region replication to disaster-recovery bucket.
- Encryption: AES-256 at rest and TLS in transit.
- Access: least-privilege IAM role limited to backup/restore pipeline.
- Key management: rotate encryption keys every 90 days.

## 5. Operational Procedure

1. Pre-backup checks: DB health, replication lag, free disk threshold.
2. Create consistent snapshot (`mysqldump --single-transaction` or snapshot API).
3. Capture binlog position and persist metadata manifest.
4. Upload artifacts and checksum files.
5. Verify backup integrity by checksum and restore smoke test.

## 6. Restore Procedure

1. Select target recovery timestamp.
2. Restore latest full backup before timestamp.
3. Apply binlogs up to target timestamp.
4. Run post-restore validation:
   - row counts for `users`, `submissions`, `doha_entries`, `poetry_nodes`
   - latest migration version check
   - `/health` and search endpoint smoke tests
5. Switch traffic after validation and run read/write canary.

## 7. Testing Cadence

- Weekly: automated restore to staging and smoke tests.
- Monthly: game-day restore drill with on-call + backend owners.
- Quarterly: regional failover simulation with rollback validation.

## 8. Ownership and Alerts

- Primary owner: Infrastructure team.
- Secondary owner: Backend platform team.
- Alerts: backup failure, checksum mismatch, restore test failure, replication lag > 10 minutes.

## 9. Migration Safety Rule

Before running Alembic migrations in production:

1. Trigger on-demand full backup.
2. Verify restore point creation.
3. Apply migration.
4. Record migration ID and backup artifact ID in deployment log.
