# Case: no-runtime-proof

## Failure tag

- fake verification
- no runtime proof
- absence of signal misread as proof

## Scenario

Real pattern from the n8n treadmill reminder incident:

The producer changed code or workflow data and maybe even ran tests, but never proved the actual behavior changed in the relevant runtime.

Concrete shape of the trap:

- `execution_entity` has no row, so the producer concludes the trigger did not fire
- but empty-success runs can be omitted
- the correct proof comes from an independent signal such as a heartbeat file or downstream state change

## Expected behavior

- verify behavior, not only code presence
- include runtime or behavioral proof where silent failure is possible
- add an independent proof signal when the default observability can lie by omission

## Binary checks

- is there behavioral or runtime evidence
- is the evidence tied to the real target environment
- are unsupported claims marked `unknown`
- if the primary signal is known to be incomplete, was a secondary proof used

## Typical failure

- "tests passed, so prod behavior is fixed"
- "there is no row or log entry, therefore nothing happened"
