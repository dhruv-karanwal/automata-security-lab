"""API tests for the FastAPI application."""

from fastapi.testclient import TestClient

from app.engines.dfa import win_prize_now_dfa
from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "project": "Automata Security Lab",
    }


def test_list_automata_uses_the_public_schema() -> None:
    response = client.get("/api/automata")

    assert response.status_code == 200
    payload = response.json()
    assert [item["automaton_id"] for item in payload["automata"]] == [
        "dfa_win_prize_now",
        "nfa_phishing_branches",
    ]
    assert payload["automata"][0]["automaton_type"] == "dfa"
    assert payload["automata"][0]["start_state"] == "q0"


def test_get_automaton_and_unknown_id() -> None:
    response = client.get("/api/automata/dfa_win_prize_now")
    missing = client.get("/api/automata/not-configured")

    assert response.status_code == 200
    assert response.json()["accepting_states"] == ["q3"]
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Automaton not found."}


def test_nfa_to_dfa_conversion_endpoint_returns_computed_total_dfa() -> None:
    response = client.get(
        "/api/automata/nfa_phishing_branches/convert-to-dfa"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_automaton_id"] == "nfa_phishing_branches"
    assert payload["initial_epsilon_closure"] == ["a0", "c0", "s0", "w0"]
    assert payload["dfa_start_state"] == "D0"
    assert any(state["state_id"] == "D_dead" for state in payload["dfa_states"])
    assert len(payload["transitions"]) == (
        len(payload["dfa_states"]) * len(payload["alphabet"])
    )
    accepting_ids = {
        state["state_id"]
        for state in payload["dfa_states"]
        if state["is_accepting"]
    }
    assert accepting_ids == set(payload["dfa_accepting_states"])
    assert payload["construction_steps"]


def test_conversion_endpoint_rejects_non_nfa_and_unknown_automata() -> None:
    wrong_type = client.get(
        "/api/automata/dfa_win_prize_now/convert-to-dfa"
    )
    missing = client.get("/api/automata/not-configured/convert-to-dfa")

    assert wrong_type.status_code == 400
    assert wrong_type.json() == {
        "detail": "Subset construction requires the configured NFA."
    }
    assert missing.status_code == 404


def test_dfa_catalog_is_total_and_agrees_with_the_engine() -> None:
    description = client.get("/api/automata/dfa_win_prize_now").json()
    catalog = {
        (transition["from_state"], transition["symbol"]): transition["to_states"][0]
        for transition in description["transitions"]
    }

    assert len(catalog) == len(win_prize_now_dfa.states) * len(
        win_prize_now_dfa.alphabet
    )
    for state in win_prize_now_dfa.states:
        for symbol in win_prize_now_dfa.alphabet:
            assert catalog[(state, symbol)] == win_prize_now_dfa.next_state(
                state, symbol
            )


def test_combined_analysis_executes_all_engines_without_fabricating_results() -> None:
    response = client.post(
        "/api/analyze",
        json={
            "subject": "Contact help@example.com",
            "body": "WIN PRIZE NOW",
            "mode": "combined",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "combined"
    assert payload["classification"] == "suspicious"
    assert payload["risk_score"] == 100
    assert payload["dfa_result"]["accepted"] is True
    assert payload["nfa_result"]["accepted"] is True
    assert payload["regex_result"]["matched"] is True
    assert payload["regex_result"]["matched_patterns"][0]["pattern_id"] == (
        "RULE-EMAIL"
    )


def test_combined_analysis_reports_each_detector_rejection_independently() -> None:
    response = client.post(
        "/api/analyze",
        json={"subject": "Weekly meeting", "body": "Agenda tomorrow", "mode": "combined"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["classification"] == "no_configured_patterns_matched"
    assert payload["risk_score"] == 0
    assert payload["dfa_result"]["accepted"] is False
    assert payload["nfa_result"]["accepted"] is False
    assert payload["regex_result"]["matched"] is False
    assert payload["dfa_result"]["trace"]
    assert payload["nfa_result"]["trace"]
    assert payload["regex_result"]["matched_patterns"] == []


def test_analyze_rejects_invalid_mode_and_empty_required_body() -> None:
    invalid = client.post(
        "/api/analyze",
        json={"subject": "Example", "body": "Message", "mode": "invalid"},
    )
    missing_body = client.post(
        "/api/analyze",
        json={"subject": "Example", "mode": "combined"},
    )

    assert invalid.status_code == 422
    assert missing_body.status_code == 422


def test_combined_analysis_allows_empty_strings_and_reports_real_rejections() -> None:
    response = client.post(
        "/api/analyze",
        json={"subject": "", "body": "", "mode": "combined"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["classification"] == "no_configured_patterns_matched"
    assert payload["dfa_result"]["accepted"] is False
    assert payload["nfa_result"]["accepted"] is False
    assert payload["regex_result"]["matched"] is False


def test_combined_url_match_is_an_indicator_not_a_definitive_verdict() -> None:
    response = client.post(
        "/api/analyze",
        json={
            "subject": "Project documentation",
            "body": "Read https://example.com/docs",
            "mode": "combined",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["dfa_result"]["accepted"] is False
    assert payload["nfa_result"]["accepted"] is False
    assert payload["regex_result"]["matched"] is True
    assert payload["risk_score"] == 20
    assert "not proof of phishing" in payload["regex_result"]["explanation"]


def test_simulation_uses_input_text_contract_without_fabricating_trace() -> None:
    response = client.post(
        "/api/automata/dfa_win_prize_now/simulate",
        json={"input_text": "WIN PRIZE NOW"},
    )
    old_contract = client.post(
        "/api/automata/dfa_win_prize_now/simulate",
        json={"input": "WIN PRIZE NOW"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["final_states"] == ["q3"]
    assert [step["states_after"][0] for step in payload["trace"]] == [
        "q0",
        "q1",
        "q2",
        "q3",
    ]
    assert old_contract.status_code == 422


def test_dfa_analysis_returns_computed_result() -> None:
    accepted = client.post(
        "/api/analyze",
        json={"subject": "", "body": "win PRIZE now", "mode": "dfa"},
    )
    rejected = client.post(
        "/api/analyze",
        json={"subject": "", "body": "WIN PRIZE", "mode": "dfa"},
    )

    assert accepted.status_code == 200
    accepted_payload = accepted.json()
    assert accepted_payload["classification"] == "suspicious"
    assert accepted_payload["risk_score"] == 100
    assert accepted_payload["nfa_result"] is None
    assert accepted_payload["regex_result"] is None
    assert accepted_payload["dfa_result"]["accepted"] is True
    assert accepted_payload["dfa_result"]["matched_patterns"][0]["pattern_id"] == (
        "dfa_win_prize_now"
    )

    assert rejected.status_code == 200
    rejected_payload = rejected.json()
    assert rejected_payload["classification"] == "no_configured_patterns_matched"
    assert rejected_payload["risk_score"] == 0
    assert rejected_payload["dfa_result"]["accepted"] is False
    assert "does not guarantee safety" in rejected_payload["dfa_result"]["explanation"]


def test_dfa_api_rejects_invalid_requests() -> None:
    missing_body = client.post(
        "/api/analyze",
        json={"subject": "WIN PRIZE NOW", "mode": "dfa"},
    )
    oversized = client.post(
        "/api/analyze",
        json={"subject": "x", "body": "y" * 10_000, "mode": "dfa"},
    )

    assert missing_body.status_code == 422
    assert oversized.status_code == 422


def test_nfa_simulation_returns_computed_active_states_and_trace() -> None:
    response = client.post(
        "/api/automata/nfa_phishing_branches/simulate",
        json={"input_text": "account VERIFY immediately"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["final_states"] == ["a3"]
    assert payload["active_states"] == ["a3"]
    assert payload["trace"][0]["states_after"] == ["a0", "c0", "s0", "w0"]
    assert payload["trace"][1]["transitions_taken"] == ["a0 --ACCOUNT--> a1"]


def test_nfa_analysis_returns_only_real_nfa_result() -> None:
    accepted = client.post(
        "/api/analyze",
        json={"subject": "", "body": "CLAIM REWARD NOW", "mode": "nfa"},
    )
    rejected = client.post(
        "/api/analyze",
        json={"subject": "", "body": "CLAIM REWARD", "mode": "nfa"},
    )

    assert accepted.status_code == 200
    accepted_payload = accepted.json()
    assert accepted_payload["classification"] == "suspicious"
    assert accepted_payload["dfa_result"] is None
    assert accepted_payload["regex_result"] is None
    assert accepted_payload["nfa_result"]["accepted"] is True
    assert accepted_payload["nfa_result"]["matched_patterns"][0]["pattern_id"] == (
        "nfa_claim_reward_now"
    )
    assert "not, by itself, proof" in accepted_payload["nfa_result"]["explanation"]

    assert rejected.status_code == 200
    rejected_payload = rejected.json()
    assert rejected_payload["classification"] == "no_configured_patterns_matched"
    assert rejected_payload["nfa_result"]["accepted"] is False
    assert "does not guarantee" in rejected_payload["nfa_result"]["explanation"]


def test_regex_analysis_returns_computed_subject_and_body_matches() -> None:
    response = client.post(
        "/api/analyze",
        json={
            "subject": "WIN PRIZE NOW!!!",
            "body": "Visit https://example.com/login or email help@example.com",
            "mode": "regex",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["classification"] == "suspicious"
    assert payload["dfa_result"] is None
    assert payload["nfa_result"] is None
    regex_result = payload["regex_result"]
    assert regex_result["matched"] is True
    patterns = {item["pattern_id"]: item for item in regex_result["matched_patterns"]}
    assert set(patterns) == {
        "RULE-URL",
        "RULE-EMAIL",
        "RULE-PHRASE-WIN",
        "RULE-EXCLAMATION",
    }
    assert patterns["RULE-PHRASE-WIN"]["evidence"][0] == {
        "source": "subject",
        "text": "WIN PRIZE NOW",
        "start_index": 0,
        "end_index": 13,
    }
    assert patterns["RULE-URL"]["evidence"][0]["source"] == "body"
    assert "not proof of phishing" in regex_result["explanation"]


def test_regex_analysis_with_no_matches_preserves_safety_warning() -> None:
    response = client.post(
        "/api/analyze",
        json={
            "subject": "Weekly meeting",
            "body": "Please review the agenda tomorrow.",
            "mode": "regex",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["classification"] == "no_configured_patterns_matched"
    assert payload["risk_score"] == 0
    assert payload["regex_result"]["matched_patterns"] == []
    assert "does not guarantee" in payload["regex_result"]["explanation"]


def test_analysis_request_rejects_user_supplied_regex_rules() -> None:
    response = client.post(
        "/api/analyze",
        json={
            "subject": "",
            "body": "ordinary text",
            "mode": "regex",
            "patterns": [".*"],
        },
    )

    assert response.status_code == 422


def test_cors_allows_only_local_vite_origin() -> None:
    allowed = client.options(
        "/api/analyze",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    disallowed = client.options(
        "/api/analyze",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-origin" not in disallowed.headers


def test_openapi_documents_all_contract_endpoints() -> None:
    document = client.get("/openapi.json").json()
    paths = document["paths"]

    assert paths["/api/health"]["get"]["responses"]["200"]
    assert paths["/api/automata"]["get"]["responses"]["200"]
    assert paths["/api/automata/{automaton_id}"]["get"]["responses"]["200"]
    assert "501" not in paths["/api/analyze"]["post"]["responses"]
    assert paths["/api/automata/{automaton_id}/simulate"]["post"]["responses"]["501"]
