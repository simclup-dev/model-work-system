# Operating System

## 1. Brief

Before execution, make the model explicit about:

- the real goal
- current state
- constraints
- success criteria
- unknowns
- what it must not assume

Minimum output from this stage:

- one-sentence objective
- concrete deliverable
- constraints list
- open questions or explicit assumptions

If the task starts without this, the model fills gaps with guesses.

## 2. Execute

Execution should stay scoped.

Rules:

- one task per thread/session when possible
- split broad work into smaller units
- keep reference context close to the task
- avoid dragging long stale history forward by default

Use fresh context for:

- new bug
- new feature
- new repo area
- new stakeholder or new acceptance criteria

## 3. Verify

Verification is not “read the answer and vibe-check it.”

Verification means:

- identify what claims the model made
- test those claims with independent signals
- record evidence
- fail the task if evidence is missing

Good independent signals:

- tests
- runtime behavior
- logs
- exact file diffs
- API response
- database state
- UI state
- second source or documentation

Weak signals:

- model explanation alone
- “it should work”
- “I checked it mentally”
- same model rephrasing the same answer

## 4. Measure

Measurement turns “seems better” into “is better.”

For recurring tasks, define:

- binary gates
- quality dimensions
- evidence needed
- pass threshold

Examples of binary gates:

- tests pass
- output schema valid
- no invented facts
- required files updated
- deployment verified
- memory note written

Examples of quality dimensions:

- correctness
- completeness
- constraint adherence
- formatting fidelity
- tone or UX quality
- latency or effort

## 5. Capture

When a failure or lesson is durable, push it into memory.

Capture when:

- the model repeated a mistake
- a hidden constraint mattered
- verification exposed a tricky failure mode
- a deploy/debug workflow had a trap
- a better rubric or checklist emerged

Do not only fix the instance.
Fix the system that allowed the instance.

## 6. Evals

Once a failure pattern repeats, promote it into an eval case.

An eval case needs:

- input
- expected behavior
- scoring criteria
- failure mode tag

The best eval sets come from real failures, not imagined examples.

## Operating policy

This system is healthy only if these statements stay true:

- the brief is short but sufficient
- verification is cheaper than failure
- measurement is stable across runs
- memory stays curated rather than bloated
- repeated mistakes become rules or evals
