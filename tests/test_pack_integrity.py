"""Integrity of the eval pack and of the numbers quoted from it.

A pack rots quietly: a case gets renamed, the manifest keeps the old name, and
the run scores nine cases while the promotion rule still talks about ten. The
same goes for BASELINE.md, which quotes figures that live in a JSON file
nobody re-reads. These tests read both and make them agree.

No network, no API keys.
"""
import json
import re
from pathlib import Path

import pytest

import runner

ROOT = Path(__file__).resolve().parent.parent
PACK = "coding-debugging-v1"
CASES_DIR = ROOT / "eval-packs" / PACK / "cases"
BASELINE = ROOT / "evals" / "BASELINE.md"


# --------------------------------------------------------------------------
# the pack
# --------------------------------------------------------------------------

def case_files():
    return sorted(CASES_DIR.glob("*.md"))


def test_the_pack_has_case_files():
    assert case_files(), f"no case files under {CASES_DIR}"


@pytest.mark.parametrize("path", case_files(), ids=lambda p: p.stem)
def test_every_case_file_is_parseable(path):
    """A case with no scenario or no checks is skipped by the runner.

    Skipped silently, it shrinks the set the promotion rule is written about.
    """
    case = runner.parse_case(path)
    assert case["scenario"], "no Scenario/Input/What happened section"
    assert case["checks"], "no Binary checks section"
    assert case["tag"], "no Failure tag section"


@pytest.mark.parametrize("path", case_files(), ids=lambda p: p.stem)
def test_case_checks_are_not_duplicated(path):
    checks = runner.parse_case(path)["checks"]
    assert len(checks) == len(set(checks)), "the same binary check appears twice"


def test_every_manifest_name_resolves_to_a_file():
    """The manifest is the contract; a name with no file scores nothing."""
    _, notes = runner.select_cases(PACK, use_manifest=True)
    assert not [n for n in notes if "no file" in n], notes


def test_manifest_selection_scores_the_documented_number_of_cases():
    cases, _ = runner.select_cases(PACK, use_manifest=True)
    assert len(cases) == len(runner.manifest_case_names(PACK))


def test_unlisted_case_files_are_reported_not_silently_included():
    """BASELINE.md states that unlisted files exist and were not scored."""
    cases, notes = runner.select_cases(PACK, use_manifest=True)
    all_cases, _ = runner.select_cases(PACK, use_manifest=False)
    unlisted = len(all_cases) - len(cases)
    if unlisted:
        assert any("not in the manifest" in n for n in notes)
        assert f"{unlisted} case files" in BASELINE.read_text(encoding="utf-8"), (
            "BASELINE.md quotes a different count of unlisted files")


# --------------------------------------------------------------------------
# BASELINE.md against the raw result it cites
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def baseline_text():
    return BASELINE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def cited_run(baseline_text):
    m = re.search(r"`(evals/results/[^`]+\.json)`", baseline_text)
    assert m, "BASELINE.md cites no raw result file"
    path = ROOT / m.group(1)
    assert path.is_file(), f"cited result file is missing: {m.group(1)}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_cited_run_is_finished_and_complete(cited_run):
    """Only a COMPLETE run may be quoted as a baseline — the repo's own rule."""
    assert cited_run["finished"] is True
    assert cited_run["summary"]["verdict"] == "complete"


def test_cited_run_scored_the_manifest_cases(cited_run):
    assert cited_run["case_selection"] == "manifest"
    assert cited_run["summary"]["cases_selected"] == len(runner.manifest_case_names(PACK))


def test_cited_run_case_hashes_still_match_the_files(cited_run):
    """If a case was edited after the run, the baseline describes older text."""
    current = {c["id"]: c["sha256"]
               for c in runner.select_cases(PACK, use_manifest=True)[0]}
    drifted = [c["id"] for c in cited_run["cases"]
               if current.get(c["id"]) != c["sha256"]]
    assert not drifted, f"case text changed since the baseline run: {drifted}"


def test_baseline_headline_numbers_match_the_raw_run(baseline_text, cited_run):
    s = cited_run["summary"]
    passed, expected = s["checks_passed"], s["checks_expected"]
    assert f"{passed} / {expected}" in baseline_text or \
           f"{passed}/{expected}" in baseline_text, \
        f"BASELINE.md does not quote {passed}/{expected}"
    assert f"{s['pass_rate_pct']}%" in baseline_text
    assert f"{s['traps_entered']} / {s['rows_ok']}" in baseline_text or \
           f"{s['traps_entered']}/{s['rows_ok']}" in baseline_text


def test_baseline_quotes_the_spread_that_makes_it_usable(baseline_text, cited_run):
    s = cited_run["summary"]
    assert s["repetitions"] > 1, "a single repetition is not a baseline"
    assert f"{s['spread_pct']} pp" in baseline_text
    for rate in s["per_rep_pass_rate_pct"]:
        assert f"{rate}%" in baseline_text, f"per-rep rate {rate}% not quoted"


def test_summarise_reproduces_the_stored_summary(cited_run):
    """Recompute the summary from the stored rows: the file must not disagree
    with the code that wrote it."""
    cases = [{"checks": [None] * c["checks"]} for c in cited_run["cases"]]
    recomputed = runner.summarise(cited_run["results"], cases,
                                  cited_run["summary"]["repetitions"])
    assert recomputed == cited_run["summary"]
