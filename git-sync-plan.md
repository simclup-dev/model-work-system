# Git Sync Plan

## Recommendation

Yes, this should live in git.

Without git, Codex and Claude will slowly diverge.

## Best model

Use one canonical repo as the source of truth for:

- prompts
- scorecards
- eval packs
- workflow docs
- reviewer sheets
- integration snippets

Keep memory separate.

Do not sync model memory automatically through git.

## What should be in git

- `model-work-system/`
- Claude slash-command files derived from it
- Codex integration snippets
- eval packs
- reviewer score sheets

## What should not be in git

- live session transcripts
- personal memory databases
- secrets
- machine-specific caches
- temporary experiments unless promoted

## Suggested structure

- canonical repo on one machine
- clone on Windows/Codex side
- clone on Natali/Claude side
- optional clone on Oracle only if needed

## Update policy

1. change the canonical repo
2. commit the workflow change
3. pull on the other machine
4. regenerate any derived command files if needed
5. rerun the active eval baseline if the workflow behavior changed

## Branch policy

Keep it simple:

- `main` for stable workflow
- short-lived branches for experiments

Do not merge workflow changes into `main` until they beat the baseline evals.

## First practical step

Turn the current `C:\codex\model-work-system` folder into the canonical repo or move it into one.
