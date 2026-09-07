# Brief: fresh review before publication

**Role:** you are the fresh reviewer under this repository's own operating rule — the
producer loop is finished, a candidate result exists, and you are seeing it with a clean
head. You did not build any of it.

**Repository:** this repository (git). Read what you need.

---

## Objective

Decide whether this repository is ready to be published publicly on GitHub as evidence of
engineering judgement, and say what must change first.

The author is applying for **manual QA trainee** positions at Ukrainian IT companies. He
does not write code himself; he directs AI agents, sets boundaries, verifies results and
accepts them. This repository is the methodology he uses daily. It will be read by a QA
team lead or a recruiter who has roughly two minutes.

## Current state

- The five-stage loop (Brief → Execute → Verify → Measure → Capture) is documented in
  `operating-system.md`, `how-to-use.md`, `reviewer-score-sheet.md`.
- `eval-packs/coding-debugging-v1/` holds 15 failure-mode cases, 5 of them derived from
  real incidents.
- **New, not yet reviewed by anyone:** `evals/runner.py` — a harness that feeds each case
  scenario to a producer model and has a *different provider's* model score the answer
  against the case's binary checks. Results land in `evals/results/*.json`.
- **New, not yet reviewed by anyone:** `examples/bug-report-word-highlight-sync.md` — a
  worked defect report on a real product (an audiobook reader), built from that project's
  actual commit history.

## Known problems, already identified — do not spend effort re-finding these

1. `Measure` was declared but never demonstrated; the harness above is the first attempt
   to close that.
2. `SYNC.md` and `git-sync-plan.md` expose home infrastructure and a personal username —
   scheduled for deletion before publication.
3. Case files under `eval-packs/*/cases/` name real private services and paths —
   scheduled for anonymisation.
4. Several markdown links use absolute `/C:/codex/...` paths and will 404 on GitHub.
5. The README does not explain in 30 seconds what this is, and never uses QA vocabulary
   (test case, acceptance criteria, regression suite, defect).

## What the review must answer

1. **Is the harness sound?** Read `evals/runner.py` as a measurement instrument, not as
   code style. Does the number it produces mean what it claims? Where can it lie —
   prompt leakage between case and judge, judge bias, unstable parsing, throttling
   recorded as failure, cases whose sections do not parse?
2. **Is the worked example honest?** Read `examples/bug-report-word-highlight-sync.md`
   against the commits it cites. Does it overclaim? Does it present after-the-fact
   reconstruction as if it were measurement?
3. **Does the repository read as QA evidence to someone who does not know the author?**
   Or does it read as notes about prompting models?
4. **What is missing that a QA reader would expect to see** and would notice the absence
   of?

## Constraints

- Do not fix anything. Report only.
- Ground each finding in a quoted line or a file path. A finding without a location is
  not usable.
- If something is genuinely strong, say so with the same specificity — the author needs
  to know what to keep, not only what to cut.
- Rank findings: blocks publication / should fix before publication / optional.
- Keep it under 900 words.

## Success criteria

A list the author can act on directly, where every item names the file it applies to, and
where nothing recommended is cosmetic.
