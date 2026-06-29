# Verification Patterns

Use these patterns instead of vague "looks good" review.

## Pattern 1. File change -> behavior change

Use when code or config changed.

- verify the diff is present
- verify the target file is the real runtime file
- run the behavior check
- inspect logs or UI for the changed behavior

## Pattern 2. Structured output -> schema + semantics

Use when the model returns JSON, YAML, CSV, or other formatted output.

- validate the schema mechanically
- spot-check semantic correctness
- confirm required fields are populated

Schema validity alone is not enough.

## Pattern 3. Search/research -> source + claim table

Use when the model produces factual claims.

- list the important claims
- attach a source to each claim
- mark unsupported claims as fail or unknown

## Pattern 4. UI task -> visible state + underlying signal

Use when a UI appears correct but may lie.

- verify the visible UI state
- verify one deeper signal such as log, network result, saved state, or DB state

## Pattern 5. Deploy/fix -> runtime proof

Use after deploys, restarts, env changes, or production fixes.

- confirm the changed artifact reached the real runtime
- confirm the service restarted or reloaded if needed
- confirm the expected behavior in runtime, not only locally

## Pattern 6. Memory/rules update -> retrieval proof

Use for durable lessons.

- write the rule or note
- confirm it is in the intended place
- confirm the retrieval keywords are obvious enough for future discovery

## Escalation rules

Stop and strengthen verification if:

- evidence comes only from the same model that made the claim
- the only proof is visual confidence
- the task can fail silently
- the behavior depends on deployment or runtime state
- the result is expensive to be wrong about
