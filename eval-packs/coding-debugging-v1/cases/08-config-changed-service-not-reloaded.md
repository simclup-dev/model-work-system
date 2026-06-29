# Case: config-changed-service-not-reloaded

## Failure tag

- config lifecycle
- file/live drift
- runtime env mismatch

## Scenario

Real pattern from the Subscription Tracker callback chain:

The producer changed config or env and maybe even saw a `200 OK`, but never proved the service actually reloaded the new state.

Concrete shape of the trap:

- `.env` was updated with the right callback URL
- the container was not recreated, or prod had drift from the git copy
- the app kept running with stale env, so behavior stayed broken
- surface-level success hid the real failure

## Expected behavior

- identify whether restart, reload, or recreate is needed
- verify the live process picked up the change
- check file parity if production is hand-synced or drift-prone
- verify the effective runtime value inside the live container or process

## Binary checks

- was reload or restart need considered
- was live state checked after the change
- was success tied to current runtime rather than file contents alone
- if a container or service was involved, was the runtime env or live config inspected directly
- if the deploy target can drift from git, was parity checked before concluding

## Typical evidence

- `docker exec ... printenv ...`
- health check after recreate or restart
- live process config dump
- proof that the deploy target and source tree are aligned

## Typical failure

- "the file contains the new value, so the service must be using it"
- "the webhook returned 200 OK, so the callback chain is healthy"
