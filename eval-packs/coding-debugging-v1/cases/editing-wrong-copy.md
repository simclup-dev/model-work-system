# Eval Case: editing the wrong copy of a service

## Failure tag

- wrong-runtime-file
- local-pass-prod-fail

## Input

Task: fix or update a service that has copies on multiple hosts (e.g. companion bot on both Natali and Oracle).
Model edits the local copy without checking which one is actually running.

## Expected behavior

- Must identify where the service actually runs (check systemd, docker ps, process list)
- Must edit only the live copy
- Must not restart a dead/disabled copy (causes conflicts like Telegram getUpdates race)

## Binary checks

- Did the model verify which host runs the live service? pass/fail
- Did the model edit files on the correct host? pass/fail
- Did the model avoid activating dead/disabled copies? pass/fail

## Known trap

Companion bot exists on both Natali (`/mnt/f/stacks/companion/` — DEAD, disabled) and Oracle (`~/stacks/companion/` — LIVE). Editing or restarting the Natali copy causes getUpdates token conflicts and both instances fight over messages.

## Human reference

Always `ssh oracle "systemctl status companion"` or `docker ps` to confirm where the service runs before touching any files.

## Notes

After migration to Oracle (2026-06-18), all services moved there. Local copies on Natali are dead remnants. This pattern applies to any multi-host setup.
