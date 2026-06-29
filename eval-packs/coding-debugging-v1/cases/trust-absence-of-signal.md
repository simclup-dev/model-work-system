# Eval Case: trusting absence of signal as proof

## Failure tag

- verification-miss
- no-runtime-proof

## Input

Task: debug why a service isn't working (e.g. n8n trigger not firing, companion reminders not arriving).
Model checks logs/executions, finds nothing, concludes "trigger didn't fire."

## Expected behavior

- Must not treat "no log entry" as "didn't execute" — n8n doesn't save empty success executions
- Must build an independent signal (heartbeat file, test trigger, curl endpoint)
- Must verify the actual runtime version/location of what's running

## Binary checks

- Did the model build an independent verification signal? pass/fail
- Did the model avoid concluding from absence alone? pass/fail
- Did the model verify the real runtime artifact (not just the source)? pass/fail

## Known trap

n8n doesn't store executions when `return []` produces empty output. "No execution row" ≠ "trigger didn't fire." Similarly, checking the wrong file/service (draft vs active, local vs remote copy) gives false absence.

## Human reference

Build a heartbeat: make the workflow write a timestamp file on every run. If the file updates, the trigger fires. Then debug the logic separately.

## Notes

This pattern recurred in: n8n treadmill debugging, companion reminder debugging, storyteller cache issues. The lesson: always verify with an independent positive signal, never trust absence.
