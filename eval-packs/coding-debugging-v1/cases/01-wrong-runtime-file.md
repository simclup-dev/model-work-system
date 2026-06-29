# Case: wrong-runtime-file

## Failure tag

- wrong target
- runtime mismatch
- duplicate file trap

## Scenario

Real pattern from the Storyteller reader work:

The producer edited a nearby JavaScript file that looked correct, but it was not the actual runtime file.

Concrete shape of the trap:

- `reader/app.js` exists and looks relevant
- the live browser shell imports `reader/js/app.js` from `reader.html`
- a change in the wrong file can look convincing in git diff but never affect runtime

## Expected behavior

- identify the true runtime file before patching
- verify the changed file is the one actually loaded or executed
- avoid claiming success from editing a lookalike or stale copy
- prove the changed module is the one the runtime actually uses

## Binary checks

- was the runtime target explicitly identified
- was there evidence the runtime uses that target
- was success verified against the real target
- if there was a duplicate file nearby, was it ruled out explicitly

## Typical evidence

- runtime HTML or script reference
- import path
- startup path
- deployed file location
- browser-loaded module path

## Typical failure

- "file changed" is treated as proof of "behavior changed"
- the nearest similarly named file is assumed to be the live one
