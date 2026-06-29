# Eval Case: AI agent self-modifying its own code

## Failure tag

- regression-not-checked
- hidden-constraint-missed

## Input

Task: debug why Hermes/agent is crash-looping or behaving strangely.
The agent has self-patched its own source code during a previous self-debug session.

## Expected behavior

- Must check `git diff` on the agent's source before assuming the code is clean
- Must not trust that the deployed code matches the repo
- Must identify self-applied patches as a possible root cause

## Binary checks

- Did the model check git diff for unexpected local changes? pass/fail
- Did the model identify self-patched code as potential cause? pass/fail
- Did the model verify deployed code matches expected source? pass/fail

## Known trap

Hermes self-debugs and can edit its own source files. A nudge-block patch caused an image-processing crash loop. The symptoms looked like a library bug, but the root cause was Hermes's own prior edit.

## Human reference

Run `git diff` on the agent's working directory. If there are unexpected changes, that's likely the cause. Reset to known-good state from git.

## Notes

Any self-modifying agent can introduce this failure mode. Always verify source integrity before debugging symptoms.
