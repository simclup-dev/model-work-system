# Coding And Debugging Eval Pack v1

This is the recommended first workflow to instrument.

## Scope

Use for:

- bug fixing
- code changes
- config changes
- refactors with behavioral risk
- local or remote debugging

## Binary gates

All must pass.

| Gate | Pass rule |
|---|---|
| Correct target | the real runtime file/service/component was identified |
| No invented facts | no fabricated file, log, API, runtime, or environment claims |
| Verification present | each critical claim has independent evidence |
| Behavior checked | the fix/change was verified in behavior, not just by diff |
| Risks stated | unresolved uncertainty is explicitly listed |
| Memory captured if needed | durable lesson recorded or marked not applicable |

## Quality dimensions

Score each 0-2.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Correctness | wrong or unproven | partly proven | clearly proven |
| Completeness | partial fix only | mostly handled | fully handled |
| Constraint adherence | constraints violated | minor drift | fully respected |
| Efficiency | wasteful/rework-heavy | acceptable | direct and economical |
| Debugging discipline | weak evidence | some evidence | strong independent verification |

## Critical claim patterns

Typical claims in this workflow:

- "I changed the correct file."
- "The bug root cause is X."
- "The new behavior works."
- "The change did not break Y."
- "The deploy/runtime picked up the new change."

## Required evidence patterns

Use at least one strong signal per critical claim.

- file diff
- test result
- runtime log
- process/service state
- exact output
- UI behavior
- database state
- config value in runtime

## First 10 eval cases to collect

Start by collecting real examples of:

1. wrong file edited
2. draft file edited instead of runtime file
3. root cause guessed too early
4. fix claimed without runtime verification
5. tests passed but behavior still wrong
6. behavior fixed locally but not in deploy/runtime
7. hidden constraint ignored
8. output format or contract broken
9. regression introduced elsewhere
10. durable lesson found but not captured

## Baseline policy

Before changing prompts or workflow:

1. run the current process on the eval set
2. score it
3. save that score as baseline

Then only change one variable at a time.
