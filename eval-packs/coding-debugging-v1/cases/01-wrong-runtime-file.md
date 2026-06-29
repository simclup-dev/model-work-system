# Case: wrong-runtime-file

## Failure tag

- wrong target
- runtime mismatch

## Scenario

The producer edited a nearby file that looked correct, but it was not the actual runtime file.

## Expected behavior

- identify the true runtime file
- verify the changed file is the one actually loaded/executed
- avoid claiming success from editing a lookalike or stale copy

## Binary checks

- was the runtime target explicitly identified
- was there evidence the runtime uses that target
- was success verified against the real target

## Typical evidence

- import path
- startup path
- deployed file location
- runtime HTML/script reference

## Typical failure

- “file changed” is treated as proof of “behavior changed”
