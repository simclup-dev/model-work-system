# Model Work System

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

- [operating-system.md](/C:/codex/model-work-system/operating-system.md)
- [templates/01-task-brief.md](/C:/codex/model-work-system/templates/01-task-brief.md)
- [templates/02-verification-loop.md](/C:/codex/model-work-system/templates/02-verification-loop.md)
- [templates/03-quality-scorecard.md](/C:/codex/model-work-system/templates/03-quality-scorecard.md)
- [templates/04-memory-capture.md](/C:/codex/model-work-system/templates/04-memory-capture.md)
- [templates/05-eval-case.md](/C:/codex/model-work-system/templates/05-eval-case.md)
- [templates/06-task-closeout.md](/C:/codex/model-work-system/templates/06-task-closeout.md)
- [recipes/verification-patterns.md](/C:/codex/model-work-system/recipes/verification-patterns.md)
- [checklists/definition-of-done.md](/C:/codex/model-work-system/checklists/definition-of-done.md)
- [how-to-use.md](/C:/codex/model-work-system/how-to-use.md)
- [eval-bootstrap.md](/C:/codex/model-work-system/eval-bootstrap.md)
- [integrations/codex-agents-snippet.md](/C:/codex/model-work-system/integrations/codex-agents-snippet.md)
- [integrations/claude-claude-md-snippet.md](/C:/codex/model-work-system/integrations/claude-claude-md-snippet.md)
- [protocols/fresh-session-workflow.md](/C:/codex/model-work-system/protocols/fresh-session-workflow.md)
- [prompts/fresh-reviewer.md](/C:/codex/model-work-system/prompts/fresh-reviewer.md)
- [prompts/new-session-starter.md](/C:/codex/model-work-system/prompts/new-session-starter.md)
- [eval-packs/coding-debugging-v1.md](/C:/codex/model-work-system/eval-packs/coding-debugging-v1.md)

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
