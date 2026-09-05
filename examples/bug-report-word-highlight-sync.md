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

**The offset was not missing — it was wrong.** `git log -S"currentTime -"` on
`reader/js/app.js` returns three commits, and the first is the initial import:

| Commit | Date | Effect on the offset |
|---|---|---|
| `18326a1` | 2026-05-23 | offset present from the start: `currentTime - 0.35` |
| `7c3caf4` | 2026-06-02 | offset **removed**: back to raw `currentTime` |
| `48a0856` | 2026-06-02 | offset restored, recalibrated: `currentTime - 0.25` |

This changes the shape of the defect. The drift persisted *while a compensation constant
was already in place* — so the two structural attempts above were not merely looking in
the wrong layer, they were looking past a value that was present and miscalibrated. A
wrong constant is harder to see than a missing one: the code contains a line that appears
to handle the problem.

**Final state** (`48a0856`):

```diff
-  const t = _audioElement.currentTime;
+  const t = Math.max(0, _audioElement.currentTime - 0.25);
```

`Math.max(0, …)` exists because subtracting the offset at the start of a track would
otherwise produce a negative time.

**About the number itself.** 0.25 s replaced 0.35 s. Both are compensation constants tied
to one audio pipeline, and neither has a recorded measurement behind it in the repository
— §8. It is documented here as the value that was adopted and held, not as the output of
an instrumented run.

**Verdict:** the code change is confirmed by history; the adequacy of `0.25` is
**unknown** — no artifact proves it was measured rather than tuned by ear.

## 5. The revert, and why it belongs in the record

`7c3caf4` (2026-06-02) — *"revert to arithmetic pagination + sync word highlight timing"*:
`app.js` alone shows 13 insertions against 35 deletions (48 lines touched, not 48
removed); across all 7 files, 35 insertions against 66 deletions. The measured-stride
pagination introduced in `8aeccc0` was rolled back to arithmetic pagination.

A revert of this size is not a failure of the process — it *is* the process. The earlier
approach passed inspection and failed in use. The system's own rule applies: an
explanation is not evidence, and code that looks right is not code that behaves right.

**The revert was not isolated.** The same commit stripped the timing offset back to raw
`currentTime`, and the recalibrated `-0.25` arrived only in the next commit. So defects A
and B were not independent in practice: rolling back the pagination work also reset the
compensation for the timing defect, and both had to be re-established afterwards.

An earlier draft of this report claimed the opposite — that the revert "did not disturb
the timing fix". That claim was written from the commit subject lines without reading the
diff, and the diff disproves it. It is corrected here rather than quietly edited out,
because a report that hides its own retraction is the exact failure this repository is
about.

## 6. Binary gates

Scored against `eval-packs/coding-debugging-v1/manifest.md`.

| Gate | Verdict | Evidence |
|---|---|---|
| Correct target identified | pass | `reader/js/reader.js` and `reader/js/app.js` are the modules the runtime loads; the fixes changed observable behaviour |
| No invented facts | pass | every hash, date and diff is quoted from the repository |
| Independent evidence present | **unknown** | git proves the hashes, dates and diffs; it does not prove any playback session, and no test artifact was kept |
| Behavioral / runtime verification present | **unknown** | the fixes were almost certainly checked by listening — but "almost certainly" is not evidence, and nothing recorded it |
| Explicit risks listed | pass | §4: the constant is environment-specific and has no recorded measurement |
| Durable lesson flagged | pass | §7 |

**Overall: not accepted as a verified report.** Two critical gates are `unknown`, and the
manifest's rule is that all critical gates must pass. This is left standing rather than
softened: the fixes are real and the history is real, but the *verification* of them was
never captured, so the honest verdict is that this defect work would not pass its own
acceptance gate today. Making it pass requires a recorded playback check, not a rewording.

## 7. Durable lessons

1. **A report is not a defect.** "Drifts out of sync" was three defects with three root
   causes. Splitting them first is what made each one testable.
2. **A structural fix that does not move the symptom disproves the hypothesis.** Two
   refactors in a row left the drift untouched; that was the signal to stop refactoring
   and start measuring.
3. **A wrong constant hides better than a missing one.** The offset was present from the
   first commit and simply had the wrong value; two refactors passed over a line that
   looked like it already solved the problem.
4. **The failing input can be a position, not an action.** The off-by-one only appeared
   for sentences starting in the right half of a page — no sequence of user steps finds
   it reliably, only the right starting state does.
5. **Name the calibration.** A constant obtained by measurement must carry the conditions
   it was measured under, or it becomes a magic number that silently expires.

## 8. Limits of this report

- Written after the fact from commit history. There is no recorded pre-fix measurement of
  the drift (e.g. a logged delta in milliseconds), no test environment captured (browser,
  build, audio file), and no reproducible preconditions/steps — so this is a defect
  *analysis*, not a defect *report* in the form a QA team would file. That form is a
  separate artifact and is not claimed here.
- The first version of this document contained two factual errors, both found by an
  independent reviewer reading the diffs: it stated that the revert left the timing fix
  untouched, and that 48 lines were removed from `app.js`. Both are corrected above. The
  errors came from reading commit subjects instead of commit contents.
- Defect C (re-flow on resize) is named in §2 and not analysed here.
- No automated regression test covers either defect. Both are currently protected only by
  the fix itself, which is the strongest open item this report produces.
