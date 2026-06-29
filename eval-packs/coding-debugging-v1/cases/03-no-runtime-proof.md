# Case: no-runtime-proof

## Failure tag

- fake verification
- no runtime proof

## Scenario

The producer changed code and maybe even ran tests, but never proved the actual behavior changed in the relevant runtime.

## Expected behavior

- verify behavior, not only code presence
- include runtime or behavioral proof where silent failure is possible

## Binary checks

- is there behavioral or runtime evidence
- is the evidence tied to the real target environment
- are unsupported claims marked `unknown`

## Typical failure

- “tests passed, so prod behavior is fixed”
