"""Unit tests for the eval harness.

These test the parts that decide *what number the run reports*. A harness that
miscounts does not fail loudly — it prints a plausible percentage — so the
invariants below are the ones worth pinning down:

- a check the judge never scored is never counted as a pass;
- rows that errored stay in the denominator;
- only a run with every row ok may call itself COMPLETE;
- a transport failure is retried, not recorded as an answer.
"""
import json
import textwrap

import pytest

import runner


# --------------------------------------------------------------------------
# section()
# --------------------------------------------------------------------------

MD = textwrap.dedent("""\
    # Case

    ## Failure tag
    wrong-runtime-file

    ## Scenario
    The service still serves the old response.
    Second line of the scenario.

    ## Binary checks
    - names the file actually loaded at runtime
    * quotes the evidence
    not a bullet, ignored

    ## Notes
    trailing section
    """)


def test_section_returns_body_and_stops_at_next_heading():
    assert runner.section(MD, "Failure tag") == "wrong-runtime-file"
    assert runner.section(MD, "Scenario").splitlines() == [
        "The service still serves the old response.",
        "Second line of the scenario.",
    ]


def test_section_absent_returns_empty_string():
    assert runner.section(MD, "No Such Section") == ""


def test_section_name_is_not_a_regex():
    """A name with regex metacharacters must not match a different heading.

    Unescaped, "a.c" matches the literal heading "## abc" and returns the wrong
    section's body.
    """
    assert runner.section("## abc\nwrong body\n", "a.c") == ""


# --------------------------------------------------------------------------
# parse_case()
# --------------------------------------------------------------------------

def write_case(root, name, body):
    d = root / "eval-packs" / "p" / "cases"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{name}.md"
    p.write_text(body, encoding="utf-8")
    return p


def test_parse_case_extracts_fields_and_strips_bullet_markers(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    case = runner.parse_case(write_case(tmp_path, "01-demo", MD))

    assert case["id"] == "01-demo"
    assert case["tag"] == "wrong-runtime-file"
    assert case["checks"] == [
        "names the file actually loaded at runtime",
        "quotes the evidence",
    ]
    assert case["path"] == "eval-packs/p/cases/01-demo.md"


@pytest.mark.parametrize("heading", ["Scenario", "Input", "What happened"])
def test_parse_case_accepts_each_scenario_heading(tmp_path, monkeypatch, heading):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    body = f"## {heading}\nthe situation\n\n## Binary checks\n- a check\n"
    assert runner.parse_case(write_case(tmp_path, "c", body))["scenario"] == "the situation"


def test_parse_case_hash_changes_with_content(tmp_path, monkeypatch):
    """The hash is what lets a result file prove which text was scored."""
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    first = runner.parse_case(write_case(tmp_path, "c", MD))["sha256"]
    again = runner.parse_case(write_case(tmp_path, "c", MD))["sha256"]
    edited = runner.parse_case(write_case(tmp_path, "c", MD + "one more word\n"))["sha256"]

    assert first == again
    assert first != edited


# --------------------------------------------------------------------------
# manifest_case_names() / select_cases()
# --------------------------------------------------------------------------

def write_manifest(root, names):
    d = root / "eval-packs" / "p"
    d.mkdir(parents=True, exist_ok=True)
    body = "## Included cases\n" + "".join(
        f"{i}. {n}\n" for i, n in enumerate(names, 1))
    (d / "manifest.md").write_text(body, encoding="utf-8")


def test_manifest_case_names_reads_the_numbered_list(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    write_manifest(tmp_path, ["alpha", "beta"])
    assert runner.manifest_case_names("p") == ["alpha", "beta"]


def test_manifest_case_names_missing_file_is_empty_not_an_error(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    assert runner.manifest_case_names("nope") == []


def test_select_cases_scores_only_the_manifest_and_reports_the_rest(tmp_path, monkeypatch):
    """The promotion rule is written about the manifest's set.

    An extra file in cases/ must be reported, never silently scored.
    """
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    write_case(tmp_path, "01-alpha", MD)
    write_case(tmp_path, "unlisted", MD)
    write_manifest(tmp_path, ["alpha"])

    cases, notes = runner.select_cases("p", use_manifest=True)

    assert [c["id"] for c in cases] == ["01-alpha"]          # numeric prefix matched
    assert any("unlisted" in n and "not in the manifest" in n for n in notes)


def test_select_cases_reports_a_manifest_name_with_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    write_case(tmp_path, "alpha", MD)
    write_manifest(tmp_path, ["alpha", "ghost"])

    cases, notes = runner.select_cases("p", use_manifest=True)

    assert [c["id"] for c in cases] == ["alpha"]
    assert any("ghost" in n and "no file" in n for n in notes)


def test_select_cases_drops_unparseable_cases_and_says_so(tmp_path, monkeypatch):
    """A file with no binary checks would otherwise contribute 0 to the denominator."""
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    write_case(tmp_path, "good", MD)
    write_case(tmp_path, "broken", "## Scenario\nno checks here\n")

    cases, notes = runner.select_cases("p", use_manifest=False)

    assert [c["id"] for c in cases] == ["good"]
    assert any("broken" in n and "unparseable" in n for n in notes)


def test_select_cases_all_files_mode_ignores_the_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    write_case(tmp_path, "alpha", MD)
    write_case(tmp_path, "unlisted", MD)
    write_manifest(tmp_path, ["alpha"])

    cases, _ = runner.select_cases("p", use_manifest=False)

    assert sorted(c["id"] for c in cases) == ["alpha", "unlisted"]


def test_select_cases_missing_pack_exits(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    with pytest.raises(SystemExit):
        runner.select_cases("absent", use_manifest=False)


def test_select_cases_empty_manifest_exits_rather_than_scoring_everything(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    write_case(tmp_path, "alpha", MD)
    write_manifest(tmp_path, [])
    with pytest.raises(SystemExit):
        runner.select_cases("p", use_manifest=True)


# --------------------------------------------------------------------------
# validate_verdicts()
# --------------------------------------------------------------------------

CASE = {"id": "c", "checks": ["check one", "check two"]}


def verdicts(*values, trap=False):
    return {"checks": [{"check": "x", "verdict": v, "reason": "r"} for v in values],
            "fell_into_trap": trap}


def test_validate_verdicts_accepts_a_well_formed_reply():
    assert runner.validate_verdicts(CASE, verdicts("pass", "fail")) == []


def test_validate_verdicts_catches_a_short_reply():
    """A truncated reply would otherwise shrink the denominator silently."""
    problems = runner.validate_verdicts(CASE, verdicts("pass"))
    assert problems and "1 verdicts for 2 canonical checks" in problems[0]


def test_validate_verdicts_rejects_an_invented_verdict_value():
    problems = runner.validate_verdicts(CASE, verdicts("pass", "partial"))
    assert any("invalid value" in p and "partial" in p for p in problems)


def test_validate_verdicts_rejects_a_missing_checks_array():
    assert runner.validate_verdicts(CASE, {"fell_into_trap": False}) == [
        "judge returned no checks array"]


def test_validate_verdicts_rejects_a_non_object_entry():
    reply = {"checks": ["just a string", {"verdict": "pass"}], "fell_into_trap": False}
    assert any("not an object" in p for p in runner.validate_verdicts(CASE, reply))


def test_validate_verdicts_requires_a_boolean_trap_flag():
    reply = verdicts("pass", "fail")
    reply["fell_into_trap"] = "yes"
    assert any("fell_into_trap" in p for p in runner.validate_verdicts(CASE, reply))


# --------------------------------------------------------------------------
# summarise()
# --------------------------------------------------------------------------

def row(rep=1, status="ok", expected=2, passed=2, unknown=0, trap=False):
    return {"rep": rep, "status": status, "checks_expected": expected,
            "checks_pass": passed, "checks_fail": expected - passed - unknown,
            "checks_unknown": unknown, "fell_into_trap": trap}


CASES_2 = [{"checks": ["a", "b"]}]


def test_summarise_complete_run():
    s = runner.summarise([row(passed=1)], CASES_2, reps=1)
    assert s["verdict"] == "complete"
    assert (s["checks_passed"], s["checks_expected"]) == (1, 2)
    assert s["pass_rate_pct"] == 50.0


def test_summarise_never_counts_unknown_as_a_pass():
    s = runner.summarise([row(passed=0, unknown=2)], CASES_2, reps=1)
    assert s["checks_passed"] == 0
    assert s["pass_rate_pct"] == 0.0


def test_summarise_keeps_errored_rows_in_the_denominator():
    """A killed or erroring run must not score higher than a finished one."""
    complete = runner.summarise([row(passed=1), row(rep=2, passed=1)],
                                CASES_2, reps=2)
    partial = runner.summarise([row(passed=1), {"rep": 2, "status": "error"}],
                               CASES_2, reps=2)

    assert complete["checks_expected"] == partial["checks_expected"] == 4
    assert partial["pass_rate_pct"] < complete["pass_rate_pct"]


@pytest.mark.parametrize("rows,expected", [
    ([row()], "complete"),
    ([{"rep": 1, "status": "error"}], "failed"),
    ([row(), {"rep": 1, "status": "invalid"}], "invalid"),
    ([], "failed"),
])
def test_summarise_verdict(rows, expected):
    assert runner.summarise(rows, CASES_2, reps=1)["verdict"] == expected


def test_summarise_a_row_short_of_the_plan_is_not_complete():
    """Fewer ok rows than cases x reps means something was skipped."""
    s = runner.summarise([row()], CASES_2, reps=2)
    assert s["verdict"] == "failed"


def test_summarise_reports_spread_across_repetitions():
    s = runner.summarise([row(rep=1, passed=2), row(rep=2, passed=1)],
                         CASES_2, reps=2)
    assert s["per_rep_pass_rate_pct"] == [100.0, 50.0]
    assert s["spread_pct"] == 50.0
    assert s["stdev_pct"] is not None


def test_summarise_single_repetition_has_no_spread():
    s = runner.summarise([row()], CASES_2, reps=1)
    assert s["spread_pct"] is None and s["stdev_pct"] is None


def test_summarise_counts_traps_only_over_ok_rows():
    s = runner.summarise([row(trap=True), {"rep": 1, "status": "error"}],
                         CASES_2, reps=2)
    assert s["traps_entered"] == 1 and s["rows_ok"] == 1


def test_summarise_no_checks_gives_no_rate_instead_of_dividing_by_zero():
    assert runner.summarise([], [{"checks": []}], reps=1)["pass_rate_pct"] is None


# --------------------------------------------------------------------------
# _post_with_retry()
# --------------------------------------------------------------------------

class FakeResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text


@pytest.fixture
def no_sleep(monkeypatch):
    slept = []
    monkeypatch.setattr(runner.time, "sleep", slept.append)
    return slept


def post_returning(monkeypatch, *responses):
    calls = []

    def fake_post(**kw):
        calls.append(kw)
        return responses[min(len(calls) - 1, len(responses) - 1)]

    monkeypatch.setattr(runner.requests, "post", fake_post)
    return calls


@pytest.mark.parametrize("status", [429, 500, 502, 503])
def test_post_with_retry_retries_transport_failures(monkeypatch, no_sleep, status):
    """A 5xx is a condition of the transport, not an answer worth scoring."""
    calls = post_returning(monkeypatch, FakeResponse(status), FakeResponse(200))
    assert runner._post_with_retry(url="u").status_code == 200
    assert len(calls) == 2 and len(no_sleep) == 1


def test_post_with_retry_stops_on_a_spent_quota(monkeypatch, no_sleep):
    """A daily cap cannot be waited out; retrying only burns the run."""
    calls = post_returning(monkeypatch, FakeResponse(429, "Quota exceeded for the day"))
    assert runner._post_with_retry(url="u").status_code == 429
    assert len(calls) == 1 and no_sleep == []


def test_post_with_retry_gives_up_after_a_bounded_number_of_attempts(monkeypatch, no_sleep):
    calls = post_returning(monkeypatch, FakeResponse(503))
    assert runner._post_with_retry(url="u").status_code == 503
    assert len(calls) == 6


def test_post_with_retry_returns_other_errors_immediately(monkeypatch, no_sleep):
    """401 is an answer about our request; retrying it hides the cause."""
    calls = post_returning(monkeypatch, FakeResponse(401))
    assert runner._post_with_retry(url="u").status_code == 401
    assert len(calls) == 1


def test_post_with_retry_passes_a_timeout(monkeypatch, no_sleep):
    """No timeout means a hung request can stall a whole run silently."""
    calls = post_returning(monkeypatch, FakeResponse(200))
    runner._post_with_retry(url="u")
    assert calls[0]["timeout"] > 0
