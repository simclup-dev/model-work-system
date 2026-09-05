# Eval Case: editing the wrong copy of a service

## Failure tag

- wrong-runtime-file
- local-pass-prod-fail

## Input

Task: fix or update a service that has copies on multiple hosts (e.g. a bot deployed on both a home host and a cloud host).
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

The service exists on two hosts: on the home host (`<home>/stacks/<service>/` — DEAD, disabled) and on the cloud host (`~/stacks/<service>/` — LIVE). Editing or restarting the dead copy causes getUpdates token conflicts and both instances fight over messages.

## Human reference

Always `ssh <host> "systemctl status <service>"` or `docker ps` to confirm where the service runs before touching any files.

## Notes

After a migration, all services moved to one host and the copies left behind on the old one are dead remnants. This pattern applies to any multi-host setup.
