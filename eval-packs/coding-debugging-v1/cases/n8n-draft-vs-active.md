# Eval Case: n8n draft vs active version

## Failure tag

- wrong-runtime-file
- config-changed-service-not-reloaded

## Input

Task: fix n8n workflow behavior (e.g. treadmill reminders not firing).
Model edits `workflow_entity.nodes` in SQLite directly.

## Expected behavior

- Must identify that n8n 2.x executes the **active version** from `workflow_history[activeVersionId]`, NOT the draft in `workflow_entity.nodes`
- Must either update `workflow_history` or publish via REST API
- Must backup database before editing
- Must stop n8n before editing SQLite

## Binary checks

- Did the model identify activeVersionId as the real runtime source? pass/fail
- Did the model edit workflow_history or publish via API? pass/fail
- Was the database backed up? pass/fail
- Was n8n stopped before edit? pass/fail

## Known trap

Editing `workflow_entity.nodes` looks correct — the JSON changes, the diff is clean, but the scheduler/webhook continues executing the old snapshot from `workflow_history`. This is a silent failure: no error, no log, just old behavior continues.

## Human reference

The correct flow: stop n8n → backup DB → update `workflow_history` WHERE `versionId = activeVersionId` → start n8n. Or: use n8n REST API to publish the workflow.

## Notes

This caused weeks of "reminders not working" debugging. The root cause was invisible because the draft looked correct.
