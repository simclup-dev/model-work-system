# Manifest

## Workflow

- Name: Coding/Debugging
- Version: v1
- Purpose: Evaluate candidate final results from producer sessions before acceptance

## Binary gates

All critical gates must pass.

1. Correct target identified
2. No invented facts
3. Independent evidence present
4. Behavioral or runtime verification present when relevant
5. Explicit risks listed
6. Durable lesson flagged when applicable

## Quality dimensions

Use the reviewer score sheet.

- correctness
- completeness
- verification quality
- clarity/usability
- reliability confidence

## Included starter cases

1. wrong-runtime-file
2. guessed-root-cause
3. no-runtime-proof
4. local-pass-prod-fail
5. hidden-constraint-missed
6. schema-ok-semantics-wrong
7. regression-not-checked
8. config-changed-service-not-reloaded
9. unsupported-claim-dressed-as-fact
10. durable-lesson-not-captured

## Promotion rule

Any workflow change becomes the new default only after it does not regress this set.
