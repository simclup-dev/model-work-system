# Fresh Session Workflow

This is the default operating mode for both Codex and Claude Code.

## Rule

Every new non-trivial task starts in a fresh window/thread/chat by default.

Use an old session only if at least one is true:

- the task continues the same unfinished implementation
- the same hidden context is expensive to rebuild
- there is active state in tools or files that must be preserved

## Why

Fresh sessions reduce:

- stale context
- inherited bad assumptions
- accidental drift from earlier goals
- fake confidence based on old discussion

## Standard start sequence

1. Open a new window or thread.
2. Paste a short task brief.
3. Attach or reference the needed local artifacts only.
4. Require the `Model Work System`.
5. Require final `Claims -> Evidence -> Risks -> Memory` closeout.

## Standard end sequence

1. Check whether critical claims were verified.
2. Score the run if the workflow is recurring.
3. Decide whether a durable lesson exists.
4. Capture the lesson if needed.
5. Close the thread.

## Reviewer split

For important outputs, use two roles in sequence:

- `Producer`: does the task, iterates, tests, verifies, and reaches a candidate final result
- `Reviewer`: fresh strong agent with no hidden production context

The reviewer is not part of the main production loop.

The reviewer is invoked only after the producer has:

- finished the implementation
- run its own verification loop
- prepared evidence
- produced a candidate final result

The reviewer should judge only from:

- the task brief
- the produced artifacts
- the scorecard
- the verification evidence

Not from trust in the producer's narrative and not from the hidden process history.

## Reviewer decision rule

If the reviewer result is satisfactory:

- accept the result
- capture durable lessons into memory if needed
- close the task

If the reviewer result is not satisfactory:

- reopen the producer loop
- fix the issues
- rerun verification
- submit again to a fresh reviewer
