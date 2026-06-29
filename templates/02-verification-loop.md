# Verification Loop

## Step 1. List model claims

Write the exact claims that matter:

- claim 1
- claim 2
- claim 3

If a claim cannot be tested, confidence stays low.

## Step 2. Choose independent signals

For each claim, define at least one independent signal.

| Claim | Independent signal | Evidence type | Pass condition |
|---|---|---|---|
| claim 1 | test, log, UI, API, doc | exact output | what must be true |
| claim 2 | test, log, UI, API, doc | exact output | what must be true |

## Step 3. Run checks

For each signal:

- run the check
- record the raw outcome
- mark `pass`, `fail`, or `unknown`

## Step 4. Resolve uncertainty

If a check returns `unknown`:

- do not upgrade it to `pass`
- run a stronger check
- or report reduced confidence

## Step 5. Close only with evidence

A task can be closed only when:

- critical claims have `pass`
- no critical claim remains `unknown`
- known failures are explicitly listed

## Anti-patterns

- using the model's own explanation as proof
- checking only one weak signal
- verifying a side effect instead of the core requirement
- skipping verification because the output "looks right"
- accepting "probably" on high-impact tasks

## Strong patterns

- test plus runtime signal
- UI check plus log check
- schema validation plus semantic spot-check
- diff check plus behavior check
