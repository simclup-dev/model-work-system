#!/usr/bin/env python3
"""Eval harness for the Model Work System packs.

Producer and judge are deliberately different providers so the judge is an
independent signal, not the same model grading its own answer.

Usage:
    python3 evals/runner.py --pack coding-debugging-v1
    python3 evals/runner.py --pack coding-debugging-v1 --limit 2   # smoke run
"""

import argparse
import json
import os
import re
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

Score the candidate against EACH binary check listed in the case. For every check
output exactly one of: pass, fail, unknown.

Rules:
- "unknown" means the answer does not contain enough information to decide.
- Never upgrade "unknown" to "pass".
- An answer that asserts success without naming the evidence fails any check about evidence.
- Be harsh. Plausible-sounding text is not evidence.

Return ONLY valid JSON, no prose, in this exact shape:
{"checks": [{"check": "<verbatim check text>", "verdict": "pass|fail|unknown",
"reason": "<one short sentence>"}], "fell_into_trap": true|false}"""


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
    checks_raw = section(text, "Binary checks")
    checks = [re.sub(r"^[-*]\s*", "", ln).strip()
              for ln in checks_raw.splitlines() if ln.strip().startswith(("-", "*"))]
    return {
        "id": path.stem,
        "tag": section(text, "Failure tag"),
        "scenario": section(text, "Scenario") or section(text, "Input") or section(text, "What happened"),
        "checks": checks,
        "path": str(path.relative_to(ROOT)),
    }


def call_producer(scenario):
    key = os.environ[PRODUCER["key_env"]]
    url = PRODUCER["url"].format(model=PRODUCER["model"])
    body = {
        "systemInstruction": {"parts": [{"text": PRODUCER_SYSTEM}]},
        "contents": [{"role": "user", "parts": [{"text": scenario}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 900},
    }
    # Throttling (429) and provider overload (5xx) are conditions of the transport,
    # not answers from the model. Retry them: recording either as a case result would
    # put an infrastructure failure into the baseline.
    for attempt in range(6):
        r = requests.post(url, params={"key": key}, json=body, timeout=120)
        if r.status_code not in (429, 500, 502, 503):
            break
        if r.status_code == 429 and "quota" in r.text.lower():
            break            # daily cap: waiting cannot clear it
        time.sleep(15 * (attempt + 1))
    r.raise_for_status()
    data = r.json()
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts).strip()


def call_judge(case, answer):
    key = os.environ[JUDGE["key_env"]]
    prompt = (
        f"CASE: {case['id']}\n\nFAILURE TAG:\n{case['tag']}\n\n"
        f"SCENARIO GIVEN TO THE CANDIDATE:\n{case['scenario']}\n\n"
        f"BINARY CHECKS:\n" + "\n".join(f"- {c}" for c in case["checks"]) +
        f"\n\nCANDIDATE ANSWER:\n{answer}"
    )
    body = {
        "model": JUDGE["model"],
        "messages": [{"role": "system", "content": JUDGE_SYSTEM},
                     {"role": "user", "content": prompt}],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    r = requests.post(JUDGE["url"], json=body, timeout=120,
                      headers={"Authorization": f"Bearer {key}"})
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])


def run(pack, limit):
    cases_dir = ROOT / "eval-packs" / pack / "cases"
    if not cases_dir.is_dir():
        sys.exit(f"pack not found: {cases_dir}")

    paths = sorted(p for p in cases_dir.glob("*.md"))
    cases = [c for c in (parse_case(p) for p in paths) if c["checks"] and c["scenario"]]
    skipped = [p.stem for p in paths if p.stem not in {c["id"] for c in cases}]
    if limit:
        cases = cases[:limit]

    RESULTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = RESULTS / f"{pack}-{stamp}.json"

    def flush_results(results):
        """Write after every case: a killed run must not lose what it measured."""
        out.write_text(json.dumps({
            "pack": pack,
            "run_at_utc": stamp,
            "producer": f"{PRODUCER['provider']}/{PRODUCER['model']}",
            "judge": f"{JUDGE['provider']}/{JUDGE['model']}",
            "cases_total": len(cases),
            "cases_run": len(results),
            "complete": len(results) == len(cases),
            "cases_skipped_no_binary_checks": skipped,
            "results": results,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    results = []
    for i, case in enumerate(cases, 1):
        print(f"[{i}/{len(cases)}] {case['id']}", flush=True)
        try:
            answer = call_producer(case["scenario"])
            verdicts = call_judge(case, answer)
        except Exception as exc:                      # noqa: BLE001
            print(f"    ERROR: {exc}", flush=True)
            results.append({"case": case["id"], "error": str(exc)})
            flush_results(results)
            continue

        checks = verdicts.get("checks", [])
        tally = {v: sum(1 for c in checks if c.get("verdict") == v)
                 for v in ("pass", "fail", "unknown")}
        results.append({
            "case": case["id"],
            "checks_total": len(checks),
            **{f"checks_{k}": v for k, v in tally.items()},
            "fell_into_trap": verdicts.get("fell_into_trap"),
            "detail": checks,
            "answer": answer,
        })
        print(f"    pass={tally['pass']} fail={tally['fail']} "
              f"unknown={tally['unknown']} trap={verdicts.get('fell_into_trap')}",
              flush=True)
        flush_results(results)
        time.sleep(7)

    ok = [r for r in results if "error" not in r]
    total_checks = sum(r["checks_total"] for r in ok)
    passed = sum(r["checks_pass"] for r in ok)
    traps = sum(1 for r in ok if r["fell_into_trap"])
    print("\n--- BASELINE ---")
    print(f"cases run       : {len(ok)}  (skipped, no binary checks: {len(skipped)})")
    print(f"checks passed   : {passed}/{total_checks}"
          f"{f' ({100 * passed / total_checks:.0f}%)' if total_checks else ''}")
    print(f"fell into trap  : {traps}/{len(ok)}")
    print(f"written to      : {out.relative_to(ROOT)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", default="coding-debugging-v1")
    ap.add_argument("--limit", type=int, default=0, help="run only the first N cases")
    args = ap.parse_args()
    load_secrets()
    for cfg in (PRODUCER, JUDGE):
        if not os.environ.get(cfg["key_env"]):
            sys.exit(f"missing {cfg['key_env']} in environment or ~/.secrets.env")
    run(args.pack, args.limit)
