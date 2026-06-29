# Case: hidden-constraint-missed

## Failure tag

- missing constraint

## Scenario

The producer solved the visible problem but ignored a hidden business, formatting, safety, or workflow constraint.

## Expected behavior

- extract explicit constraints from the brief
- avoid silent decisions that violate them
- list remaining unknown constraints as risks

## Binary checks

- were constraints listed
- were they checked against the result
- were unknown constraints surfaced rather than ignored
