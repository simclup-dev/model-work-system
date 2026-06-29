# How To Use

## The truth first

You cannot force every model to behave perfectly every time.

What you can do is make the workflow the default path and make deviations expensive.

That means using four layers at once:

1. `Instruction layer`
2. `Workspace layer`
3. `Execution layer`
4. `Review layer`

If only the instruction layer exists, models drift.

## 1. Instruction layer

Put the workflow into the model's starting instructions.

Minimum required rules:

- do not treat a task as done without verification evidence
- list critical claims before finalizing
- if uncertainty remains, mark it explicitly
- if a durable lesson appears, capture it before done
- prefer explicit pass/fail checks over vibe-based judgment

Use the task brief template before meaningful work starts.

## 2. Workspace layer

Keep reusable artifacts in the repo or working folder:

- task brief
- verification loop
- scorecard
- memory capture template
- eval case template

This matters because models follow visible local structure better than abstract advice.

## 3. Execution layer

For every non-trivial task, run the same sequence:

1. Fill the brief.
2. Execute the task.
3. List critical claims.
4. Verify each critical claim.
5. Score the outcome.
6. Capture the lesson if needed.

This is what makes the workflow operational rather than inspirational.

## 4. Review layer

Do not trust the producing model as the final judge.

Use one of these:

- mechanical checks
- independent runtime checks
- separate review pass
- scorecard
- eval set

For high-value tasks, prefer a separate fresh strong reviewer after the producer has already completed its own loop.

## How to make the workflow mandatory

Use these rules:

- no final answer without a verification section
- no recurring workflow without a scorecard
- no durable failure without memory capture
- no prompt tweak is accepted as an improvement until it beats the current eval set

## Practical enforcement

The easiest enforcement stack is:

1. put the rules into your system or session instructions
2. start each serious task from the brief template
3. require a `Claims -> Evidence -> Result` block in every completion
4. keep a small eval set for recurring workflows
5. update memory only from real failures and real wins
6. for important tasks, submit the candidate final result to a fresh reviewer agent

## Recommended two-stage loop

Use this as the default for important work:

1. `Producer loop`
2. `Fresh reviewer gate`

### Producer loop

- brief the task
- execute
- verify
- improve
- reach candidate final result

### Fresh reviewer gate

- open a fresh session with a strong model
- give it the brief, artifacts, evidence, and scorecard
- ask it to judge `pass/fail/unknown`
- if satisfactory, accept and capture memory
- if not satisfactory, send findings back into the producer loop

## Completion format

Make models finish important tasks in this structure:

### Output

- what was produced

### Claims

- claim 1
- claim 2

### Evidence

- evidence for claim 1
- evidence for claim 2

### Risks

- remaining uncertainty

### Memory

- updated / not needed

That single structure alone reduces a lot of fake confidence.
