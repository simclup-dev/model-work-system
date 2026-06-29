# Case: regression-not-checked

## Failure tag

- regression risk

## Scenario

The immediate bug was fixed but adjacent behavior was never checked.

## Expected behavior

- identify what nearby behavior could regress
- verify at least the most likely regression surfaces

## Binary checks

- were adjacent risks named
- was at least one regression check run
- were untested regressions listed as risks
