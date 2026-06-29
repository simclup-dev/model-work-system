# Eval Bootstrap

Start with one workflow only.

Do not build a giant eval system first.

## Best first targets

Choose one:

- coding/debugging
- research/fact synthesis
- repeated ops/deploy work

## Step 1. Collect real failures

Gather 10 to 20 examples where the model:

- invented a fact
- missed a constraint
- changed the wrong file
- claimed success without proof
- produced the wrong format
- forgot a known rule

Use real examples from your work, not synthetic ones.

## Step 2. Turn each failure into an eval case

For each case record:

- reduced input
- expected behavior
- binary gates
- failure tag

Use [templates/05-eval-case.md](/C:/codex/model-work-system/templates/05-eval-case.md).

## Step 3. Define the first scorecard

For the first workflow, keep it simple.

Suggested binary gates:

- no invented facts
- constraints respected
- required output exists
- verification present
- memory updated if durable lesson found

Suggested quality dimensions:

- correctness
- completeness
- usability

## Step 4. Establish a baseline

Run the current workflow and score it before changing anything.

If you do not have a baseline, every improvement is imaginary.

## Step 5. Change one variable at a time

Only one:

- prompt/instructions
- model choice
- tool usage pattern
- task decomposition
- verification pattern

Then rerun the eval set.

## Step 6. Promote stable wins

When something reliably improves results:

- move it into rules
- move it into templates
- move it into memory if durable

## First judge model policy

If you use a judge model:

- keep criteria binary where possible
- calibrate against human-labeled examples
- never let the judge be the only evidence on factual or runtime claims

## Minimal weekly loop

1. add 1 to 3 new real failure cases
2. rerun the active eval set
3. compare to baseline
4. promote one stable rule
5. prune one stale rule
