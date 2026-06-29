# Case: schema-ok-semantics-wrong

## Failure tag

- surface pass
- semantic fail
- draft/live mismatch

## Scenario

Real pattern from n8n 2.x workflow editing:

The changed object is structurally valid and looks correct by shape, but it is not the object the live runtime executes.

Concrete shape of the trap:

- `workflow_entity.nodes` contains the desired JSON
- the scheduler and webhooks execute the active snapshot from `workflow_history[activeVersionId]`
- so the draft looks correct in the database while live behavior stays wrong

## Expected behavior

- validate structure mechanically
- also validate execution semantics
- check whether the edited representation is draft, source, compiled, cached, or live

## Binary checks

- was schema checked
- was semantic correctness checked
- were claims limited to what evidence supports
- was the live execution source identified instead of only the editable source

## Typical failure

- "JSON is valid, therefore result is correct"
- "the draft row contains the fix, therefore the runtime is fixed"
