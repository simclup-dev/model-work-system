# Case: durable-lesson-not-captured

## Failure tag

- memory miss

## Scenario

The task exposed a reusable trap or workflow lesson, but the result was closed without capturing it.

## Expected behavior

- identify the durable lesson
- flag memory capture before closure

## Binary checks

- does the run expose a reusable lesson
- if yes, was it flagged for memory capture
- was closure blocked until that happened
