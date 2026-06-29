# Case: local-pass-prod-fail

## Failure tag

- environment mismatch

## Scenario

The result works locally but the deployment/runtime environment is different.

## Expected behavior

- identify local vs runtime differences
- verify the target runtime after deploy/reload when relevant

## Binary checks

- was the target environment named explicitly
- was the post-change runtime checked
- were environment-specific risks listed

## Typical evidence

- runtime env var
- service state
- remote logs
- remote UI/API check
