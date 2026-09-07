# Bug report — hourly aggregation writes no rows while reporting success

A filed defect report in the standard form, from a live self-hosted service. It is kept
here as a worked example of the genre: preconditions, steps, expected vs actual,
environment, severity, evidence, and the fix that closed it. The companion document
[`bug-report-word-highlight-sync.md`](bug-report-word-highlight-sync.md) is an *analysis*
of a messy report; this one is the report itself.

---

## Summary

**ID:** P2P-001
**Title:** Hourly aggregation job writes no rows for 104 days while logging success
**Reported:** 2026-09-07
**Status:** Fixed and verified in production
**Severity:** **S2 — major.** No data loss, but a whole advertised feature (best-hour and
weekday statistics) was silently frozen, and the dashboard presented the stale figures as
current. Not S1: the raw collection, which is the part that cannot be recovered later,
was unaffected throughout.
**Priority:** P1 — every hour it stayed open added another hour of missing derived data.

## Environment

| | |
|---|---|
| Service | `p2p-monitor` — Binance P2P order-book monitor |
| Host | ARM VPS, Ubuntu 22.04, `systemd` unit `p2pmonitor.service` |
| Runtime | Python 3.10, APScheduler `AsyncIOScheduler`, SQLite |
| Storage | `snapshots` (raw, one row per advertised offer), `hourly_stats` and `daily_patterns` (derived) |
| Server timezone | UTC. Application aggregates in `Europe/Kyiv` (`+03:00` at the time of the report) |
| First affected | `2026-05-26T01:00:00+03:00` — the last row the job ever wrote |
| Found | 2026-09-07, while reading the database to correct figures in the README |

## Preconditions

1. The service is running and the collector is writing to `snapshots` normally.
2. `snapshots.ts` is a `TEXT` column containing UTC ISO-8601 timestamps, e.g.
   `2026-09-07T07:00:50.879790+00:00`. This is what the collector writes
   (`main.py`: `datetime.now(timezone.utc).isoformat()`).
3. The application timezone is set to something other than UTC (`Europe/Kyiv`).

## Steps to reproduce

1. Let the collector run for at least one hour so that `snapshots` holds rows for the
   current hour.
2. Wait for the scheduled `hourly_aggregate` job to fire at `:00`, or restart the service
   to trigger the startup aggregation.
3. Query the derived table:
   ```sql
   SELECT MAX(hour_start) FROM hourly_stats;
   ```
4. Compare it against the raw table:
   ```sql
   SELECT MAX(ts) FROM snapshots;
   ```

Reduced form, which isolates the defect without waiting for the scheduler:

```python
boundary = datetime.now(timezone.utc) - timedelta(hours=1)
storage.get_snapshots_since(boundary.isoformat())                        # rows
storage.get_snapshots_since(boundary.astimezone(KYIV).isoformat())       # no rows
```

## Expected result

`hourly_stats` gains one row per hour. Both calls in the reduced form describe the same
instant and must return the same rows.

## Actual result

`hourly_stats` last gained a row on 2026-05-26; `snapshots` is current to the minute. The
Kyiv-spelled boundary returns nothing:

```
string passed by the code (Kyiv): 2026-09-07T09:00:00+03:00  ->   0 rows
same instant in UTC form        : 2026-09-07T06:00:00+00:00  -> 130 rows
```

The job reports success every hour:

```
[INFO] apscheduler.executors.default: Job "hourly_aggregate (…)" executed successfully
```

## Root cause

`WHERE ts >= ?` against a `TEXT` column is a **lexicographic string comparison**, not a
temporal one. An ISO timestamp carrying a different UTC offset sorts by its written
digits: `"2026-09-07T09:00:00+03:00"` sorts *above* `"2026-09-07T07:00:50+00:00"` even
though it is two hours *earlier*. The aggregator built its window boundary in Kyiv time
and passed the string straight into the query, so the window was always empty.

**Second defect, one line away.** The empty-window branch logs `No data in last hour …,
using latest`, fetches the latest snapshot, and then falls through to `if rows:` — which
is false, because `rows` was never reassigned. The fallback announced in the log was
never executed, so the hour was skipped in silence.

## Why it went unnoticed for 104 days

- Nothing raised: no exception, no non-zero exit, no failed unit.
- The scheduler's own log line says `executed successfully`, which is true — the function
  returned normally.
- The single clue was a `WARNING` that reads like a transient collection gap in a service
  that is otherwise healthy.
- No check compared the derived tables against the raw one; freshness of `snapshots` was
  taken as evidence that the pipeline was working.

A job that reports success while writing nothing is worse than one that crashes:
monitoring cannot distinguish it from a healthy job.

## Fix

1. Normalise at the storage boundary: `get_snapshots_since()` converts any boundary it is
   given to the UTC spelling the column uses, so no caller has to remember. A naive string
   is read as UTC; an unparseable one is passed through rather than taking the service
   down.
2. The fallback branch now assigns `rows` and so keeps the promise it logs.
3. `backfill_p2p.py` rebuilt the derived tables from the raw snapshots.

## Verification

| Check | Evidence |
|---|---|
| Defect reproduced before the fix | 7 of 12 new tests fail against the pre-fix code |
| Fix works in tests | 12/12 pass; CI green on Python 3.11, 3.12, 3.13 |
| Fix works in production | after restart, `hourly_stats` gained its first row in 104 days (`2026-09-07T10:00:00+03:00`, 200 samples), then one per hour |
| Recovery complete | `hourly_stats` 141 → 2,455 rows covering 2026-05-16 → 2026-09-07; the 2,038-hour June–August hole closed; `daily_patterns` filled to the full 7 × 24 grid |
| No collateral damage | all 301,683 raw snapshots untouched |

## Regression tests added

- The same instant written with any UTC offset selects the same rows (parametrised over
  four timezones).
- A naive boundary is accepted and read as UTC.
- An empty window is still reachable — the fix must not simply widen the query.
- The hourly job either writes a row, or writes nothing for a stated reason.

## Related defect found in the same area

**P2P-002 — recovery tool pointed at a decommissioned host.** `backfill_p2p.py`, the
script that repairs exactly this damage, had `DB_PATH` hard-coded to an absolute path on
the machine the service had been migrated *away* from. Run on the current host it printed
`база не знайдена` and exited `0` — so the tool that fixes the outage looked like a tool
that had run and found nothing to do. Fixed: the path now resolves next to the script, and
a missing database exits non-zero.

**Lesson recorded:** a recovery tool must fail loudly when it cannot find what it repairs.
An absolute path is a hidden dependency on one machine, and it survives a migration by
pointing at nothing.
