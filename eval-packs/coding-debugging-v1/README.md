# Coding/Debugging Eval Dataset v1

This is the first practical eval dataset for the `Model Work System`.

It is designed for:

- bug fixing
- code editing
- config changes
- debugging
- deploy validation

## Goal

This dataset is not trying to score everything.

It is trying to catch the most expensive early failure modes:

- wrong target
- invented facts
- fake verification
- missing runtime proof
- uncaptured durable lessons

## Structure

- [manifest.md](/C:/codex/model-work-system/eval-packs/coding-debugging-v1/manifest.md)
- [reviewer-runbook.md](/C:/codex/model-work-system/eval-packs/coding-debugging-v1/reviewer-runbook.md)
- `cases/` individual starter cases

## First use

1. Pick the real task you are about to run.
2. Check which starter cases are closest to that risk.
3. Use the score sheet and reviewer prompt after the producer has a candidate final result.
4. Add a new case whenever a real failure appears that is not covered here.

## Maintenance rule

When a case is no longer representative, replace it with a fresher real case.
