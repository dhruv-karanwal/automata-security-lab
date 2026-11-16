"""Unit tests for API data-model validation."""

import pytest
from pydantic import ValidationError

from app.schemas import (
    MAX_EMAIL_LENGTH,
    AnalysisMode,
    AnalyzeEmailRequest,
    AnalyzeEmailResponse,
    AutomatonDescription,
    AutomatonTransition,
    Classification,
    DFAAnalysisResult,
)


def test_analyze_request_uses_expected_defaults() -> None:
    request = AnalyzeEmailRequest(body="Please review this email.")

    assert request.subject == ""
    assert request.mode == AnalysisMode.COMBINED


def test_analyze_request_rejects_invalid_mode() -> None:
    with pytest.raises(ValidationError):
        AnalyzeEmailRequest(body="Example", mode="unknown")


def test_analyze_request_rejects_oversized_combined_input() -> None:
    with pytest.raises(ValidationError, match="must not exceed 10000 characters"):
        AnalyzeEmailRequest(subject="S", body="B" * MAX_EMAIL_LENGTH)


def test_analyze_response_rejects_invalid_risk_score() -> None:
    with pytest.raises(ValidationError):
        AnalyzeEmailResponse(
            classification=Classification.SUSPICIOUS,
            risk_score=101,
            mode=AnalysisMode.DFA,
            dfa_result=DFAAnalysisResult(
                matched=False,
                accepted=False,
                explanation="No match.",
            ),
        )


def test_single_engine_response_requires_selected_result() -> None:
    with pytest.raises(ValidationError, match="dfa mode requires its matching result"):
        AnalyzeEmailResponse(
            classification=Classification.NO_CONFIGURED_PATTERNS_MATCHED,
            risk_score=0,
            mode=AnalysisMode.DFA,
        )


def test_valid_dfa_description() -> None:
    automaton = AutomatonDescription(
        automaton_id="example_dfa",
        name="Example DFA",
        description="A small DFA used by this schema test.",
        automaton_type="dfa",
        states=["q0", "q1"],
        alphabet=["a"],
        start_state="q0",
        accepting_states=["q1"],
        transitions=[
            AutomatonTransition(
                from_state="q0",
                symbol="a",
                to_states=["q1"],
            )
        ],
    )

    assert automaton.start_state == "q0"
    assert automaton.transitions[0].to_states == ["q1"]


def test_dfa_rejects_multiple_destination_states() -> None:
    with pytest.raises(ValidationError, match="one destination state"):
        AutomatonDescription(
            automaton_id="invalid_dfa",
            name="Invalid DFA",
            description="An invalid DFA used by this schema test.",
            automaton_type="dfa",
            states=["q0", "q1"],
            alphabet=["a"],
            start_state="q0",
            accepting_states=["q1"],
            transitions=[
                AutomatonTransition(
                    from_state="q0",
                    symbol="a",
                    to_states=["q0", "q1"],
                )
            ],
        )


def test_analysis_response_serializes_with_snake_case_contract() -> None:
    response = AnalyzeEmailResponse(
        classification=Classification.NO_CONFIGURED_PATTERNS_MATCHED,
        risk_score=0,
        mode=AnalysisMode.DFA,
        dfa_result=DFAAnalysisResult(
            matched=False,
            accepted=False,
            final_states=["q_dead"],
            active_states=["q_dead"],
            explanation="The configured sequence was not accepted.",
        ),
    )

    payload = response.model_dump(mode="json")

    assert payload["classification"] == "no_configured_patterns_matched"
    assert payload["dfa_result"]["final_states"] == ["q_dead"]
    assert "finalState" not in payload["dfa_result"]
