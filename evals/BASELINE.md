# Baseline — coding-debugging-v1

The repository asked for this and never had it: *"If you do not have a baseline, every
improvement is imaginary"* (`eval-bootstrap.md`). First one recorded 2026-09-05.

## Run

| | |
|---|---|
| Pack | `coding-debugging-v1`, manifest selection (10 cases) |
| Producer | `gemini/gemini-3.1-flash-lite`, temperature 0.3 |
| Judge | `groq/openai/gpt-oss-120b`, temperature 0, independent provider |
| Repetitions | 3 |
| Verdict | **COMPLETE** — 30 rows ok, 0 invalid, 0 errored |
| Raw | `evals/results/coding-debugging-v1-20260905T201109Z.json` |

## Result

| Metric | Value |
|---|---|
| Checks passed | **37 / 105 (35.2%)** |
| Traps entered | **10 / 30 runs** |
| Per-repetition pass rate | 34.3% · 34.3% · 37.1% |
| Spread | 2.8 pp (stdev 1.6 pp) |

The spread is what makes the number usable: a single run of a non-deterministic producer
is not a measurement, and without repetitions a 3-point swing would read as progress.
**Any claimed improvement below ~3 pp is inside the noise of this setup.**

## What this number is, and is not

It is a **reasoning/policy** score: given a written scenario, does the model's *stated*
reasoning satisfy the case's binary checks. The producer executes nothing, so a check
like "was the database backed up" scores whether the answer says it — not whether it
happened. This is not a measurement of runtime quality, and the harness records that
caveat in every result file.

It is also **not a measure of this repository's own method**: the producer is a small
model answering cold, with no brief, no verification loop and no reviewer. It is a
floor — what the failure patterns catch when nothing is done to avoid them.

## Promotion rule

Per `manifest.md`, a workflow change becomes the new default only if it does not regress
this set. That rule is now checkable: re-run `python3 evals/runner.py --repeat 3` and
compare. A run whose verdict is not `COMPLETE` may not be quoted as a baseline —
the harness exits non-zero and says so.

## Known limits

- Scenarios state the mechanism of the trap in the case text, so part of what is scored
  is whether the model follows an obvious hint. There are no holdout cases, no negative
  controls, and no human-labelled calibration of the judge.
- 5 case files in `cases/` are not named by the manifest and were not scored; the runner
  reports them rather than silently including them.
- One judge, one producer. Neither is the model stack this method is normally run with,
  so this baseline does not describe that stack.
