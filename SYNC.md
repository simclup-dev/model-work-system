# Git Sync Instructions

## Architecture

```
Natali (WSL2)                          PC (Windows)
~/.claude/model-work-system/    →    C:\codex\model-work-system\
       ↕ push/pull                          ↕ push/pull
~/Sync/model-work-system.git  ←→  \\wsl$\Ubuntu\home\natali\Sync\model-work-system.git
       (bare repo, single source of truth)
```

Both working copies push/pull to the SAME bare repo via different paths.

## Setup (one-time, on PC in PowerShell)

```powershell
cd C:\codex
git clone \\wsl$\Ubuntu\home\natali\Sync\model-work-system.git model-work-system
```

If `C:\codex\model-work-system` already exists with uncommitted work:
```powershell
cd C:\codex\model-work-system
git remote set-url origin \\wsl$\Ubuntu\home\natali\Sync\model-work-system.git
git pull --rebase
```

## After changes on Natali (Claude Code)

```bash
cd ~/.claude/model-work-system
git add -A && git commit -m "description"
git push
```

Then on PC: `git pull` (Codex does this, or manually in PowerShell).

## After changes on PC (Codex)

```powershell
cd C:\codex\model-work-system
git add -A && git commit -m "description"
git push
```

Then on Natali: `cd ~/.claude/model-work-system && git pull`.

## Rules

- Always pull before starting work
- Never force-push
- Conflicts: resolve manually, prefer the newer change
- Memory files stay separate (Claude memory ≠ Codex memory) — only the system itself syncs
