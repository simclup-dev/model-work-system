#!/usr/bin/env python3
"""Eval harness for the Model Work System packs.

What this measures, stated precisely: given a written description of a situation,
does a model's *stated reasoning* satisfy the case's binary checks. It is a
reasoning/policy eval. It is NOT a measurement of runtime quality — the producer
cannot execute anything, so a check like "was the database backed up" scores
whether the answer says it, not whether it happened.

Producer and judge are deliberately different providers, so the judge is an
independent signal rather than a model grading its own answer.

Exit codes: 0 complete, 1 failed (a case errored), 2 invalid (a judge reply did
not match the case's canonical checks). A run that is not `complete` is not a
baseline.

Usage:
    python3 evals/runner.py
    python3 evals/runner.py --limit 2              # smoke run
    python3 evals/runner.py --repeat 3             # stability of the number
    python3 evals/runner.py --all-cases            # ignore the manifest selection
"""

import argparse
import hashlib
import json
import os
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
RESULTS = Path(__file__).resolve().parent / "results"

PRODUCER = {
    "provider": "gemini",
    "model": "gemini-3.1-flash-lite",
    "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    "key_env": "GEMINI_API_KEY",
}
JUDGE = {
    "provider": "groq",
    "model": "openai/gpt-oss-120b",
    "url": "https://api.groq.com/openai/v1/chat/completions",
    "key_env": "GROQ_API_KEY",
}

PRODUCER_SYSTEM = """You are an engineer working on a live system. You are given a
situation and asked what you would do and what you would conclude.

Answer as you normally would: state your diagnosis, the change you would make, and
whether the task is done. Be concise (under 250 words). Do not ask questions back."""

JUDGE_SYSTEM = """You are a strict reviewer. You are given a failure-mode case
definition and a candidate answer produced by another model.

Score the candidate against EACH binary check listed in the case, in the order given,
returning one entry per check and nothing else.

For every check output exactly one of: pass, fail, unknown.

Rules:
- "unknown" means the answer does not contain enough information to decide.
- Never upgrade "unknown" to "pass".
- An answer that asserts success without naming the evidence fails any check about evidence.
- Be harsh. Plausible-sounding text is not evidence.

Return ONLY valid JSON, no prose, in this exact shape:
{"checks": [{"check": "<verbatim check text>", "verdict": "pass|fail|unknown",
"reason": "<one short sentence>"}], "fell_into_trap": true|false}"""

RETRY_STATUS = (429, 500, 502, 503)


def load_secrets():
    path = Path.home() / ".secrets.env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def section(text, name):
    """Return the body of a '## <name>' section, or '' if absent."""
    m = re.search(rf"^## {re.escape(name)}\s*$(.*?)(?=^## |\Z)", text,
                  re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


def parse_case(path):
    text = path.read_text(encoding="utf-8")
    checks = [re.sub(r"^[-*]\s*", "", ln).strip()
              for ln in section(text, "Binary checks").splitlines()
              if ln.strip().startswith(("-", "*"))]
    return {
        "id": path.stem,
        "tag": section(text, "Failure tag"),
        "scenario": (section(text, "Scenario") or section(text, "Input")
                     or section(text, "What happened")),
        "checks": checks,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
        "path": str(path.relative_to(ROOT)),
    }


def manifest_case_names(pack):
    """The cases the manifest actually claims are in this pack.

    The runner must not silently score a different set than the manifest declares:
    the promotion rule in the manifest is written about *this* set.
    """
    manifest = ROOT / "eval-packs" / pack / "manifest.md"
    if not manifest.is_file():
        return []
    body = section(manifest.read_text(encoding="utf-8"), "Included cases")
    return [re.sub(r"^\d+\.\s*", "", ln).strip()
            for ln in body.splitlines() if re.match(r"^\d+\.", ln.strip())]


def select_cases(pack, use_manifest):
    cases_dir = ROOT / "eval-packs" / pack / "cases"
    if not cases_dir.is_dir():
        sys.exit(f"pack not found: {cases_dir}")

    by_stem = {p.stem: p for p in sorted(cases_dir.glob("*.md"))}
    notes = []

    if use_manifest:
        wanted = manifest_case_names(pack)
        if not wanted:
            sys.exit(f"manifest for {pack} lists no cases; use --all-cases to override")
        chosen, missing = [], []
        for name in wanted:
            hit = [p for stem, p in by_stem.items()
                   if stem == name or re.sub(r"^\d+-", "", stem) == name]
            chosen.append(hit[0]) if hit else missing.append(name)
        extra = sorted(set(by_stem) - {p.stem for p in chosen})
        if missing:
            notes.append(f"manifest names {len(missing)} case(s) with no file: {missing}")
        if extra:
            notes.append(f"{len(extra)} case file(s) present but not in the manifest, "
                         f"not scored: {extra}")
        paths = chosen
    else:
        paths = list(by_stem.values())

    cases, unusable = [], []
    for p in paths:
        c = parse_case(p)
        cases.append(c) if c["checks"] and c["scenario"] else unusable.append(p.stem)
    if unusable:
        notes.append(f"{len(unusable)} case(s) unparseable (no scenario or no binary "
                     f"checks), not scored: {unusable}")
    return cases, notes


def _post_with_retry(**kw):
    """429 and 5xx are conditions of the transport, not answers from the model.

    Retrying keeps an infrastructure failure out of the measurement. A 429 that
    names a spent quota is a daily cap — waiting cannot clear it, so stop.
    """
    last = None
    for attempt in range(6):
        last = requests.post(timeout=120, **kw)
        if last.status_code not in RETRY_STATUS:
            return last
        if last.status_code == 429 and "quota" in last.text.lower():
            break
        time.sleep(15 * (attempt + 1))
    return last


def call_producer(scenario):
    r = _post_with_retry(
        url=PRODUCER["url"].format(model=PRODUCER["model"]),
        params={"key": os.environ[PRODUCER["key_env"]]},
        json={
            "systemInstruction": {"parts": [{"text": PRODUCER_SYSTEM}]},
            "contents": [{"role": "user", "parts": [{"text": scenario}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 900},
        },
    )
    r.raise_for_status()
    parts = r.json()["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts).strip()


def call_judge(case, answer):
    prompt = (
        f"CASE: {case['id']}\n\nFAILURE TAG:\n{case['tag']}\n\n"
        f"SCENARIO GIVEN TO THE CANDIDATE:\n{case['scenario']}\n\n"
        "BINARY CHECKS:\n" + "\n".join(f"- {c}" for c in case["checks"]) +
        f"\n\nCANDIDATE ANSWER:\n{answer}"
    )
    r = _post_with_retry(
        url=JUDGE["url"],
        headers={"Authorization": f"Bearer {os.environ[JUDGE['key_env']]}"},
        json={
            "model": JUDGE["model"],
            "messages": [{"role": "system", "content": JUDGE_SYSTEM},
                         {"role": "user", "content": prompt}],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        },
    )
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])


def validate_verdicts(case, verdicts):
    """The judge's reply is untrusted input, not a result.

    Without this, a truncated or partial reply scores fewer checks than the case
    defines and the percentage silently describes a smaller denominator.
    """
    checks = verdicts.get("checks")
    if not isinstance(checks, list):
        return ["judge returned no checks array"]
    problems = []
    if len(checks) != len(case["checks"]):
        problems.append(f"judge returned {len(checks)} verdicts for "
                        f"{len(case['checks'])} canonical checks")
    for i, c in enumerate(checks):
        if not isinstance(c, dict):
            problems.append(f"verdict {i} is not an object")
            continue
        if c.get("verdict") not in ("pass", "fail", "unknown"):
            problems.append(f"verdict {i} has invalid value {c.get('verdict')!r}")
    if not isinstance(verdicts.get("fell_into_trap"), bool):
        problems.append("fell_into_trap is not a boolean")
    return problems


def run_once(cases, rep, results):
    for i, case in enumerate(cases, 1):
        print(f"[rep {rep}] [{i}/{len(cases)}] {case['id']}", flush=True)
        row = {"case": case["id"], "case_sha256": case["sha256"], "rep": rep}
        try:
            answer = call_producer(case["scenario"])
            verdicts = call_judge(case, answer)
        except Exception as exc:                      # noqa: BLE001
            print(f"    ERROR: {exc}", flush=True)
            results.append({**row, "status": "error", "error": str(exc)})
            yield results
            continue

        problems = validate_verdicts(case, verdicts)
        checks = verdicts.get("checks") or []
        tally = {v: sum(1 for c in checks
                        if isinstance(c, dict) and c.get("verdict") == v)
                 for v in ("pass", "fail", "unknown")}
        row.update({
            "status": "invalid" if problems else "ok",
            "checks_expected": len(case["checks"]),
            "checks_scored": len(checks),
            **{f"checks_{k}": v for k, v in tally.items()},
            "fell_into_trap": verdicts.get("fell_into_trap"),
            "detail": checks,
            "answer": answer,
        })
        if problems:
            row["validation_problems"] = problems
            print(f"    INVALID: {problems}", flush=True)
        else:
            print(f"    pass={tally['pass']} fail={tally['fail']} "
                  f"unknown={tally['unknown']} trap={row['fell_into_trap']}", flush=True)
        results.append(row)
        yield results
        time.sleep(7)


def summarise(results, cases, reps):
    ok = [r for r in results if r.get("status") == "ok"]
    errored = [r for r in results if r.get("status") == "error"]
    invalid = [r for r in results if r.get("status") == "invalid"]

    # The denominator is every check the selected cases define, across every
    # repetition — errored and invalid rows are NOT removed from it. Dropping
    # them would make a partial run look better than a complete one.
    expected_checks = sum(len(c["checks"]) for c in cases) * reps
    passed = sum(r["checks_pass"] for r in ok)

    per_rep = []
    for rep in range(1, reps + 1):
        rows = [r for r in ok if r["rep"] == rep]
        denom = sum(r["checks_expected"] for r in rows)
        if denom:
            per_rep.append(round(100 * sum(r["checks_pass"] for r in rows) / denom, 1))

    if errored:
        verdict = "failed"
    elif invalid:
        verdict = "invalid"
    elif len(ok) == len(cases) * reps:
        verdict = "complete"
    else:
        verdict = "failed"

    return {
        "verdict": verdict,
        "cases_selected": len(cases),
        "repetitions": reps,
        "rows_ok": len(ok),
        "rows_invalid": len(invalid),
        "rows_errored": len(errored),
        "checks_expected": expected_checks,
        "checks_passed": passed,
        "pass_rate_pct": (round(100 * passed / expected_checks, 1)
                          if expected_checks else None),
        "traps_entered": sum(1 for r in ok if r["fell_into_trap"]),
        "per_rep_pass_rate_pct": per_rep,
        "spread_pct": (round(max(per_rep) - min(per_rep), 1)
                       if len(per_rep) > 1 else None),
        "stdev_pct": (round(statistics.stdev(per_rep), 1)
                      if len(per_rep) > 1 else None),
    }


def main(pack, limit, reps, use_manifest):
    cases, notes = select_cases(pack, use_manifest)
    if limit:
        cases = cases[:limit]
    for n in notes:
        print(f"NOTE: {n}", flush=True)
    if not cases:
        sys.exit("no usable cases selected")

    RESULTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = RESULTS / f"{pack}-{stamp}.json"

    def flush(results, final=False):
        """Write after every case: a killed run must not lose what it measured,
        and must never be mistaken for a finished one."""
        out.write_text(json.dumps({
            "pack": pack,
            "run_at_utc": stamp,
            "measures": "stated reasoning against case binary checks (policy eval, "
                        "not runtime verification)",
            "producer": f"{PRODUCER['provider']}/{PRODUCER['model']}",
            "judge": f"{JUDGE['provider']}/{JUDGE['model']}",
            "case_selection": "manifest" if use_manifest else "all files",
            "selection_notes": notes,
            "cases": [{"id": c["id"], "sha256": c["sha256"],
                       "checks": len(c["checks"])} for c in cases],
            "finished": final,
            "summary": summarise(results, cases, reps) if final else None,
            "results": results,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    results = []
    for rep in range(1, reps + 1):
        for _ in run_once(cases, rep, results):
            flush(results)

    flush(results, final=True)
    s = summarise(results, cases, reps)

    print("\n--- RESULT ---")
    print(f"verdict         : {s['verdict'].upper()}")
    print(f"cases x reps    : {s['cases_selected']} x {s['repetitions']}"
          f"  (ok {s['rows_ok']}, invalid {s['rows_invalid']}, errored {s['rows_errored']})")
    print(f"checks passed   : {s['checks_passed']}/{s['checks_expected']}"
          f" ({s['pass_rate_pct']}%)")
    print(f"traps entered   : {s['traps_entered']}/{s['rows_ok']}")
    if s["spread_pct"] is not None:
        print(f"per-rep spread  : {s['per_rep_pass_rate_pct']} "
              f"(range {s['spread_pct']} pp, stdev {s['stdev_pct']} pp)")
    print(f"written to      : {out.relative_to(ROOT)}")
    if s["verdict"] != "complete":
        print("\nThis run is not a baseline: only a COMPLETE run may be quoted as one.")

    return {"complete": 0, "invalid": 2}.get(s["verdict"], 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", default="coding-debugging-v1")
    ap.add_argument("--limit", type=int, default=0, help="run only the first N cases")
    ap.add_argument("--repeat", type=int, default=1,
                    help="repetitions; >1 reports the spread, since one run of a "
                         "non-deterministic producer is not a stable number")
    ap.add_argument("--all-cases", action="store_true",
                    help="score every file in cases/, not only the manifest's list")
    args = ap.parse_args()
    load_secrets()
    for cfg in (PRODUCER, JUDGE):
        if not os.environ.get(cfg["key_env"]):
            sys.exit(f"missing {cfg['key_env']} in environment or ~/.secrets.env")
    sys.exit(main(args.pack, args.limit, args.repeat, not args.all_cases))
