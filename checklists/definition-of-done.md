# Definition Of Done

A non-trivial model-assisted task is done only if:

- the deliverable exists
- critical claims were verified with independent evidence
- quality gates passed
- known risks or unknowns were stated
- repeated or durable lessons were captured

Add these task-end questions:

1. What exactly did we verify?
2. What evidence do we have?
3. What could still be wrong?
4. Did this reveal a reusable lesson?
5. If yes, where was that lesson stored?

Mandatory rule:

- If a durable lesson appeared and was not captured, the task is not done.

---

## Pre-flight gate: before any external call or long run

Precedence, stated so it cannot be resolved by convenience: **cost decides how much to
run. It never decides whether the run is observable.** When the cheaper path is the less
verifiable one, verifiability wins.

Four questions. "Probably yes" counts as no.

1. **Was the model / endpoint name verified in THIS session?**
   Not recalled. Model names go stale between sessions; listing them costs one call.
2. **Can the output be polled WHILE the run is in progress?**
   Never pipe a long run through `tail`, `head` or `grep` — the buffer releases nothing
   until the end, so a hung run and a working run look identical. Write to a log file and
   read it separately.
3. **Do partial results survive a kill?**
   Write after every unit and carry an explicit `complete` flag. Otherwise a killed run
   yields nothing, and — worse — a partial result reads as a full one.
4. **Is a transport failure distinguishable from an answer?**
   Retry 429 and 5xx; never record them as results. An infrastructure failure written
   into a measurement produces a quietly understated number. If a 429 names a spent
   quota, retrying cannot clear it — that is a daily cap, not a burst.

Each of the four, when skipped, produces a **quietly wrong number** rather than a visible
error. That is why this is a gate and not advice.

Provenance: all four were violated in a single session on 2026-09-05 while building the
eval harness in `evals/` — the tool meant to catch exactly this class of mistake.
