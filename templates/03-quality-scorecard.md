# Quality Scorecard

Use this for recurring workflows.

## Workflow name

- Name:

## Binary gates

If any binary gate fails, the run fails.

| Gate | Pass/Fail rule | Evidence |
|---|---|---|
| correctness floor | no invented facts / no broken output | proof |
| required artifact | expected file/result exists | proof |
| verification complete | all critical claims verified | proof |
| memory captured if needed | note written or not applicable | proof |

## Quality dimensions

Score each dimension with a clear rule.

| Dimension | Rule | Score range |
|---|---|---|
| correctness | how fully the result matches reality | 0-2 |
| completeness | whether the task is fully handled | 0-2 |
| constraint adherence | whether constraints were respected | 0-2 |
| clarity/usability | whether the output is usable without cleanup | 0-2 |
| efficiency | whether the path avoided waste/rework | 0-2 |

## Judge notes

- Prefer binary checks where possible.
- Use model-as-judge only for dimensions that cannot be mechanically checked.
- If using a judge model, calibrate it against human-scored examples.

## Eval dataset seed

Each recurring failure should be added as:

- input
- expected output or behavior
- failure tag
- scoring notes

## Release threshold

- Binary gates: all must pass
- Quality score: define minimum acceptable total
- Regression rule: no drop on critical dimensions
