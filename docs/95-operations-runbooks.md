# 95 - Operations Runbooks

## Source stale

1. Check policy review has not expired.
2. Check network and endpoint manually.
3. Inspect last ingestion run and HTTP status.
4. Compare fixture/schema with current documented response.
5. Disable connector if source changed.
6. Use manual capture until updated and tested.

## Worker down

1. `make status` and inspect worker logs.
2. Confirm Redis/Postgres health.
3. Restart worker only.
4. Run reconciliation.
5. Confirm queue drains without duplicates.

## LLM budget reached

1. Confirm budget ledger and model usage.
2. Keep ingestion/rules running.
3. Queue jobs in `READY_TO_SCORE`.
4. Raise budget only after review, or switch to manual/fake/local mode.

## Unsupported claim detected

1. Block proposal.
2. Inspect evidence links and claim ledger.
3. Correct evidence classification or prompt.
4. Add regression evaluation.
5. Regenerate as a new revision.

## Submission unknown

1. Do not retry.
2. Check platform manually or query official receipt endpoint.
3. Mark submitted/cancelled only with evidence.
4. Record incident.

## Backup failed

1. Stop destructive updates.
2. Check disk space, permissions, encryption key availability.
3. Run backup manually.
4. Verify archive and test restore when resolved.
