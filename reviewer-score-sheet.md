# Reviewer Score Sheet

Use this with the fresh strong reviewer after the producer already has a candidate final result.

## Review inputs

The reviewer should receive only:

- task brief
- produced artifact/output
- critical claims
- verification evidence
- scorecard

The reviewer should not rely on hidden process history.

## Binary gates

If any critical gate fails, the verdict is `not done`.

| Gate | Question | Pass/Fail |
|---|---|---|
| Brief sufficiency | Is the task brief sufficient to judge the result? |  |
| Claim coverage | Were the critical claims identified clearly enough? |  |
| Evidence sufficiency | Does each critical claim have independent evidence? |  |
| No fabricated support | Is there any sign of invented facts, logs, files, or runtime claims? |  |
| Behavioral verification | For silent-failure risk, is there behavioral/runtime proof? |  |
| Constraint adherence | Were explicit constraints respected? |  |
| Memory discipline | If a durable lesson appeared, was it flagged for capture? |  |

## Quality dimensions

Score each 0-2.

| Dimension | 0 | 1 | 2 | Score |
|---|---|---|---|---|
| Correctness | unproven/wrong | partly supported | well supported |  |
| Completeness | major gaps | minor gaps | complete |  |
| Verification quality | weak | mixed | strong |  |
| Clarity/usability | unclear | acceptable | clean and usable |  |
| Reliability confidence | low | medium | high |  |

## Verdict rules

- If any critical binary gate fails -> `not done`
- If all critical gates pass but notable risk remains -> `done with risk`
- If all critical gates pass and risks are acceptable -> `done`

## Reviewer output format

### Binary gates
- gate 1: pass/fail
- gate 2: pass/fail

### Quality score
- x / 10

### Findings
- finding 1
- finding 2

### Risks
- risk 1
- risk 2

### Verdict
- done
- done with risk
- not done

### Memory trigger
- yes/no
- what should be captured
