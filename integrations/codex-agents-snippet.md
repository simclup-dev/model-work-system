# Codex `AGENTS.md` Snippet

Add a section like this to your Codex `AGENTS.md`.

```md
## Model Work System

For all non-trivial tasks, operate under the `Model Work System`.

Required workflow:

1. Start from a short task brief.
2. Keep work scoped; prefer a fresh thread/session for a new task.
3. Before finalizing, list critical claims.
4. Verify critical claims with independent evidence.
5. Score recurring workflows with explicit gates/criteria.
6. For important tasks, produce a candidate final result and send it to a fresh strong reviewer agent/session.
7. If a durable lesson appears, capture it into memory/runbook before the task is done.

Hard rules:

- Never mark an important task done without verification evidence.
- Never treat model confidence as evidence.
- If a claim is not verified, mark it `unknown` instead of implying success.
- If a task can fail silently, verification must include an independent runtime or behavioral signal.
- For important tasks, producer and reviewer should be separate fresh sessions; the reviewer should not inherit the hidden process context.
- If a recurring workflow changes, compare it against the current eval baseline before adopting the change.
- If a repeated or durable failure is found, update memory/runbook as part of done.

Completion format for important tasks:

1. Output
2. Critical claims
3. Evidence
4. Remaining risks
5. Memory result
6. Final status

Fresh-session policy:

- Default to a fresh thread/window for each new non-trivial task.
- Do not continue old threads by default unless prior context is truly needed.
- For review/evaluation, use a separate fresh strong agent/thread that did not produce the original result and sees only the brief, artifacts, evidence, and scorecard.
```
