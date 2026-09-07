# Model Work System

[![tests](https://github.com/simclup-dev/model-work-system/actions/workflows/tests.yml/badge.svg)](https://github.com/simclup-dev/model-work-system/actions/workflows/tests.yml)

A working method for getting verified results out of AI models, and for knowing when
you have not. I use it daily to run and check work I direct rather than type: I set the
objective and the boundaries, the model produces, and nothing is accepted until an
independent signal says it holds. The failure cases in `eval-packs/` are not
hypotheticals — each one is a real incident from my own systems that this method now
catches.

**If you work in QA, the vocabulary maps directly:**

| Here | Usual QA term |
|---|---|
| `Brief` | acceptance criteria |
| `Verify` | test execution + evidence |
| `Measure` | exit criteria / regression suite |
| `Capture` | defect knowledge base |
| eval case | test case with an expected result |
| `failure tag` | defect category |
| `unknown` verdict | not tested — never counted as a pass |

## Tests

The harness is the thing that produces the number, so it is tested. `python -m pytest`
runs 82 tests on every push (Python 3.11-3.13, `.github/workflows/tests.yml`); they use
no network and no API keys, and the CI job is given none, so a test that reaches a paid
endpoint fails there.

Two kinds:

- **`tests/test_runner.py`** pins the invariants that decide what the reported number
  means: an `unknown` verdict is never counted as a pass, rows that errored stay in the
  denominator so a killed run cannot outscore a finished one, a short reply from the
  judge is rejected instead of silently shrinking the denominator, only a run with every
  row ok may call itself `COMPLETE`, and a 429/5xx is retried as transport rather than
  recorded as an answer - except a 429 naming a spent quota, which is a daily cap and is
  not waited out.
- **`tests/test_pack_integrity.py`** reads the pack and the published baseline and makes
  them agree: every manifest name resolves to a file, every case still parses, the case
  hashes stored in the baseline run still match the case text on disk, and the figures
  quoted in `evals/BASELINE.md` are recomputed from the raw result file it cites.

The suite was checked against nine deliberately introduced defects - five in the runner
(dropping errored rows from the denominator, skipping the judge-reply length check,
retrying a spent quota, counting `unknown` as a pass, matching a section name as a
regex) and four in the data (a drifted figure in the baseline, a manifest name with no
file, a case edited after the baseline run, a case stripped of its checks). All nine
were caught. A suite that has never failed has not been shown to work.

Worth reading first: [`examples/bug-report-hourly-aggregation-window.md`](examples/bug-report-hourly-aggregation-window.md)
— a filed defect report in the standard form: a scheduled job that logged
`executed successfully` every hour for 104 days while writing nothing, with the
reproduction, the root cause, and the production verification. Then
[`examples/bug-report-word-highlight-sync.md`](examples/bug-report-word-highlight-sync.md)
— an *analysis* of a messy report, including the part where the report's own
acceptance gate fails, and [`checklists/definition-of-done.md`](checklists/definition-of-done.md).

This is a practical operating system for high-volume work with AI models.

Important operating rule:

- The main working agent does the iterative producer loop.
- A separate fresh strong reviewer is invoked only after a candidate final result exists.

It is built around five rules:

1. Give the model the right context at the start.
2. Control context instead of letting one chat grow forever.
3. Require verification instead of trusting confident output.
4. Measure quality with explicit criteria.
5. Capture durable lessons so the same mistakes do not repeat.

## Core loop

Use this loop for every meaningful task:

1. `Brief`
2. `Execute`
3. `Verify`
4. `Measure`
5. `Capture`

If one stage is weak, the later stages become noisy:

- bad brief -> bad assumptions
- bad verification -> fake confidence
- bad measurement -> random "improvements"
- no capture -> repeated mistakes

## Files

- [operating-system.md](operating-system.md)
- [templates/01-task-brief.md](templates/01-task-brief.md)
- [templates/02-verification-loop.md](templates/02-verification-loop.md)
- [templates/03-quality-scorecard.md](templates/03-quality-scorecard.md)
- [templates/04-memory-capture.md](templates/04-memory-capture.md)
- [templates/05-eval-case.md](templates/05-eval-case.md)
- [templates/06-task-closeout.md](templates/06-task-closeout.md)
- [recipes/verification-patterns.md](recipes/verification-patterns.md)
- [checklists/definition-of-done.md](checklists/definition-of-done.md)
- [how-to-use.md](how-to-use.md)
- [eval-bootstrap.md](eval-bootstrap.md)
- [integrations/codex-agents-snippet.md](integrations/codex-agents-snippet.md)
- [integrations/claude-claude-md-snippet.md](integrations/claude-claude-md-snippet.md)
- [protocols/fresh-session-workflow.md](protocols/fresh-session-workflow.md)
- [prompts/fresh-reviewer.md](prompts/fresh-reviewer.md)
- [prompts/new-session-starter.md](prompts/new-session-starter.md)
- [eval-packs/coding-debugging-v1.md](eval-packs/coding-debugging-v1.md)

## Rollout order

Do not adopt everything at once.

1. Start using the task brief on every non-trivial task.
2. Add the verification loop to any task that can fail silently.
3. Add the quality scorecard to recurring tasks.
4. Make memory capture mandatory in the definition of done.
5. Turn recurring failures into eval cases.

## Non-negotiables

- No important task is "done" without evidence.
- No recurring workflow is "good" without a scorecard.
- No repeated failure is acceptable without being captured into memory or rules.
- If verification is weak, confidence must stay low.
