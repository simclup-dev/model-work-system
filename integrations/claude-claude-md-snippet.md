# Claude Code `CLAUDE.md` Snippet

Add a section like this to your Claude Code `CLAUDE.md`.

```md
## Model Work System

For all non-trivial tasks, use the `Model Work System`.

Required workflow:

1. Build a short task brief before execution.
2. Keep context scoped; start new chats for new tasks by default.
3. Before finalizing, list critical claims.
4. Verify those claims using independent evidence.
5. Use explicit pass/fail gates and scorecards for recurring workflows.
6. For important tasks, produce a candidate final result and submit it to a fresh strong reviewer chat.
7. If a durable lesson or repeated failure appears, write it to memory/runbook before considering the task done.

Hard rules:

- No important task is done without evidence.
- Model explanation is not proof.
- Unknowns must be marked explicitly.
- Silent-failure tasks require independent behavioral verification.
- For important tasks, the reviewer should be a separate fresh session that did not see the hidden production process.
- Workflow changes must beat the eval baseline before becoming the new default.
- Durable lessons must be captured, not merely fixed locally.

Completion format for important tasks:

1. Output
2. Critical claims
3. Evidence
4. Remaining risks
5. Memory result
6. Final status

Fresh-chat policy:

- Use a fresh chat by default for each new meaningful task.
- Keep old chats only when prior task state is essential.
- Use a separate fresh strong reviewer/evaluator chat when judging quality or correctness.
```
