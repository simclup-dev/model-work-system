# Reviewer Runbook

Use this after the producer already has a candidate final result.

## Inputs to the reviewer

Give the reviewer only:

- task brief
- produced artifact/output
- critical claims
- verification evidence
- score sheet

Do not give the hidden producer process by default.

## Launch prompt

Use:

- [fresh-reviewer.md](/C:/codex/model-work-system/prompts/fresh-reviewer.md)
- [reviewer-score-sheet.md](/C:/codex/model-work-system/reviewer-score-sheet.md)

## Review sequence

1. Check the task brief.
2. Extract the critical claims.
3. Match each claim to evidence.
4. Fail any unsupported claim.
5. Score the result.
6. Return verdict:
   - `done`
   - `done with risk`
   - `not done`
7. Flag memory capture if needed.

## Strict reviewer rules

- Do not trust narrative confidence.
- Do not accept “probably works.”
- Do not upgrade `unknown` to `pass`.
- If behavior can fail silently, require runtime or behavioral proof.
- If the producer says memory is not needed but the lesson is durable, flag it.

## Daily use

For each important task:

1. Producer finishes loop.
2. Reviewer evaluates candidate result.
3. If `not done`, return findings to producer.
4. If `done` or `done with risk`, capture memory if needed.

## Weekly use

Once per week:

1. Review the recent reviewer findings.
2. Add 1-3 new real failure cases.
3. Remove stale toy cases once real cases replace them.
