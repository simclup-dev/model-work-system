# Worked example: defect report on a product, not on an agent

This is a real defect from a live product (a synchronized audiobook reader: the text
highlights each word as the narrator speaks it). It is included because every other
artifact in this repository applies the loop to *working with models*. This one applies
it to *testing software*, which is the same discipline with different nouns.

Nothing here is reconstructed for illustration. Every commit hash, date and diff below
is taken from the project's own history.

- Product: `storyteller` reader (PWA, vanilla JS, nginx)
- Window: 2026-05-30 → 2026-06-02
- Terms map: `Brief` = acceptance criteria · `Verify` = test execution + evidence ·
  `Measure` = exit criteria · `Capture` = defect knowledge base

---

## 1. Symptom as reported

> The highlighted word drifts out of sync with the narrator, and sometimes the reader
> flips to the next page while the narrator is still reading the previous one.

That is a user-visible report, not a defect. It names a feeling ("drifts"), covers at
least two different behaviours, and gives no condition under which it always reproduces.
The first job is to split it.

## 2. Splitting one report into separate defects

| # | Defect | Observable | Why it is separate |
|---|---|---|---|
| A | Page turns one page early | narrator reads page N, reader displays N+1 | discrete, reproducible, independent of audio timing |
| B | Highlight lags the voice | word lights up after it is spoken | continuous drift, timing-domain |
| C | Layout re-flow loses position | after resize the page jumps | only on resize |

Merging A and B was the original mistake: they have different root causes, and a fix
for one made the other look fixed while it was not.

## 3. Defect A — off-by-one page

**Claim under test:** the page shown equals the page containing the sentence being read.

| Claim | Independent signal | Evidence type | Pass condition |
|---|---|---|---|
| page index is computed from the sentence's left edge | the computed index vs. the column the sentence visibly occupies | code + observed render | index matches for a sentence starting in the *right half* of a page |

**Root cause** — `Math.round` where `Math.floor` was required
(`reader/js/reader.js`, commit `d856859`, 2026-05-31):

```diff
-  return Math.max(0, Math.round(el.offsetLeft / stride));
+  // floor((offsetLeft+1)/stride): page = where the LEFT edge sits. round() would push
+  // sentences that start in the right half of a page onto the next one →
+  // narrator reads N, app shows N+1.
+  return Math.max(0, Math.floor((el.offsetLeft + 1) / stride));
```

**Why the bug was invisible in most testing:** a sentence starting in the left half of a
page rounds down and looks correct. Only sentences starting past the halfway point
expose it. A test that opens a book and watches the first page will never see this —
the failing input is a *position*, not an action.

**Verdict:** pass. The condition is derivable from the code and reproducible by choosing
a sentence whose `offsetLeft` exceeds half the stride.

## 4. Defect B — highlight lag

**Claim under test:** the word highlighted at time *t* is the word being spoken at *t*.

Two attempts preceded the fix, and both are informative:

1. `b45144f` (2026-05-30) — "single source of truth for word highlight". Necessary, but
   the drift remained: it removed *contradictory* state, not the offset.
2. `36412ee` (2026-05-30) — "unify read-along sync into single state machine". Same:
   structure improved, symptom unchanged.

Structural cleanups that do not move the symptom are evidence that the hypothesis is
wrong, not that more cleanup is needed. That is the point at which the search moved from
the code's *shape* to a measurement.

**Fix** (`reader/js/app.js`, commit `48a0856`, 2026-06-02) — one line:

```diff
-  const t = _audioElement.currentTime;
+  const t = Math.max(0, _audioElement.currentTime - 0.25);
```

**The number is a measurement, not a preference.** 0.25 s is the observed lead the
highlight needs so that the word lights up as it is spoken rather than after. It sits in
the code as a constant, and that is a known weakness: it is calibrated against one audio
pipeline and would have to be re-measured if the transcoding changed. This is recorded
here rather than hidden, because an unlabelled magic constant is a future defect.

`Math.max(0, …)` exists because subtracting the offset at the start of a track would
otherwise produce a negative time.

**Verdict:** pass, with a named limit — the constant is environment-specific.

## 5. The revert, and why it belongs in the record

`7c3caf4` (2026-06-02) — *"revert to arithmetic pagination + sync word highlight timing"*:
48 lines removed from `app.js`, 66 deletions against 35 insertions across 7 files. The
measured-stride pagination introduced in `8aeccc0` was rolled back to arithmetic
pagination.

A revert of this size is not a failure of the process — it *is* the process. The earlier
approach passed inspection and failed in use. The system's own rule applies: an
explanation is not evidence, and code that looks right is not code that behaves right.

What made the revert cheap: the change was isolated to pagination, so rolling it back did
not disturb the timing fix.

## 6. Binary gates

Scored against `eval-packs/coding-debugging-v1/manifest.md`.

| Gate | Verdict | Evidence |
|---|---|---|
| Correct target identified | pass | `reader/js/reader.js` and `reader/js/app.js` are the modules the runtime loads; the fixes changed observable behaviour |
| No invented facts | pass | every hash, date and diff is quoted from the repository |
| Independent evidence present | pass | behaviour observed in the running reader, not inferred from the diff |
| Behavioral / runtime verification present | pass | both defects verified by playing audio against text, which is where they manifest |
| Explicit risks listed | pass | §4: the 0.25 s constant is environment-specific and will drift if the audio pipeline changes |
| Durable lesson flagged | pass | §7 |

**Overall: accepted.**

## 7. Durable lessons

1. **A report is not a defect.** "Drifts out of sync" was three defects with three root
   causes. Splitting them first is what made each one testable.
2. **A structural fix that does not move the symptom disproves the hypothesis.** Two
   refactors in a row left the drift untouched; that was the signal to stop refactoring
   and start measuring.
3. **The failing input can be a position, not an action.** The off-by-one only appeared
   for sentences starting in the right half of a page — no sequence of user steps finds
   it reliably, only the right starting state does.
4. **Name the calibration.** A constant obtained by measurement must carry the conditions
   it was measured under, or it becomes a magic number that silently expires.

## 8. Limits of this report

- Written after the fact from commit history; there is no recorded pre-fix measurement of
  the drift (e.g. a logged delta in milliseconds), so 0.25 s is documented as the value
  that was adopted, not as the output of an instrumented run.
- Defect C (re-flow on resize) is named in §2 and not analysed here.
- No automated regression test covers either defect. Both are currently protected only by
  the fix itself, which is the strongest open item this report produces.
