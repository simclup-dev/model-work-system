# Case: guessed-root-cause

## Failure tag

- guessed root cause

## Scenario

The producer locked onto a plausible explanation too early and built the fix around it.

## Expected behavior

- separate symptom from root cause
- verify the root cause with independent signals
- avoid declaring root cause from intuition alone

## Binary checks

- was the root cause stated clearly
- was there evidence for it
- was at least one alternative ruled out

## Typical evidence

- logs
- config inspection
- version check
- diff between expected and actual runtime state
