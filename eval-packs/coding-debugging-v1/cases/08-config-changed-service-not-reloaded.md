# Case: config-changed-service-not-reloaded

## Failure tag

- config lifecycle

## Scenario

The producer changed config or env but never proved the service actually reloaded the new state.

## Expected behavior

- identify whether restart/reload/recreate is needed
- verify the live process picked up the change

## Binary checks

- was reload/restart need considered
- was live state checked after the change
- was success tied to current runtime rather than file contents alone
